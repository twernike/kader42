// // Iterates through all of the user's existing panels

var panelsList = panels();

for (var i = 0; i < panelsList.length; ++i) {
    var panel = panelsList[i];
    var widgetsList = panel.widgets();

    for (var j = 0; j < widgetsList.length; ++j) {
        var widget = widgetsList[j];

        // We're specifically looking for the Icons-Only Task Manager
        if (widget.type === "org.kde.plasma.icontasks") {
            widget.currentConfigGroup = ["General"];
            
            // Reads the user's current startup programs
            var currentLaunchers = widget.readConfig("launchers");
            
            if (currentLaunchers) {
                var launchersArray = [];

                // If it's an array or a comma-separated string, we'll clean it up:
                if (Array.isArray(currentLaunchers)) {
                    launchersArray = currentLaunchers;
                } else if (typeof currentLaunchers === "string") {
                    launchersArray = currentLaunchers.split(",");
                }

                // Filters out all entries related to Discover or PackageKit
                var cleanedLaunchers = [];
                for (var k = 0; k < launchersArray.length; ++k) {
                    var launcher = launchersArray[k].trim();
                    if (launcher.indexOf("org.kde.discover") === -1 && 
                        launcher.indexOf("discover") === -1) {
                        cleanedLaunchers.push(launcher);
                    }
                }

                // Returns the filtered list as a clean, true JavaScript array
                widget.writeConfig("launchers", cleanedLaunchers);
            }
        }
    }
}