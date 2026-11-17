use inotify::{EventMask, Inotify, WatchMask};
use serde_json::Value as JsonValue;
use std::collections::HashMap;
use std::env;
use std::fs;
use std::path::PathBuf;
use std::process::Command;
use std::sync::mpsc::{self, Sender};
use std::thread;
use std::time::{Duration, Instant};
use zbus::blocking::{Connection, MessageIterator};
use zbus::zvariant::{OwnedObjectPath, Value};

struct GuardState {
    last_repair: Option<Instant>,
    consecutive_failures: u32,
    pending_recovery_notice: bool,
    notified_locker_pid: Option<u32>,
}

impl GuardState {
    fn new() -> Self {
        Self {
            last_repair: None,
            consecutive_failures: 0,
            pending_recovery_notice: false,
            notified_locker_pid: None,
        }
    }
}

fn state_dir() -> PathBuf {
    env::var("XDG_STATE_HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|_| {
            let home = env::var("HOME").unwrap_or_else(|_| "/tmp".into());
            PathBuf::from(home).join(".local/state")
        })
        .join("wireplumber")
}

fn is_german() -> bool {
    for key in ["LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"] {
        if let Ok(val) = env::var(key) {
            let first = val.split(':').next().unwrap_or("").trim();
            if !first.is_empty() {
                return first.to_lowercase().starts_with("de");
            }
        }
    }

    let plasma_locale = env::var("XDG_CONFIG_HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|_| {
            let home = env::var("HOME").unwrap_or_else(|_| "/tmp".into());
            PathBuf::from(home).join(".config")
        })
        .join("plasma-localerc");

    if let Ok(content) = fs::read_to_string(plasma_locale) {
        for prefix in ["LANGUAGE=", "LANG="] {
            for line in content.lines() {
                if let Some(val) = line.trim().strip_prefix(prefix) {
                    let first = val.split(':').next().unwrap_or("").trim();
                    if !first.is_empty() {
                        return first.to_lowercase().starts_with("de");
                    }
                }
            }
        }
    }

    false
}

fn notifications_enabled() -> bool {
    let user_cfg = env::var("XDG_CONFIG_HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|_| {
            let home = env::var("HOME").unwrap_or_else(|_| "/tmp".into());
            PathBuf::from(home).join(".config")
        })
        .join("kader42/audio-guard.conf");

    for path in [user_cfg, PathBuf::from("/etc/kader42/audio-guard.conf")] {
        if let Ok(content) = fs::read_to_string(path) {
            for line in content.lines() {
                let line = line.trim();
                if let Some(val) = line.strip_prefix("notifications=") {
                    return !matches!(val.trim().to_lowercase().as_str(), "false" | "0" | "no");
                }
            }
        }
    }
    true
}

fn notify_user(
    dbus: &Connection,
    event_id: &str,
    de: (&str, &str),
    en: (&str, &str),
    icon: &str,
) {
    if !notifications_enabled() {
        return;
    }

    let (summary, body) = if is_german() { de } else { en };
    let actions: Vec<&str> = Vec::new();
    let mut hints: HashMap<&str, Value> = HashMap::new();
    hints.insert("desktop-entry", Value::from("kader42-audio-guard"));
    hints.insert("x-kde-event", Value::from(event_id));

    let _ = dbus.call_method(
        Some("org.freedesktop.Notifications"),
        "/org/freedesktop/Notifications",
        Some("org.freedesktop.Notifications"),
        "Notify",
        &(
            "Kader42 Audio Guard",
            0u32,
            icon,
            summary,
            body,
            actions,
            hints,
            5000i32,
        ),
    );
}

fn has_alsa_hardware() -> bool {
    fs::read_to_string("/proc/asound/cards")
        .map(|c| c.lines().any(|l| l.contains('[')))
        .unwrap_or(false)
}

fn get_pipewire_sinks() -> Option<Vec<String>> {
    let output = Command::new("pw-dump").arg("Node").output().ok()?;
    if !output.status.success() {
        return None;
    }

    let nodes: JsonValue = serde_json::from_slice(&output.stdout).ok()?;
    let arr = nodes.as_array()?;

    let mut sinks = Vec::new();
    for node in arr {
        let Some(props) = node.get("info").and_then(|i| i.get("props")) else {
            continue;
        };
        if props.get("media.class").and_then(|v| v.as_str()) == Some("Audio/Sink") {
            let name = props
                .get("node.name")
                .and_then(|v| v.as_str())
                .unwrap_or("unknown")
                .to_string();
            sinks.push(name);
        }
    }
    Some(sinks)
}

/// Returns true if ALSA hardware is present in the kernel, but PipeWire has no active hardware sink
fn is_audio_broken() -> bool {
    if !has_alsa_hardware() {
        return false;
    }

    let Some(sinks) = get_pipewire_sinks() else {
        return false;
    };

    !sinks
        .iter()
        .any(|name| name.starts_with("alsa_output.") && name != "auto_null")
}

/// Scans /proc for processes holding an exclusive file descriptor on /dev/snd/pcmC*
fn find_pcm_locker() -> Option<(u32, String, String)> {
    let proc_entries = fs::read_dir("/proc").ok()?;
    for entry in proc_entries.flatten() {
        let pid: u32 = match entry.file_name().to_string_lossy().parse() {
            Ok(p) => p,
            Err(_) => continue,
        };

        let fds = match fs::read_dir(entry.path().join("fd")) {
            Ok(f) => f,
            Err(_) => continue,
        };

        for fd in fds.flatten() {
            if let Ok(target) = fs::read_link(fd.path()) {
                let target_str = target.to_string_lossy();
                if target_str.starts_with("/dev/snd/pcmC") {
                    let comm = fs::read_to_string(entry.path().join("comm"))
                        .unwrap_or_else(|_| "unknown".into())
                        .trim()
                        .to_string();

                    if comm != "pipewire" && comm != "wireplumber" {
                        return Some((pid, comm, target_str.into_owned()));
                    }
                }
            }
        }
    }
    None
}

fn restart_user_unit(dbus: &Connection, unit: &str) -> zbus::Result<()> {
    let reply = dbus.call_method(
        Some("org.freedesktop.systemd1"),
        "/org/freedesktop/systemd1",
        Some("org.freedesktop.systemd1.Manager"),
        "RestartUnit",
        &(unit, "replace"),
    )?;
    let _job: OwnedObjectPath = reply.body().deserialize()?;
    Ok(())
}

fn reset_wireplumber_state() {
    let dir = state_dir();
    let _ = fs::remove_file(dir.join("default-profile"));
    let _ = fs::remove_file(dir.join("restore-stream"));
}

fn perform_repair(dbus: &Connection, reset_profiles: bool) {
    if reset_profiles {
        eprintln!("[kader42-audio-guard] Resetting saved WirePlumber profiles...");
        reset_wireplumber_state();
    }

    eprintln!("[kader42-audio-guard] No active ALSA sink – restarting audio stack via D-Bus...");
    for unit in [
        "pipewire.service",
        "pipewire-pulse.service",
        "wireplumber.service",
    ] {
        if let Err(e) = restart_user_unit(dbus, unit) {
            eprintln!(
                "[kader42-audio-guard] D-Bus RestartUnit ({}) error: {}",
                unit, e
            );
        }
    }
}

/// Watches /dev/snd via inotify for created, removed, or closed audio device nodes
fn spawn_snd_watcher(tx: Sender<()>) {
    thread::spawn(move || {
        let mut inotify = match Inotify::init() {
            Ok(i) => i,
            Err(e) => {
                eprintln!("[kader42-audio-guard] inotify initialization failed: {}", e);
                return;
            }
        };

        if let Err(e) = inotify.watches().add(
            "/dev/snd",
            WatchMask::CREATE
                | WatchMask::DELETE
                | WatchMask::CLOSE_WRITE
                | WatchMask::CLOSE_NOWRITE,
        ) {
            eprintln!(
                "[kader42-audio-guard] Failed to add watch on /dev/snd: {}",
                e
            );
            return;
        }

        let mut buffer = [0; 2048];
        loop {
            let events = match inotify.read_events_blocking(&mut buffer) {
                Ok(ev) => ev,
                Err(_) => {
                    thread::sleep(Duration::from_secs(1));
                    continue;
                }
            };

            let relevant = events.into_iter().any(|ev| {
                let is_audio = ev
                    .name
                    .map(|n| {
                        let s = n.to_string_lossy();
                        s.starts_with("pcmC") || s.starts_with("controlC")
                    })
                    .unwrap_or(false);
                let is_mask = ev.mask.intersects(
                    EventMask::CREATE
                        | EventMask::DELETE
                        | EventMask::CLOSE_WRITE
                        | EventMask::CLOSE_NOWRITE,
                );
                is_audio && is_mask
            });

            if relevant && tx.send(()).is_err() {
                break;
            }
        }
    });
}

/// Listens via zbus for systemd user session events (e.g. PipeWire or WirePlumber restarts)
fn spawn_systemd_watcher(tx: Sender<()>) {
    thread::spawn(move || {
        let Ok(conn) = Connection::session() else {
            return;
        };

        let rule = "type='signal',sender='org.freedesktop.systemd1',interface='org.freedesktop.DBus.Properties',member='PropertiesChanged'";
        if conn
            .call_method(
                Some("org.freedesktop.DBus"),
                "/org/freedesktop/DBus",
                Some("org.freedesktop.DBus"),
                "AddMatch",
                &(rule,),
            )
            .is_err()
        {
            return;
        }

        for msg in MessageIterator::from(&conn) {
            if msg.is_ok() && tx.send(()).is_err() {
                break;
            }
        }
    });
}

fn evaluate_and_heal(dbus: &Connection, state: &mut GuardState) {
    if !is_audio_broken() {
        if state.pending_recovery_notice {
            notify_user(
                dbus,
                "audio-recovered",
                (
                    "Audio wiederhergestellt",
                    "Die Audio-Ausgabe wurde erfolgreich neu initialisiert.",
                ),
                (
                    "Audio recovered",
                    "Audio output has been successfully reinitialized.",
                ),
                "audio-card",
            );
            state.pending_recovery_notice = false;
        }
        if state.consecutive_failures > 0 || state.notified_locker_pid.is_some() {
            eprintln!("[kader42-audio-guard] Audio state healthy again.");
            state.consecutive_failures = 0;
            state.notified_locker_pid = None;
        }
        return;
    }

    if let Some((pid, comm, dev)) = find_pcm_locker() {
        eprintln!(
            "[kader42-audio-guard] {} is still locked by PID {} ({}) – waiting for release.",
            dev, pid, comm
        );
        if state.notified_locker_pid != Some(pid) {
            notify_user(
                dbus,
                "audio-blocked",
                (
                    "Audiogerät blockiert",
                    &format!(
                        "Das Programm '{}' (PID {}) belegt {} exklusiv.",
                        comm, pid, dev
                    ),
                ),
                (
                    "Audio device blocked",
                    &format!(
                        "Application '{}' (PID {}) holds an exclusive lock on {}.",
                        comm, pid, dev
                    ),
                ),
                "dialog-warning",
            );
            state.notified_locker_pid = Some(pid);
        }
        return;
    }

    let cooldown = if state.consecutive_failures >= 3 {
        Duration::from_secs(60)
    } else {
        Duration::from_secs(10)
    };

    if let Some(last) = state.last_repair {
        if last.elapsed() < cooldown {
            return;
        }
    }

    state.last_repair = Some(Instant::now());
    state.consecutive_failures += 1;
    state.pending_recovery_notice = true;
    let reset_profiles = state.consecutive_failures >= 2;
    perform_repair(dbus, reset_profiles);
}

fn run_daemon() -> ! {
    let dbus = Connection::session().expect("Failed to connect to D-Bus session bus");
    let mut state = GuardState::new();

    let (tx, rx) = mpsc::channel::<()>();
    spawn_snd_watcher(tx.clone());
    spawn_systemd_watcher(tx);

    eprintln!("[kader42-audio-guard] Event monitoring (inotify + zbus) active.");

    // Initial check after session startup
    thread::sleep(Duration::from_millis(900));
    evaluate_and_heal(&dbus, &mut state);

    loop {
        if rx.recv().is_err() {
            thread::sleep(Duration::from_secs(1));
            continue;
        }

        // Debounce: wait 900 ms for related kernel/D-Bus events to settle
        while rx.recv_timeout(Duration::from_millis(900)).is_ok() {}
        evaluate_and_heal(&dbus, &mut state);
    }
}

fn run_manual_repair(force_unlock: bool) -> bool {
    let dbus = match Connection::session() {
        Ok(c) => c,
        Err(e) => {
            eprintln!("[kader42-audio-guard] D-Bus error: {}", e);
            return false;
        }
    };

    if let Some((pid, comm, dev)) = find_pcm_locker() {
        if force_unlock {
            eprintln!(
                "[kader42-audio-guard] Terminating blocking process PID {} ({}) on {}...",
                pid, comm, dev
            );
            let _ = Command::new("kill")
                .args(["-9", &pid.to_string()])
                .status();
            thread::sleep(Duration::from_millis(500));
        } else {
            eprintln!(
                "[kader42-audio-guard] {} is locked by PID {} ({}). Use --force-unlock to terminate it.",
                dev, pid, comm
            );
            return false;
        }
    }

    perform_repair(&dbus, true);
    thread::sleep(Duration::from_secs(2));

    let ok = !is_audio_broken();
    if ok {
        eprintln!("[kader42-audio-guard] Audio recovery successful.");
        notify_user(
            &dbus,
            "audio-recovered",
            (
                "Audio wiederhergestellt",
                "Die Audio-Ausgabe wurde erfolgreich neu initialisiert.",
            ),
            (
                "Audio recovered",
                "Audio output has been successfully reinitialized.",
            ),
            "audio-card",
        );
    } else {
        eprintln!("[kader42-audio-guard] Audio recovery failed.");
    }
    ok
}

fn main() {
    let mut args = env::args().skip(1);
    match args.next().as_deref() {
        Some("--daemon") => run_daemon(),
        Some("--repair") => {
            let force = args.next().as_deref() == Some("--force-unlock");
            if !run_manual_repair(force) {
                std::process::exit(1);
            }
        }
        Some("--test-notify") => {
            if let Ok(dbus) = Connection::session() {
                notify_user(
                    &dbus,
                    "audio-recovered",
                    (
                        "Kader42 Audio Guard",
                        "Desktop-Benachrichtigungen sind aktiv.",
                    ),
                    (
                        "Kader42 Audio Guard",
                        "Desktop notifications are active.",
                    ),
                    "audio-card",
                );
            }
        }
        _ => {
            eprintln!(
                "Usage: kader42-audio-guard [--daemon | --repair [--force-unlock] | --test-notify]"
            );
            std::process::exit(1);
        }
    }
}