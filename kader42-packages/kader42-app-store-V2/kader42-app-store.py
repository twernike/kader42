import sys
import os
import json
import subprocess
import locale
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QListWidget, QListWidgetItem, QScrollArea, QFrame, QGridLayout)
from PySide6.QtCore import Qt, QSize, QTimer, QUrl
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

API_URL = "http://127.0.0.1:8080"

# ==========================================================
# LANGUAGE & LOCALIZATION SETUP
# ==========================================================
try:
    # Ermittelt das System-Locale (z.B. de_DE -> de, en_US -> en)
    SYSTEM_LANG = locale.getdefaultlocale()[0][:2]
except:
    SYSTEM_LANG = "de"

if SYSTEM_LANG not in ["de", "en"]:
    SYSTEM_LANG = "de"  # Fallback auf Haupt-OS-Sprache

TRANSLATIONS = {
    "de": {
        "search_placeholder": "🔎 Durchsuche Repositories und das AUR...",
        "install": "Installieren",
        "remove": "Entfernen",
        "status_installed": "✓ Installiert",
        "status_available": "Verfügbar",
        "status_checking": "Prüfe...",
        "status_queue": "⌛ In Warteschlange..."
    },
    "en": {
        "search_placeholder": "🔎 Search repositories and AUR...",
        "install": "Install",
        "remove": "Remove",
        "status_installed": "✓ Installed",
        "status_available": "Available",
        "status_checking": "Checking...",
        "status_queue": "⌛ Queued..."
    }
}

def _(key):
    return TRANSLATIONS[SYSTEM_LANG].get(key, key)

# ==========================================================
# 1. DIE APP-KACHEL
# ==========================================================
class AppCard(QFrame):
    def __init__(self, name, description, pkg_name, icon_name=None, source="repo", flatpak_id=None):
        super().__init__()
        self.pkg_name = pkg_name
        self.source = source
        self.flatpak_id = flatpak_id
        self.icon_name = icon_name if icon_name else "package-x-generic"
        self.current_job_id = None
        
        self.setObjectName("AppCard")
        self.setFixedSize(240, 280)
        
        self.setStyleSheet("""
            #AppCard { background-color: #131926; border-radius: 14px; border: 2px solid #232e48; }
            #AppCard:hover { border: 2px solid #00f0ff; background-color: #1a233a; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)
        
        # Icon Label
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)
        self.set_system_fallback_icon()
        
        # Name
        name_label = QLabel(name)
        name_label.setFont(QFont("Cantarell", 13, QFont.Weight.Bold))
        name_label.setStyleSheet("color: white; background: transparent;")
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # Beschreibung (Zweisprachig aus dem JSON-Dict extrahiert)
        desc_text = ""
        if isinstance(description, dict):
            desc_text = description.get(SYSTEM_LANG, description.get("de", ""))
        else:
            desc_text = description

        self.desc_label = QLabel(desc_text)
        self.desc_label.setStyleSheet("color: #8fa0c4; font-size: 11px; background: transparent;")
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setFixedHeight(55)
        layout.addWidget(self.desc_label)
        
        # Status & Button
        self.status_label = QLabel(_("status_checking"))
        self.status_label.setStyleSheet("font-size: 10px; color: #00f0ff; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.btn = QPushButton(_("install"))
        self.btn.setFont(QFont("Cantarell", 10, QFont.Weight.Bold))
        self.btn.setFixedHeight(35)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.clicked.connect(self.trigger_api_action)
        layout.addWidget(self.btn)
        
        self.nav_manager = QNetworkAccessManager(self)
        
        if self.flatpak_id and self.flatpak_id.strip():
            self.load_flathub_icon()
            
        QTimer.singleShot(10, self.update_status_local)

    def set_system_fallback_icon(self):
        # Erkennt, ob ein absoluter Pfad (wie /usr/share/icons/mello.png) oder ein Theme-Name angegeben ist
        if os.path.isabs(self.icon_name) and os.path.exists(self.icon_name):
            pixmap = QPixmap(self.icon_name)
            self.icon_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon = QIcon.fromTheme(self.icon_name, QIcon.fromTheme("package-x-generic"))
            self.icon_label.setPixmap(icon.pixmap(QSize(64, 64)))

    def load_flathub_icon(self):
        url = QUrl(f"https://dl.flathub.org/repo/appstream/x86_64/icons/128x128/{self.flatpak_id.strip()}.png")
        req = QNetworkRequest(url)
        req.setRawHeader(b"User-Agent", b"Mozilla/5.0 (X11; Linux x86_64)")
        self.reply = self.nav_manager.get(req)
        self.reply.finished.connect(self.on_icon_downloaded)

    def on_icon_downloaded(self):
        if self.reply.error() == QNetworkReply.NoError:
            pixmap = QPixmap()
            if pixmap.loadFromData(self.reply.readAll()):
                self.icon_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.reply.deleteLater()

    def update_status_local(self):
        is_installed = os.path.exists(f"/usr/bin/{self.pkg_name}") or \
                       os.path.exists(f"/usr/bin/{self.pkg_name.split('-')[0]}")
        
        if is_installed:
            self.status_label.setText(_("status_installed"))
            self.btn.setText(_("remove"))
            self.btn.setStyleSheet("background-color: #e74c3c; border-radius: 8px; color: white; border: none;")
            self.action_mode = "remove"
        else:
            self.status_label.setText(_("status_available"))
            self.btn.setText(_("install"))
            self.btn.setStyleSheet("background-color: #3daee9; border-radius: 8px; color: white; border: none;")
            self.action_mode = "install"
        self.btn.setEnabled(True)

    def trigger_api_action(self):
        self.btn.setEnabled(False)
        self.status_label.setText(_("status_queue"))
        
        req = QNetworkRequest(QUrl(f"{API_URL}/job"))
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        
        job_data = {"package_name": self.pkg_name, "source": self.source, "action": self.action_mode}
        payload = json.dumps(job_data).encode("utf-8")
        
        reply = self.nav_manager.post(req, payload)
        reply.finished.connect(lambda: self.on_action_triggered(reply))

    def on_action_triggered(self, reply):
        if reply.error() == QNetworkReply.NoError:
            try:
                response_data = json.loads(reply.readAll().data().decode())
                self.current_job_id = response_data.get("id")
                self.poll_timer = QTimer(self)
                self.poll_timer.timeout.connect(self.poll_job_status)
                self.poll_timer.start(1000)
            except:
                self.btn.setEnabled(True)
        else:
            self.btn.setEnabled(True)
        reply.deleteLater()

    def poll_job_status(self):
        if not self.current_job_id: return
        req = QNetworkRequest(QUrl(f"{API_URL}/job/{self.current_job_id}"))
        reply = self.nav_manager.get(req)
        reply.finished.connect(lambda: self.on_poll_finished(reply))

    def on_poll_finished(self, reply):
        if reply.error() == QNetworkReply.NoError:
            try:
                job = json.loads(reply.readAll().data().decode())
                status = job.get("status")
                progress = job.get("progress", 0)
                
                if status in ["installing", "removing", "building_aur", "running"]:
                    self.status_label.setText(f"⌛ {status} ({progress}%)")
                elif status == "completed":
                    self.poll_timer.stop()
                    self.update_status_local()
                elif status == "failed":
                    self.poll_timer.stop()
                    self.update_status_local()
            except:
                pass
        reply.deleteLater()


# ==========================================================
# 2. DAS HAUPTFENSTER (Zweisprachige Sidebar & Suche)
# ==========================================================
class KaderStore(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kader⁴² App Store")
        self.resize(1240, 900)  # Höhe minimal erhöht für den Banner
        self.setStyleSheet("background-color: #0b0f19; color: white;")
        
        # ==========================================================
        # NEU: ANWENDUNGS-ICON ZUWEISEN
        # ==========================================================
        # Pfad zu deinem Logo (wähle einen der beiden Ansätze):
        app_icon_path = "/usr/share/icons/mello.png" 
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
        else:
            self.setWindowIcon(QIcon.fromTheme("system-software-install"))

        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.on_json_loaded)
        
        self.apps_data = {"categories": [], "apps": {}}
        
        central = QWidget()
        self.setCentralWidget(central)
        self.root = QVBoxLayout(central)
        self.root.setContentsMargins(15, 15, 15, 15)
        
        # Header (Suchleiste)
        header = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(_("search_placeholder"))
        self.search.setFixedHeight(45)
        self.search.setStyleSheet("""
            QLineEdit { background: #131926; border-radius: 10px; padding: 10px; color: white; border: 1px solid #232e48; font-size: 14px; }
            QLineEdit:focus { border: 1px solid #00f0ff; }
        """)
        self.search.textChanged.connect(self.start_search_timer)
        header.addWidget(self.search)
        self.root.addLayout(header)

        # Haupt-Inhaltsbereich
        content = QHBoxLayout()
        
        # Sidebar Setup
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(270)
        self.sidebar.setStyleSheet("""
            QListWidget { background: #0b0f19; border: none; } 
            QListWidget::item { 
                padding: 20px; 
                color: #8fa0c4; 
                font-size: 13pt; 
                font-weight: bold; 
                border-bottom: 1px solid #131926; 
            } 
            QListWidget::item:selected { background: #1a233a; color: #00f0ff; border-radius: 10px; }
        """)
        self.sidebar.setIconSize(QSize(32, 32))
        self.sidebar.itemClicked.connect(self.on_sidebar_clicked)
        content.addWidget(self.sidebar)
        
        # Rechter Bereich: Aufgeteilt in Banner (oben) + Scroll-Grid (unten)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        
        # ==========================================================
        # NEU: HERO-BANNER MIT AUTOMATISCHEM FALLBACK
        # ==========================================================
        self.banner_label = QLabel()
        self.banner_label.setFixedHeight(160)
        self.banner_label.setAlignment(Qt.AlignCenter)
        
        # Pfad zu deiner zukünftigen Banner-Grafik
        banner_path = "/usr/share/kader42/kader-store-banner.png"
        
        if os.path.exists(banner_path):
            # Wenn deine Grafik existiert, laden und skalieren wir sie
            banner_pixmap = QPixmap(banner_path)
            self.banner_label.setPixmap(banner_pixmap.scaled(920, 160, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            self.banner_label.setStyleSheet("border-radius: 14px; background: #131926;")
        else:
            # Fallback: Ein schicker CSS-Farbverlauf, bis deine Grafik fertig ist
            self.banner_label.setText("<h2>Kader⁴² Software Hub</h2><p style='color: #8fa0c4;'>Entdecke handverlesene Apps und Tools für dein Convertible.</p>")
            self.banner_label.setStyleSheet("""
                QLabel { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a233a, stop:1 #131926);
                    border: 1px solid #232e48;
                    border-radius: 14px;
                    padding-left: 30px;
                }
            """)
        right_layout.addWidget(self.banner_label)
        
        # Scroll-Bereich für das Kachel-Grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.setSpacing(22)
        self.scroll.setWidget(self.grid_widget)
        
        right_layout.addWidget(self.scroll)
        content.addLayout(right_layout)
        
        self.root.addLayout(content)
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.trigger_search)

        self.fetch_data()
    def fetch_data(self):
        url = QUrl("https://kader42.de/repo/apps.json")
        self.network_manager.get(QNetworkRequest(url))

    def on_json_loaded(self, reply):
        if reply.error() == QNetworkReply.NoError:
            try:
                self.apps_data = json.loads(reply.readAll().data().decode())
                self.setup_sidebar()
            except Exception as e:
                print(f"JSON Parse Fehler: {e}")
        reply.deleteLater()

    def setup_sidebar(self):
        self.sidebar.clear()
        cats = self.apps_data.get("categories", [])
        for c in cats:
            # Holt den übersetzten Kategorie-Namen (de oder en) aus der JSON
            name = c["label"].get(SYSTEM_LANG, c["label"].get("de", "Apps"))
            
            # Icon-Zuweisung (Unterstützt Pfade wie für mello.png und System-Themes)
            icon_path = c.get("icon", "package-x-generic")
            if os.path.isabs(icon_path) and os.path.exists(icon_path):
                icon = QIcon(icon_path)
            else:
                icon = QIcon.fromTheme(icon_path, QIcon.fromTheme("package-x-generic"))
                
            item = QListWidgetItem(icon, name)
            item.setData(Qt.UserRole, c["id"])
            self.sidebar.addItem(item)
            
        if self.sidebar.count() > 0: 
            self.sidebar.setCurrentRow(0)
            self.load_category()

    def on_sidebar_clicked(self, item):
        self.search.blockSignals(True)
        self.search.clear() 
        self.search.blockSignals(False)
        self.load_category()

    def load_category(self):
        self.clear_grid()
        cur = self.sidebar.currentItem()
        if not cur: return
        
        cat_id = cur.data(Qt.UserRole)
        apps = self.apps_data.get("apps", {}).get(cat_id, [])
        
        columns = 3
        for index, a in enumerate(apps):
            row = index // columns
            col = index % columns
            
            # Heuristik für Flathub-Icons bei bekannten Standard-Apps
            flat_id = None
            if a['package'] == "firefox": flat_id = "org.mozilla.firefox"
            elif a['package'] == "vlc": flat_id = "org.videolan.VLC"
            elif a['package'] == "gimp": flat_id = "org.gimp.GIMP"
            elif a['package'] == "openboard": flat_id = "ch.openboard.OpenBoard"
            
            card = AppCard(
                a['name'], 
                a.get('desc', ''), 
                a['package'], 
                icon_name=a.get('icon'), 
                source=a.get('source', 'repo'),
                flatpak_id=flat_id
            )
            self.grid_layout.addWidget(card, row, col)

    def start_search_timer(self, text):
        if text.strip(): self.search_timer.start(400)
        else: self.load_category()

    def trigger_search(self):
        query = self.search.text().strip()
        if not query: return
        self.clear_grid()
        self.sidebar.clearSelection()
        
        try:
            res = subprocess.run(["yay", "-Ss", query], capture_output=True, text=True)
            lines = res.stdout.split("\n")
            apps_found = []
            
            for i in range(0, len(lines) - 1, 2):
                if not lines[i].strip(): continue
                meta = lines[i].split("/")
                if len(meta) < 2: continue
                
                repo_source = meta[0].strip()
                pkg_name = meta[1].split(" ")[0].strip()
                desc = lines[i+1].strip() if i+1 < len(lines) else ""
                source_type = "aur" if repo_source.lower() == "aur" else "repo"
                
                apps_found.append({"name": pkg_name, "desc": desc, "package": pkg_name, "source": source_type})
                if len(apps_found) >= 12: break
            
            columns = 3
            for index, a in enumerate(apps_found):
                row = index // columns
                col = index % columns
                
                flat_id = None
                low_pkg = a['package'].lower()
                if "firefox" in low_pkg: flat_id = "org.mozilla.firefox"
                elif "vlc" in low_pkg: flat_id = "org.videolan.VLC"
                elif "gimp" in low_pkg: flat_id = "org.gimp.GIMP"
                elif "openboard" in low_pkg: flat_id = "ch.openboard.OpenBoard"
                
                card = AppCard(a['name'], a['desc'], a['package'], icon_name="package-x-generic", source=a['source'], flatpak_id=flat_id)
                self.grid_layout.addWidget(card, row, col)
        except Exception as e:
            print(f"Suchfehler: {e}")

    def clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KaderStore()
    window.show()
    sys.exit(app.exec())