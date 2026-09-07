/*
 * Angepasste Sidebar QML für den KADER 42 Installer.
 * Basiert auf dem Calamares Sidebar Template (Manjaro Style).
 * Styling: Dunkler Hintergrund (#12121C) mit Neonblau-Akzenten (#00BFFF).
 */

import io.calamares.ui 1.0
import io.calamares.core 1.0

import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import QtQuick.Shapes 1.15

Rectangle {
    id: sideBar;

    readonly property color sidebarBackground: "#12121C" // Sehr Dunkel
    readonly property color sidebarHighlight: "#00BFFF"   // Neonblau
    readonly property color sidebarMid: "#1A1A2A"         // Etwas heller als Hintergrund, für Linien/inaktive Punkte
    readonly property color sidebarText: "#E0F2F7"        // Heller Text

    color: sidebarBackground; // Hauptfarbe der Sidebar

    antialiasing: true

    Rectangle {
        anchors.fill: parent
        anchors.rightMargin: 25 / 2
        color: sidebarBackground;
    }

    ListView {
        id: list
        anchors.leftMargin: 12
        anchors.fill: parent
        model: ViewManager
        interactive: false
        spacing: 0

        delegate: RowLayout {
            // Ausblenden des ersten Schritts (meistens "Welcome" oder "Start")
            visible: index != 0
            //height: index == 0 ? 0 : 50
            height: index == 0 ? 140 : 40
            width: parent.width

            Text {
                Layout.fillWidth: true
                fontSizeMode: Text.Fit
                color: {
                    // Aktueller Schritt = Neonblau, Abgeschlossen = Hell, Zukünftig = Etwas dunkler
                    if (index == ViewManager.currentStepIndex) {
                        return sidebarHighlight;
                    } else if (index < ViewManager.currentStepIndex) {
                        return sidebarText;
                    }
                    return sidebarText;
                }
                text: display;
                font.pointSize : 12
                minimumPointSize: 5
                Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
                clip: true // Stellt sicher, dass der Text am Rand abgeschnitten wird
            }

            // --- STATUS INDIKATOR (PUNKT & LINIE) ---
            Item {
                Layout.fillHeight: true
                // Breite für den Indikator reduziert (von 35 auf 25), um mehr Platz für den Text zu lassen
                Layout.preferredWidth: 25 

                // Der runde Punkt
                Rectangle {
                    anchors.centerIn: parent
                    id: image
                    height: parent.width * 0.65
                    width: height
                    radius: height / 2
                    color: {
                        // Zukünftiger Schritt
                        if (index > ViewManager.currentStepIndex) {
                            return sidebarMid; // Dunkle inaktive Farbe
                        }
                        // Aktueller oder abgeschlossener Schritt
                        return sidebarHighlight; // Neonblau
                    }
                    z: 10
                }
                
                // Obere Linie (Verbindung zum vorherigen Schritt)
                Rectangle {
                    color: {
                        if (index > ViewManager.currentStepIndex && index != 1) {
                            return sidebarMid; // Dunkel (inaktiv)
                        }
                        return sidebarHighlight; // Neonblau (aktiv)
                    }
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.bottom: image.verticalCenter
                    height: parent.height / 2
                    width: 5
                    z: 0
                }

                // Untere Linie (Verbindung zum nächsten Schritt)
                Rectangle {
                    color: {
                        if (index < ViewManager.currentStepIndex || ViewManager.currentStepIndex == list.count - 1) {
                            return sidebarHighlight; // Neonblau (abgeschlossen)
                        }
                        return sidebarMid; // Dunkel (zukünftig)
                    }
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: image.verticalCenter
                    height: parent.height / 2
                    width: 5
                    z: 0
                }

                // Neon-Ring um den AKTUELLEN Schritt
                Shape {
                    visible: index == ViewManager.currentStepIndex
                    id: shape
                    anchors.fill: parent
                    smooth: true
                    layer.enabled: true
                    layer.samples: 8

                    ShapePath {
                        fillColor: "transparent"
                        strokeColor: sidebarHighlight // Neonblau
                        strokeWidth: 3
                        capStyle: ShapePath.FlatCap

                        PathAngleArc {
                            centerX: shape.width / 2; centerY: shape.height / 2
                            radiusX: 10; radiusY: 10 // Radius reduziert, um innerhalb von Layout.preferredWidth: 25 zu passen
                            startAngle: 0
                            sweepAngle: 360
                        }
                    }
                }
            }
        }
        
// --- HEADER BLOCK IN calamares-sidebar.qml (LOGO WIEDERHERSTELLEN) ---
        header: RowLayout { 
            height: 55
            anchors.right: parent.right
            anchors.left: parent.left
            
            // Linker Platzhalter: Füllt den verfügbaren Raum
            Item {
                Layout.fillWidth: true
            }
            
            // IHR LOGO
            Image {
                Layout.preferredHeight: 225
                Layout.preferredWidth: 190
                source: "images/logo.svg" 
                fillMode: Image.PreserveAspectFit
                Layout.alignment: Qt.AlignVLeft 
            }

            // Rechter Platzhalter: Füllt den restlichen Raum und zentriert das Logo
            Item {
                Layout.fillWidth: true
            }
        }
}
    
    // --- UNTERE VERBINDUNGSLINIE ---
    Item {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: list.height - list.contentHeight
        width: 25 // Breite angepasst
        Rectangle {
            color: {
                if (ViewManager.currentStepIndex == list.count - 1) {
                    return sidebarHighlight; // Neonblau (Installation abgeschlossen)
                }
                return sidebarMid; // Dunkel (Installation läuft)
            }
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            height: parent.height
            width: 5
            z: 0
        }
    }
}
