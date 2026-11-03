use evdev::{AttributeSet, Device, InputEventKind, SwitchType};
use std::fs;
use std::path::PathBuf;
use std::process::Command;

fn main() {
    println!("[kader42-tablet-event-listener] 🚀 Service started...");

    let mut chassis_type = get_chassis_type();
    if matches!(chassis_type.as_str(), "8" | "9" | "10") {
        if is_convertible_hardware() {
            chassis_type = "31".to_string();
        }
    }
    println!("[kader42-tablet-event-listener] ⚙ Detected Chassis Type: {}", chassis_type);

    if chassis_type != "31" {
        println!("[kader42-tablet-event-listener] 💻 Chassis '{}' not a convertible. Exiting.", chassis_type);
        return;
    }

    let (dev_path, mut tablet_device) = match find_tablet_switch_device() {
        Some(res) => res,
        None => {
            eprintln!("[kader42-tablet-event-listener] ⚠️ No SW_TABLET_MODE switch found in /dev/input/! Exiting.");
            return;
        }
    };

    println!(
        "[kader42-tablet-event-listener] ⚡ Bound to hardware switch: {} ({:?})",
        tablet_device.name().unwrap_or("Unknown Device"),
        dev_path
    );

    let initial_state = get_switch_state(&tablet_device);
    let mut last_mode: u8 = if initial_state { 1 } else { 0 };
    
    println!("[kader42-tablet-event-listener] ✅ Initial Kernel Switch State: {}", last_mode);
    trigger_switcher(last_mode, true);

    loop {
        match tablet_device.fetch_events() {
            Ok(events) => {
                for event in events {
                    if let InputEventKind::Switch(SwitchType::SW_TABLET_MODE) = event.kind() {
                        let new_mode: u8 = if event.value() == 1 { 1 } else { 0 };

                        if new_mode != last_mode {
                            println!("[kader42-tablet-event-listener] ⚙️ Hardware Switch Toggled: {} -> {}", last_mode, new_mode);
                            trigger_switcher(new_mode, false);
                            last_mode = new_mode;
                        }
                    }
                }
            }
            Err(e) => {
                eprintln!("[kader42-tablet-event-listener] ⚠️ Read error on {:?}: {}", dev_path, e);
                std::thread::sleep(std::time::Duration::from_millis(1000));
            }
        }
    }
}

/// Robustes Durchsuchen von /dev/input/ ohne Absturz bei fehlenden/virtuellen Nodes
fn find_tablet_switch_device() -> Option<(PathBuf, Device)> {
    let entries = fs::read_dir("/dev/input").ok()?;

    for entry in entries.flatten() {
        let path = entry.path();
        if path.to_string_lossy().contains("event") {
            if let Ok(device) = Device::open(&path) {
                if let Some(switches) = device.supported_switches() {
                    if switches.contains(SwitchType::SW_TABLET_MODE) {
                        return Some((path, device));
                    }
                }
            }
        }
    }
    None
}

fn get_switch_state(device: &Device) -> bool {
    if let Ok(sw_state) = device.get_switch_state() {
        return sw_state.contains(SwitchType::SW_TABLET_MODE);
    }
    false
}

fn get_chassis_type() -> String {
    fs::read_to_string("/sys/class/dmi/id/chassis_type")
        .unwrap_or_default()
        .trim()
        .to_string()
}

fn is_convertible_hardware() -> bool {
    if let Ok(devices) = fs::read_to_string("/proc/bus/input/devices") {
        let dev_lower = devices.to_lowercase();
        if dev_lower.contains("intel virtual buttons")
            || dev_lower.contains("gpio-keys")
            || dev_lower.contains("tablet mode switch")
            || dev_lower.contains("intel hid switches")
        {
            return true;
        }
    }
    false
}

fn trigger_switcher(mode: u8, force: bool) {
    let mut cmd = Command::new("/usr/bin/kader42-plasma-convertible-switcher");
    cmd.arg(mode.to_string());
    if force {
        cmd.arg("--force");
    }

    match cmd.spawn() {
        Ok(_) => println!("[kader42-tablet-event-listener] 🚀 Switcher triggered (mode: {})", mode),
        Err(e) => eprintln!("[kader42-tablet-event-listener] ❌ Failed to execute switcher: {}", e),
    }
}