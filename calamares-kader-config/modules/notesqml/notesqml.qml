import QtQuick
import QtQuick.Controls

Item {
    id: root
    
    // Wir erzwingen eine Suche in verschiedenen Ebenen
    readonly property string debugText: {
        // Test 1: Existiert 'config' global?
        if (typeof config !== "undefined") return "Erfolg! Config gefunden. Keys: " + Object.keys(config).join(", ");
        
        // Test 2: Hat die Komponente ein 'configuration' Property? (Manche Versionen nutzen das)
        if (typeof configuration !== "undefined") return "Gefunden als 'configuration'.";
        
        // Test 3: Ist es an root gebunden?
        if (root.config) return "An root gebunden.";

        return "KRITISCH: Calamares hat absolut kein Konfig-Objekt an dieses QML übergeben.";
    }

    Rectangle {
        anchors.fill: parent
        color: "#1A1A1B"
        Text {
            anchors.centerIn: parent
            text: root.debugText
            color: "red"
            font.pointSize: 14
        }
    }
}