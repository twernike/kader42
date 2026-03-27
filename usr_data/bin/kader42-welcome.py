#!/usr/bin/env python3
import sys
import os
import gettext
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton, QHBoxLayout
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

# Pfade definieren
CONFIG_FILE = os.path.expanduser("~/.config/distro-welcome-autostart")
MASCOT_IMAGE = "/usr/share/pixmaps/dein-maskottchen.png" # PFAD ANPASSEN!
DISTRO_ICON = "/usr/share/icons/hicolor/64x64/apps/distro-logo.png" # PFAD ANPASSEN!

# Übersetzungen (einfaches Beispiel)
# Für ein echtes GitHub-Projekt nutzt man später .mo/.po Dateien.
translations = {
    'de_DE': {
        'title': 'Willkommen bei [Dein Distro-Name]',
        'welcome_text': 'Hallo! Schön, dass du da bist.\n\nIch bin dein Begleiter für [Dein Distro-Name].\nDein System wurde für das Framework 12 optimiert.',
        'features': '✅ Display-Rotation & Sensoren geladen\n✅ Touch-Gesten aktiviert\n✅ Performance-Profil angepasst',
        'checkbox': 'Dieses Fenster beim nächsten Start nicht mehr anzeigen',
        'close': 'Schließen'
    },
    'en_US': {
        'title': 'Welcome to [Dein Distro-Name]',
        'welcome_text': 'Hi! Great to have you here.\n\nI am your companion for [Dein Distro-Name].\nYour system has been optimized for the Framework 12.',
        'features': '✅ Display rotation & sensors loaded\n✅ Touch gestures enabled\n✅ Performance profile adjusted',
        'checkbox': "Don't show this window again on next start",
        'close': 'Close'
    }
}

# Sprache ermitteln
lang = os.environ.get('LANG', 'en_US').split('.')[0]
t = translations.get(lang, translations['en_US']) # Fallback auf Englisch


class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(t['title'])
        self.setWindowIcon(QIcon(DISTRO_ICON))
        self.setFixedSize(550, 450)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)

        # Layouts
        main_layout = QVBoxLayout()
        content_layout = QHBoxLayout()

        # --- Linke Seite: Maskottchen ---
        self.mascot_label = QLabel()
        pixmap = QPixmap(MASCOT_IMAGE)
        # Bild skalieren, Seitenverhältnis beibehalten
        self.mascot_label.setPixmap(pixmap.scaled(200, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        content_layout.addWidget(self.mascot_label, alignment=Qt.AlignmentFlag.AlignTop)

        # --- Rechte Seite: Text ---
        text_layout = QVBoxLayout()
        self.welcome_label = QLabel(t['welcome_text'])
        self.welcome_label.setWordWrap(True)
        self.welcome_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        text_layout.addWidget(self.welcome_label)

        self.features_label = QLabel(t['features'])
        self.features_label.setStyleSheet("color: #555; margin-top: 15px;")
        text_layout.addWidget(self.features_label)
        
        text_layout.addStretch() # Platzhalter
        content_layout.addLayout(text_layout)

        main_layout.addLayout(content_layout)

        # --- Untere Leiste: Checkbox & Button ---
        bottom_layout = QHBoxLayout()
        self.show_again_cb = QCheckBox(t['checkbox'])
        self.show_again_cb.setChecked(True) # Standardmäßig anzeigen
        bottom_layout.addWidget(self.show_again_cb)

        self.close_button = QPushButton(t['close'])
        self.close_button.clicked.connect(self.close_application)
        bottom_layout.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def close_application(self):
        # Config-Datei schreiben, falls Checkbox NICHT gesetzt ist
        if not self.show_again_cb.isChecked():
            try:
                with open(CONFIG_FILE, 'w') as f:
                    f.write("false")
            except Exception as e:
                print(f"Error writing config: {e}")
        self.close()


def main():
    # Prüfen, ob Autostart deaktiviert ist
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                content = f.read().strip()
                if content == "false":
                    sys.exit(0)
        except Exception as e:
            print(f"Error reading config: {e}")

    app = QApplication(sys.argv)
    window = WelcomeWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()