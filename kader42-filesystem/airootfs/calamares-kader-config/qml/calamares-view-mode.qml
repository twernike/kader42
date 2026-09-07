// --- AUSSCHNITT AUS calamares-view-mode.qml ---

Rectangle {
    id: mainView
    // ... (Weitere Eigenschaften)
    
    // ------------------------------------------------------------------
    // 1. HEADER-BEREICH
    // ------------------------------------------------------------------
    Rectangle {
        id: headerArea
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 100 // Erhöhen Sie die Höhe, um Platz für das Logo zu schaffen
        color: calamares.style.headerColor // oder die gewünschte Farbe

        // HIER FÜGEN WIR DAS LOGO EIN
        Image {
           
            anchors.fill: parent
            
            source: "images/kader-banner2.svg" // Ihr SVG-Pfad
            
            fillMode: Image.PreserveAspectFit
            
            // Optional: Zentrierung in der Breite
            // anchors.horizontalCenter: parent.horizontalCenter
        }

        // ------------------------------------------------
        // 2. Schritte-Zähler/Überschrift (MUSS VERSCHOBEN WERDEN)
        // ------------------------------------------------
        Item {
            anchors.top: headerArea.top
            anchors.topMargin: 60 // Starte *unter* dem Logo (55px + 5px Abstand)
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: headerArea.bottom
            
            // Fügen Sie hier den ursprünglichen Inhalt des Headers ein
            // (z.B. den Text des aktuellen Installationsschritts)
            
            // Beispiel:
            // Text {
            //     text: calamares.navigation.currentPage.title
            //     anchors.centerIn: parent
            //     ...
            // }
        }
    }
    
    // ------------------------------------------------------------------
    // 3. CONTENT-BEREICH (muss unter dem erhöhten Header beginnen)
    // ------------------------------------------------------------------
    Rectangle {
        id: contentArea
        anchors.top: headerArea.bottom // Wichtig: Beginnt nach dem erhöhten Header
        // ... (Der Rest der Content-Definition)
    }
    // ...
}