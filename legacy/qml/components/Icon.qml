import QtQuick
import Qt5Compat.GraphicalEffects
import "../themes"

// A crisp, recolorable SVG line icon.
// Renders the white-stroke source SVG into an offscreen Image, then tints it
// with ColorOverlay so any theme color can be applied. sourceSize is set so
// the SVG rasterizes sharply at the requested pixel size (no blank icons).
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
        id: src
        anchors.fill: parent
        // Qt.resolvedUrl makes the relative path robust regardless of CWD.
        source: root.name ? Qt.resolvedUrl("../assets/icons/" + root.name + ".svg") : ""
        sourceSize.width: root.size * 2
        sourceSize.height: root.size * 2
        fillMode: Image.PreserveAspectFit
        smooth: true
        antialiasing: true
        visible: false
        cache: true
    }

    ColorOverlay {
        anchors.fill: src
        source: src
        color: root.color
        antialiasing: true
        visible: src.status === Image.Ready
    }
}
