// ~/.local/share/kwin/scripts/forceautorotation/contents/code/main.js

function forceRotation() {
    const outputs = workspace.outputs;

    for (let i = 0; i < outputs.length; i++) {
        let o = outputs[i];

        // genau hier wird die echte Runtime-Property gesetzt
        o.autoRotationPolicy = "always";
    }
}

// Warten bis KWin komplett ready ist
workspace.outputsChanged.connect(forceRotation);

// Fallback beim Start
forceRotation();