shareCalamares="/usr/share/calamares"
modules="$shareCalamares/modules"
branding="$shareCalamares/branding"
kaderBranding="$branding/kader42"
etcCalamares="/etc/calamares"
qmlCalamares="$shareCalamares/qml"
calamaresScripts="$shareCalamares/scripts"
tmpCalamares="calamares-kader-config"

echo -e "[1;98m --------------------------------------------\e[0m"
echo -e "[1;98m | ✍🏼 | create needed calamares directories |\e[0m"
echo -e "[1;98m --------------------------------------------\e[0m"
echo
mkdir -p "$shareCalamares"
mkdir -p "$modules"
mkdir -p "$branding"
mkdir -p "$kaderBranding"
mkdir -p "$qmlCalamares"
mkdir -p "$calamaresScripts"
mkdir -p "$etcCalamares"

echo
echo -e "[1;98m ---------------------------------------------------------------------------[0m"
echo -e "[1;98m | 🗐 | Copy the calamares configuration files to the needed directories...|[0m"
echo -e "[1;98m ---------------------------------------------------------------------------[0m"

cp -r $tmpCalamares/modules/. $modules
cp -r $tmpCalamares/branding/. $branding
cp -r $tmpCalamares/qml/. $qmlCalamares
cp -r $tmpCalamares/scripts/. $calamaresScripts
cp -r $tmpCalamares/settings.conf $etcCalamares