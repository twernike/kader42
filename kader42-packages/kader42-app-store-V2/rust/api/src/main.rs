use alpm::{Alpm, SigLevel};
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use listenfd::ListenFd;
use rusqlite::Connection;
use serde::{Deserialize, Serialize};
use std::{
    collections::{HashMap, HashSet},
    fs,
    net::SocketAddr,
    path::Path as StdPath,
    process::Command,
    sync::{Arc, Mutex},
};
use tower_http::cors::CorsLayer;

const DB_PATH: &str = "/var/lib/kader42/software-center.db";
const SETTINGS_FILE: &str = "/etc/kader42/software-center.json";

// --- STRUCTS & MODELS ---

#[derive(Serialize, Deserialize, Clone)]
struct CategoryDef {
    id: String,
    icon: String,
    de: String,
    en: String,
    query: String,
}

#[derive(Serialize, Deserialize, Clone)]
struct AppItem {
    package_name: String,
    name: String,
    source: String, // "repo" oder "aur"
    status: String, // "installed", "update_available", "available"
    description: String,
    icon_path: Option<String>,
}

#[derive(Serialize, Deserialize)]
struct Settings {
    auto_updates: bool,
    update_time: String,
    retention_completed_days: i32,
    retention_failed_days: i32,
}

#[derive(Serialize, Deserialize)]
struct Job {
    id: i64,
    package_name: String,
    action: String,
    status: String,
    progress: i32,
    log_output: Option<String>,
    created_at: Option<String>,
}

#[derive(Deserialize)]
struct CreateJobRequest {
    package_name: String,
    source: Option<String>,
    action: String,
}

#[derive(Deserialize)]
struct AurRpcResponse {
    results: Vec<AurRpcPackage>,
}

#[derive(Deserialize)]
struct AurRpcPackage {
    Name: String,
    Description: Option<String>,
}

// Globaler Anwendungs-Status für Axum State
struct AppState {
    db_conn: Mutex<Connection>,
    categories: Vec<CategoryDef>,
}

// --- MAIN FUNCTION ---

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("[kader42-api] Initialisiere libalpm und SQLite-Datenbank...");

    // 1. SQLite Datenbankverbindung initialisieren
    let conn = Connection::open(DB_PATH).unwrap_or_else(|_| Connection::open_in_memory().unwrap());

    // 2. Kategorien laden
    let categories = vec![
        CategoryDef { id: "development".into(), icon: "applications-development".into(), de: "Entwicklungstools".into(), en: "Development".into(), query: "code visual-studio-code-bin vscodium-bin eclipse pycharm gitkraken".into() },
        CategoryDef { id: "internet".into(), icon: "applications-internet".into(), de: "Internet & Browser".into(), en: "Internet".into(), query: "firefox chromium thunderbird filezilla discord".into() },
        CategoryDef { id: "multimedia".into(), icon: "applications-multimedia".into(), de: "Multimedia".into(), en: "Multimedia".into(), query: "vlc gimp inkscape blender audacity handbrake".into() },
        CategoryDef { id: "office".into(), icon: "applications-office".into(), de: "Büro & Office".into(), en: "Office".into(), query: "libreoffice-fresh openboard xournalpp".into() },
    ];

    let shared_state = Arc::new(AppState {
        db_conn: Mutex::new(conn),
        categories,
    });

    // 3. Axum Router aufbauen
// 3. Axum Router aufbauen (Axum 0.8 Syntax mit {id})
    let app = Router::new()
        .route("/self-update-check", get(self_update_check))
        .route("/categories", get(get_categories))
        .route("/apps", get(search_apps))
        .route("/installed", get(get_installed))
        .route("/updates", get(get_updates))
        .route("/settings", get(get_settings).post(save_settings_handler))
        .route("/jobs", get(get_jobs))
        .route("/job", post(create_job))
        .route("/job/{id}", get(get_job_status).delete(delete_job))
        .route("/job/{id}/log", get(get_job_log))
        .layer(CorsLayer::permissive())
        .with_state(shared_state);

    // 4. Systemd Socket Activation vs. Standalone Server
    let mut listenfd = ListenFd::from_env();
    let listener = if let Some(l) = listenfd.take_tcp_listener(0)? {
        println!("[kader42-api] Systemd Socket Activation erkannt.");
        tokio::net::TcpListener::from_std(l)?
    } else {
        let addr = SocketAddr::from(([127, 0, 0, 1], 8080));
        println!("[kader42-api] Gestartet auf http://{}", addr);
        tokio::net::TcpListener::bind(addr).await?
    };

    axum::serve(listener, app).await?;
    Ok(())
}

// --- LIBALPM HELPERS ---

fn init_alpm() -> Result<Alpm, alpm::Error> {
    let handle = Alpm::new("/", "/var/lib/pacman")?;
    let _ = handle.register_syncdb("core", SigLevel::NONE);
    let _ = handle.register_syncdb("extra", SigLevel::NONE);
    let _ = handle.register_syncdb("multilib", SigLevel::NONE);
    Ok(handle)
}

fn get_installed_pkg_names(alpm: &Alpm) -> HashSet<String> {
    let local_db = alpm.localdb();
    local_db.pkgs().iter().map(|p| p.name().to_string()).collect()
}

// --- API HANDLERS ---

async fn self_update_check() -> Json<serde_json::Value> {
    let output = Command::new("yay")
        .args(["-Qu", "kader42-software-center"])
        .output();

    let has_update = match output {
        Ok(out) => !String::from_utf8_lossy(&out.stdout).trim().is_empty(),
        Err(_) => false,
    };

    Json(serde_json::json!({
        "update_available": has_update,
        "package_name": "kader42-software-center"
    }))
}

async fn get_categories(State(state): State<Arc<AppState>>) -> Json<Vec<CategoryDef>> {
    Json(state.categories.clone())
}

// Reichenfolge in Axum 0.8: Query MUSS vor State stehen!
#[derive(Deserialize)]
struct SearchParams {
    category: Option<String>,
    search: Option<String>,
}

async fn search_apps(
    Query(params): Query<SearchParams>,
    State(state): State<Arc<AppState>>,
) -> Json<Vec<AppItem>> {
    let mut search_term = String::new();

    if let Some(cat_id) = &params.category {
        if let Some(cat) = state.categories.iter().find(|c| &c.id == cat_id) {
            search_term = cat.query.clone();
        }
    } else if let Some(q) = &params.search {
        search_term = q.trim().to_lowercase();
    }

    if search_term.is_empty() {
        return Json(vec![]);
    }

    let mut results = Vec::new();
    let mut installed_pkgs = HashSet::new();

    // SCHRITT 1: Synchrone libalpm-Abfrage in eigenem Scope (wird vor dem .await wieder verworfen!)
    {
        if let Ok(alpm) = init_alpm() {
            installed_pkgs = get_installed_pkg_names(&alpm);

            for db in alpm.syncdbs() {
                for pkg in db.pkgs() {
                    let name = pkg.name();
                    if name.contains(&search_term) || search_term.contains(name) {
                        let status = if installed_pkgs.contains(name) {
                            "installed"
                        } else {
                            "available"
                        };
                        results.push(AppItem {
                            package_name: name.to_string(),
                            name: capitalize(name),
                            source: "repo".to_string(),
                            status: status.to_string(),
                            description: pkg.desc().unwrap_or("").to_string(),
                            icon_path: None,
                        });
                    }
                }
            }
        }
    } // <-- `alpm` wird hier sicher gedroppt!

    // SCHRITT 2: Asynchrone AUR-Abfrage via HTTPS (jetzt gefahrlos mit .await möglich)
    if results.len() < 5 {
        let client = reqwest::Client::new();
        let url = format!("https://aur.archlinux.org/rpc/v5/search/{}", search_term);
        if let Ok(res) = client.get(&url).send().await {
            if let Ok(aur_data) = res.json::<AurRpcResponse>().await {
                for aur_pkg in aur_data.results {
                    let status = if installed_pkgs.contains(&aur_pkg.Name) {
                        "installed"
                    } else {
                        "available"
                    };
                    results.push(AppItem {
                        package_name: aur_pkg.Name.clone(),
                        name: capitalize(&aur_pkg.Name),
                        source: "aur".to_string(),
                        status: status.to_string(),
                        description: aur_pkg.Description.unwrap_or_default(),
                        icon_path: None,
                    });
                }
            }
        }
    }

    results.truncate(100);
    Json(results)
}

async fn get_installed() -> Json<Vec<AppItem>> {
    let alpm = match init_alpm() {
        Ok(a) => a,
        Err(_) => return Json(vec![]),
    };

    let mut installed_apps = Vec::new();

    for pkg in alpm.localdb().pkgs() {
        let pkg_name = pkg.name();

        let desktop_file = format!("/usr/share/applications/{}.desktop", pkg_name);
        let is_gui = StdPath::new(&desktop_file).exists()
            || ["code", "vscodium-bin", "discord", "steam", "spotify"].contains(&pkg_name);

        if is_gui {
            installed_apps.push(AppItem {
                package_name: pkg_name.to_string(),
                name: capitalize(pkg_name),
                source: "repo".to_string(),
                status: "installed".to_string(),
                description: "desc_installed_repo".to_string(),
                icon_path: Some("/usr/share/pixmaps/nobody.png".to_string()),
            });
        }
    }

    Json(installed_apps)
}

async fn get_updates() -> Json<serde_json::Value> {
    let mut update_packages = Vec::new();
    if let Ok(output) = Command::new("yay").arg("-Qu").output() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        for line in stdout.lines() {
            if let Some(pkg_name) = line.split_whitespace().next() {
                update_packages.push(AppItem {
                    package_name: pkg_name.to_string(),
                    name: capitalize(pkg_name),
                    source: "repo".to_string(),
                    status: "update_available".to_string(),
                    description: "desc_update_available".to_string(),
                    icon_path: None,
                });
            }
        }
    }

    Json(serde_json::json!({
        "total_updates": update_packages.len(),
        "packages": update_packages
    }))
}

// --- SETTINGS HANDLERS ---

async fn get_settings() -> Json<Settings> {
    let is_enabled = Command::new("systemctl")
        .args(["is-enabled", "kader42-autoupdate.timer"])
        .output()
        .map(|out| String::from_utf8_lossy(&out.stdout).trim() == "enabled")
        .unwrap_or(false);

    let mut settings = Settings {
        auto_updates: is_enabled,
        update_time: "04:00".into(),
        retention_completed_days: 1,
        retention_failed_days: 3,
    };

    if let Ok(content) = fs::read_to_string(SETTINGS_FILE) {
        // Explizite Typangabe auf der rechten Seite für serde_json:
        if let Ok(json) = serde_json::from_str::<serde_json::Value>(&content) {
            if let Some(t) = json.get("update_time").and_then(|v| v.as_str()) {
                settings.update_time = t.to_string();
            }
        }
    }

    Json(settings)
}

async fn save_settings_handler(Json(payload): Json<Settings>) -> Json<serde_json::Value> {
    let cmd = if payload.auto_updates {
        "pkexec systemctl enable --now kader42-autoupdate.timer"
    } else {
        "pkexec systemctl disable --now kader42-autoupdate.timer"
    };
    let _ = Command::new("sh").arg("-c").arg(cmd).output();

    let data = serde_json::json!({
        "update_time": payload.update_time,
        "retention_completed_days": payload.retention_completed_days,
        "retention_failed_days": payload.retention_failed_days,
    });

    let _ = fs::write(SETTINGS_FILE, serde_json::to_string_pretty(&data).unwrap_or_default());
    Json(serde_json::json!({"status": "saved"}))
}

// --- JOB DB HANDLERS ---

async fn get_jobs(State(state): State<Arc<AppState>>) -> Json<Vec<Job>> {
    let conn = state.db_conn.lock().unwrap();
    let mut stmt = conn
        .prepare("SELECT id, package_name, action, status, progress, log_output, created_at FROM jobs ORDER BY id DESC LIMIT 50")
        .unwrap();

    let jobs_iter = stmt
        .query_map([], |row| {
            Ok(Job {
                id: row.get(0)?,
                package_name: row.get(1)?,
                action: row.get(2)?,
                status: row.get(3)?,
                progress: row.get(4)?,
                log_output: row.get(5)?,
                created_at: row.get(6)?,
            })
        })
        .unwrap();

    let mut jobs = Vec::new();
    for job in jobs_iter.flatten() {
        jobs.push(job);
    }

    Json(jobs)
}

async fn create_job(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<CreateJobRequest>,
) -> impl IntoResponse {
    let conn = state.db_conn.lock().unwrap();
    let source = payload.source.unwrap_or_else(|| "repo".to_string());

    let res = conn.execute(
        "INSERT INTO jobs (package_name, source, action, status, progress) VALUES (?1, ?2, ?3, 'queued', 0)",
        [&payload.package_name, &source, &payload.action],
    );

    match res {
        Ok(_) => {
            let id = conn.last_insert_rowid();
            (StatusCode::CREATED, Json(serde_json::json!({"id": id, "status": "queued"})))
        }
        Err(_) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({"error": "Failed to create job"})),
        ),
    }
}

async fn get_job_status(
    State(state): State<Arc<AppState>>,
    Path(id): Path<i64>,
) -> Json<serde_json::Value> {
    let conn = state.db_conn.lock().unwrap();
    let mut stmt = conn
        .prepare("SELECT status, progress, log_output FROM jobs WHERE id = ?1")
        .unwrap();

    let result = stmt.query_row([id], |row| {
        Ok(serde_json::json!({
            "status": row.get::<_, String>(0)?,
            "progress": row.get::<_, i32>(1)?,
            "log": row.get::<_, Option<String>>(2)?.unwrap_or_default()
        }))
    });

    Json(result.unwrap_or_else(|_| serde_json::json!({"status": "unknown", "progress": 0, "log": ""})))
}

async fn get_job_log(
    State(state): State<Arc<AppState>>,
    Path(id): Path<i64>,
) -> Json<serde_json::Value> {
    let conn = state.db_conn.lock().unwrap();
    let log: Result<String, _> = conn.query_row(
        "SELECT log_output FROM jobs WHERE id = ?1",
        [id],
        |row| row.get(0),
    );

    Json(serde_json::json!({
        "id": id,
        "log": log.unwrap_or_default()
    }))
}

async fn delete_job(
    State(state): State<Arc<AppState>>,
    Path(id): Path<i64>,
) -> Json<serde_json::Value> {
    let conn = state.db_conn.lock().unwrap();
    let _ = conn.execute("DELETE FROM jobs WHERE id = ?1", [id]);
    Json(serde_json::json!({"status": "deleted", "id": id}))
}

// --- UTILS ---

fn capitalize(s: &str) -> String {
    let clean = s.replace("-bin", "").replace("-git", "");
    let mut c = clean.chars();
    match c.next() {
        None => String::new(),
        Some(f) => f.to_uppercase().collect::<String>() + c.as_str(),
    }
}