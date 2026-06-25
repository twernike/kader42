import sys
import os
import locale
import subprocess
import urllib.request
import json
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QTimer

# ==========================================================
# LANGUAGE & LOCALIZATION SETUP
# ==========================================================
try:
    SYSTEM_LANG = locale.getdefaultlocale()[0][:2]
except:
    SYSTEM_LANG = "de"

if SYSTEM_LANG not in ["de", "en"]:
    SYSTEM_LANG = "de"

TRANSLATIONS = {
    "de": {
        "tray_tooltip": "Kader42 Software Center",
        "tray_tooltip_updates": "Kader42 Software Center ({count} Updates verfügbar)",
        "menu_updates_available": " Updates verfügbar ({count})",
        "menu_open_store": "Software Center öffnen",
        "menu_quit": "Beenden"
    },
    "en": {
        "tray_tooltip": "Kader42 Software Center",
        "tray_tooltip_updates": "Kader42 Software Center ({count} updates available)",
        "menu_updates_available": " Updates available ({count})",
        "menu_open_store": "Open Software Center",
        "menu_quit": "Quit"
    }
}

def _(key):
    return TRANSLATIONS[SYSTEM_LANG].get(key, key)

# ==========================================================
# ACTIONS & LOGIC
# ==========================================================
def open_software_center():
    # Launch your Software Center as a standalone process, separate from the system tray
    subprocess.Popen(["kader42-software-center"])

def open_update_center():
    # Passes the argument that opens the Software Center directly in the Updates tab
    subprocess.Popen(["kader42-software-center", "--view=updates"])

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    tray_icon = QSystemTrayIcon(QIcon.fromTheme("software-center-tray-icon"), app)
    tray_icon.setToolTip(_("tray_tooltip"))

    # Initialize the context menu (right-click) as an empty default menu
    menu = QMenu()
    tray_icon.setContextMenu(menu)

    # Outsourced menu creation for dynamic updating
    def rebuild_menu(update_count=0):
        menu.clear()
        
        # When updates are available, the user sees a prominent notification at the very top
        if update_count > 0:
            update_text = _("menu_updates_available").format(count=update_count)
            update_action = QAction(update_text, menu)
            update_action.triggered.connect(open_update_center)
            
            # Make the text bold for better visibility
            font = update_action.font()
            font.setBold(True)
            update_action.setFont(font)
            
            menu.addAction(update_action)
            menu.addSeparator()

        # Standard Actions
        open_action = QAction(_("menu_open_store"), menu)
        open_action.triggered.connect(open_software_center)
        menu.addAction(open_action)
        
        menu.addSeparator()
        
        quit_action = QAction(_("menu_quit"), menu)
        quit_action.triggered.connect(app.quit)
        menu.addAction(quit_action)

    # Set the menu to empty/default at startup
    rebuild_menu(0)

    def check_api_updates():
        try:
            with urllib.request.urlopen("http://localhost:8080/updates", timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                total_updates = data.get("total_updates", 0)
                
                # Rebuild the menu with the new count in real time!
                rebuild_menu(total_updates)
                
                if total_updates > 0:
                    tooltip_text = _("tray_tooltip_updates").format(count=total_updates)
                    tray_icon.setToolTip(tooltip_text)
                    # Optional: Set a different icon (e.g., one with a red dot)
                    # tray_icon.setIcon(QIcon.fromTheme(“software-center-tray-update-icon”))
                else:
                    tray_icon.setToolTip(_("tray_tooltip"))
                    tray_icon.setIcon(QIcon.fromTheme("software-center-tray-icon"))
                    
        except Exception as e:
            print(f"Tray-Notifier Error during API retrieval: {e}")

    # Timer for periodic polling (every 30 minutes)
    update_timer = QTimer(app)
    update_timer.timeout.connect(check_api_updates)
    update_timer.start(30 * 60 * 1000)

    # Instant startup check after 1 second
    QTimer.singleShot(1000, check_api_updates)

    # Interaction: Left-clicking opens the app as usual
    def on_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            open_software_center()

    tray_icon.activated.connect(on_activated)
    tray_icon.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()