print("Loading Kickoff Shortcut Script");

var panelsList = panels();

for (var i = 0; i < panelsList.length; i++) {
    var panel = panelsList[i];
    var widgets = panel.widgets();
    for (var j = 0; j < widgets.length; j++) {
        var w = widgets[j];
        if (w.type === "org.kde.plasma.kickoff") {
            w.currentConfigGroup = ["Shortcuts"];
            w.writeConfig("global", "Meta");
            print("Set Kickoff Shortcut successfully!");
        }
    }
}