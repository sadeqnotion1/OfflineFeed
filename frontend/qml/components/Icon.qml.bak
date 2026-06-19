import QtQuick
import Qt5Compat.GraphicalEffects
import "../themes"

// Recolorable SVG icon.
//   Icon { name: "twitter-x"; color: Theme.textSecondary; size: 18 }
// Resolves `name` -> ../assets/icons/<name>.svg and tints it via ColorOverlay.
// If the file is missing it shows a visible fallback box + warns (no crash).
Item {
    id: root
    property string name: ""
    property color color: Theme.text
    property int size: 22

    implicitWidth: size
    implicitHeight: size
    width: size
    height: size

    Image {
        id: img
        anchors.fill: parent
        // Use Qt.resolvedUrl to ensure paths resolve relative to this QML file correctly.
        source: root.name ? Qt.resolvedUrl("../assets/icons/" + root.name + ".svg") : ""
        sourceSize.width: root.size * 2
        sourceSize.height: root.size * 2
        fillMode: Image.PreserveAspectFit
        smooth: true
        antialiasing: true
        visible: false
        cache: true
        onStatusChanged: {
            if (status === Image.Error)
                console.warn("[Icon] missing icon '" + root.name +
                             "' -> ../assets/icons/" + root.name + ".svg")
        }
    }

    ColorOverlay {
        anchors.fill: img
        source: img
        color: root.color
        antialiasing: true
        visible: img.status === Image.Ready
    }

    // Graceful fallback glyph when the SVG can't load.
    Rectangle {
        anchors.fill: parent
        radius: 3
        color: "transparent"
        border.width: 1
        border.color: root.color
        visible: img.status === Image.Error
        Text {
            anchors.centerIn: parent
            text: "?"
            color: root.color
            font.pixelSize: Math.max(8, Math.round(root.size * 0.6))
        }
    }
}
