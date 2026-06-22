import sys
import subprocess
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction

def open_software_center():
    # Startet dein Software Center als eigenständigen Prozess abgelöst vom Tray
    subprocess.Popen(["kader42-software-center"])

def main():
    # Eine QApplication ohne sichtbares Hauptfenster initialisieren
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # 1. Tray Icon erstellen und dein mello.svg zuweisen
    # QIcon.fromTheme sucht automatisch in /usr/share/icons/hicolor/...
    tray_icon = QSystemTrayIcon(QIcon.fromTheme("software-center-tray-icon"), app)
    tray_icon.setToolTip("Kader42 Software Center")

    # 2. Kontextmenü (Rechtsklick) bauen
    menu = QMenu()
    
    open_action = QAction("Software Center öffnen", menu)
    open_action.triggered.connect(open_software_center)
    menu.addAction(open_action)
    
    menu.addSeparator()
    
    quit_action = QAction("Beenden", menu)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    tray_icon.setContextMenu(menu)

    # 3. Interaktion: Einfacher Linksklick öffnet die App direkt
    def on_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            open_software_center()

    tray_icon.activated.connect(on_activated)

    # Icon im Systemabschnitt anzeigen
    tray_icon.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()