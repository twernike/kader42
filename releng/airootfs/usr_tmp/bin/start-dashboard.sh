# Sucht die ID des Dashboards, das wirklich im aktuellen Layout existiert
DASH_ID=$(qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.dumpCurrentLayoutJS | grep -B 1 "org.kde.plasma.kickerdash" | grep "id:" | awk '{print $2}')
qdbus6 org.kde.kglobalaccel /component/plasmashell invokeShortcut "activate widget $DASH_ID"