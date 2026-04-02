import QtQuick
import QtMultimedia

Item {
    id: root
    anchors.fill: parent
    property int stage: 0

    Rectangle {
        anchors.fill: parent
        color: "black"
    }

    VideoOutput {
        id: videoOutput
        anchors.fill: parent
        fillMode: VideoOutput.PreserveAspectFit
        opacity: 1
        Behavior on opacity {
            NumberAnimation { duration: 500 }
        }
    }

    MediaPlayer {
        id: mediaPlayer
        videoOutput: videoOutput
        // Wir nutzen hier eine sicherere Pfad-Auflösung
        source: Qt.resolvedUrl("images/mello_winkt.mp4")
        loops: MediaPlayer.Infinite
        
        // Debugging-Hilfe
        onErrorOccurred: (error, errorString) => console.log("Video-Fehler: " + errorString)
        
        Component.onCompleted: {
            mediaPlayer.play()
        }
    }

    Connections {
        target: root
        // Plasma 6 verlangt zwingend die 'function' Syntax für Signale
        function onStageChanged() {
            if (root.stage >= 5) {
                videoOutput.opacity = 0
            }
        }
    }
}