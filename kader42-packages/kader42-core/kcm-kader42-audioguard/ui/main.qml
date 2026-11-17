import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.kcmutils as KCM

KCM.SimpleKCM {
    id: root

    readonly property bool isGerman: Qt.locale().name.startsWith("de")
    property bool serviceActive: kcm.isServiceActive()
    property bool notifyEnabled: kcm.notificationsEnabled()

    Kirigami.FormLayout {
        QQC2.Label {
            Layout.fillWidth: true
            Layout.maximumWidth: Kirigami.Units.gridUnit * 32
            wrapMode: Text.WordWrap
            text: root.isGerman
                ? "Der Kader42 Audio Guard überwacht im Hintergrund Ihre Soundkarten und USB-Docks (z. B. Dell WD15). Falls eine Anwendung ein ALSA-Gerät exklusiv blockiert oder PipeWire auf „Schein-Ausgabe“ zurückfällt, stellt der Dienst die Audio-Ausgabe automatisch wieder her."
                : "Kader42 Audio Guard monitors your sound cards and USB docks (such as the Dell WD15) in the background. If an application exclusively locks an ALSA device or PipeWire falls back to Dummy Output, the service automatically restores audio output."
        }

        Kirigami.Separator {
            Kirigami.FormData.isSection: true
        }

        QQC2.CheckBox {
            id: serviceCheck
            Kirigami.FormData.label: root.isGerman ? "Hintergrunddienst:" : "Background service:"
            text: root.isGerman
                ? "Überwachung beim Anmelden aktivieren"
                : "Enable monitoring on login"
            checked: root.serviceActive
            onToggled: {
                kcm.setServiceEnabled(checked)
                root.serviceActive = kcm.isServiceActive()
                checked = root.serviceActive
            }
        }

        QQC2.Label {
            Kirigami.FormData.label: root.isGerman ? "Status:" : "Status:"
            text: root.serviceActive
                ? (root.isGerman ? "Aktiv (läuft im Hintergrund)" : "Active (running in background)")
                : (root.isGerman ? "Inaktiv" : "Inactive")
            color: root.serviceActive ? Kirigami.Theme.positiveTextColor : Kirigami.Theme.disabledTextColor
        }

        QQC2.CheckBox {
            id: notifyCheck
            Kirigami.FormData.label: root.isGerman ? "Benachrichtigungen:" : "Notifications:"
            text: root.isGerman
                ? "Desktop-Popups bei Blockaden und Reparaturen anzeigen"
                : "Show desktop popups on device locks and recovery"
            checked: root.notifyEnabled
            onToggled: {
                kcm.setNotificationsEnabled(checked)
                root.notifyEnabled = checked
            }
        }

        RowLayout {
            Kirigami.FormData.label: root.isGerman ? "Aktionen:" : "Actions:"
            spacing: Kirigami.Units.smallSpacing

            QQC2.Button {
                icon.name: "notifications"
                text: root.isGerman ? "Test-Meldung" : "Test notification"
                enabled: root.notifyEnabled
                onClicked: kcm.testNotify()
            }

            QQC2.Button {
                id: repairButton
                icon.name: "view-refresh"
                text: root.isGerman ? "Audio jetzt reparieren" : "Repair audio now"
                onClicked: {
                    repairButton.enabled = false
                    const ok = kcm.repairAudio()
                    repairButton.enabled = true
                    statusBanner.type = ok ? Kirigami.MessageType.Positive : Kirigami.MessageType.Warning
                    statusBanner.text = ok
                        ? (root.isGerman
                            ? "PipeWire und WirePlumber wurden erfolgreich neu initialisiert."
                            : "PipeWire and WirePlumber have been successfully reinitialized.")
                        : (root.isGerman
                            ? "Ein Programm belegt das Audiogerät noch exklusiv. Bitte schließen Sie die blockierende Anwendung."
                            : "An application is still holding an exclusive lock on the audio device. Please close the blocking application.")
                    statusBanner.visible = true
                }
            }
        }

        Kirigami.InlineMessage {
            id: statusBanner
            Layout.fillWidth: true
            Layout.maximumWidth: Kirigami.Units.gridUnit * 32
            visible: false
            showCloseButton: true
        }
    }
}
