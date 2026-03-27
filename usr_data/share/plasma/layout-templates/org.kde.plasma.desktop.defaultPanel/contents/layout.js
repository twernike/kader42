// cleanup

var panels = panels();
for (var i = 0; i < panels.length; ++i) {
    panels[i].remove();
}

// Notebook Panel
var notebook = new Panel
var notebookScreen = notebook.screen
notebook.location = "bottom"
notebook.height = 32

// No need to set panel.location as ShellCorona::addPanel will automatically pick one available edge

// For an Icons-Only Task Manager on the bottom, *3 is too much, *2 is too little
// Round up to next highest even number since the Panel size widget only displays
// even numbers
notebook.height = 2 * Math.ceil(gridUnit * 2.5 / 2)

// Restrict horizontal panel to a maximum size of a 21:9 monitor
const maximumAspectRatio = 21/9;
if (notebook.formFactor === "horizontal") {
    const geo = screenGeometry(notebookScreen);
    const maximumWidth = Math.ceil(geo.height * maximumAspectRatio);

    if (geo.width > maximumWidth) {
        notebook.alignment = "center";
        notebook.minimumLength = maximumWidth;
        notebook.maximumLength = maximumWidth;
    }
}
notebook.writeConfig("panelType", "notebook")
notebook.writeConfig("convertibleManaged", true)
notebook.writeConfig("managedBy", "convertible")
notebook.writeConfig("panelRole", "notebook")
notebook.writeConfig("visibilityMode", "desktop")


// notebook.currentConfigGroup = ["General"]
// notebook.writeConfig("defaultLauncher", "org.kde.plasma.kickerdash")
var kickoff=notebook.addWidget("org.kde.plasma.kickoff")
// kickoff.currentConfigGroup = ["Shortcuts"];
// kickoff.writeConfig("globalShortcut", "Meta");

notebook.addWidget("org.kde.plasma.pager")
notebook.addWidget("org.kde.plasma.icontasks")
notebook.addWidget("org.kde.plasma.marginsseparator")
notebook.addWidget("org.kde.plasma.systemtray")
notebook.addWidget("org.kde.plasma.digitalclock")
notebook.addWidget("org.kde.plasma.showdesktop")

/* Next up is determining whether to add the Input Method Panel
 * widget to the panel or not. This is done based on whether
 * the system locale's language id is a member of the following
 * white list of languages which are known to pull in one of
 * our supported IME backends when chosen during installation
 * of common distributions. */

var langIds = ["as",    // Assamese
               "bn",    // Bengali
               "bo",    // Tibetan
               "brx",   // Bodo
               "doi",   // Dogri
               "gu",    // Gujarati
               "hi",    // Hindi
               "ja",    // Japanese
               "kn",    // Kannada
               "ko",    // Korean
               "kok",   // Konkani
               "ks",    // Kashmiri
               "lep",   // Lepcha
               "mai",   // Maithili
               "ml",    // Malayalam
               "mni",   // Manipuri
               "mr",    // Marathi
               "ne",    // Nepali
               "or",    // Odia
               "pa",    // Punjabi
               "sa",    // Sanskrit
               "sat",   // Santali
               "sd",    // Sindhi
               "si",    // Sinhala
               "ta",    // Tamil
               "te",    // Telugu
               "th",    // Thai
               "ur",    // Urdu
               "vi",    // Vietnamese
               "zh_CN", // Simplified Chinese
               "zh_TW"] // Traditional Chinese

if (langIds.indexOf(languageId) != -1) {
    notebook.addWidget("org.kde.plasma.kimpanel");
}

// notebook.enabled = true

// // Tablet Panel
// var tablet = new Panel
// tablet.location = "bottom"
// tablet.height = 64
// tablet.addWidget("org.kde.plasma.icontasks")

// var tabletScreen = tablet.screen

// // Tablet Panel zunächst deaktivieren
// tablet.enabled = false
// tablet.writeConfig("panelType", "tablet")
// tablet.writeConfig("convertibleManaged", true)
// tablet.writeConfig("managedBy", "convertible")
// tablet.writeConfig("panelRole", "tablet")
// tablet.writeConfig("visibilityMode", "tablet")

// tablet.hiding = "dodgewindows"
// tablet.enabled = false
// var dash = tablet.addWidget("org.kde.plasma.kickerdash");

// dash.currentConfigGroup = ["General"];
// dash.writeConfig("showCategories", false); 
// dash.writeConfig("icon", "dashboard-show");