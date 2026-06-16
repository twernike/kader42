// Wir gehen durch alle Panels (Taskleisten) des Users
for (var p of panels()) {
    for (var a of p.applets) {
        if (a.pluginName === "org.kde.plasma.kickoff") {
            a.currentConfigGroup = ["Configuration", "General"];
            var favs = a.readConfig("favorites");
            var newFav = "applications:kader42-software-center.desktop";
            
            // Nur hinzufügen, wenn es noch nicht drin ist
            if (favs.indexOf(newFav) === -1) {
                if (favs === "") {
                    a.writeConfig("favorites", newFav);
                } else {
                    // Die bestehende Liste wird beibehalten und nur erweitert!
                    a.writeConfig("favorites", favs + "," + newFav);
                }
                a.reload();
            }
        }
    }
}