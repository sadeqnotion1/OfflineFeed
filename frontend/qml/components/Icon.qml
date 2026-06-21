import QtQuick
import Qt5Compat.GraphicalEffects
import "../themes"

// Recolorable, SIZE- and TINT-standardized SVG icon.
//
//   Icon { name: "search" }                            // Inherit color (= Theme.text), Medium (22)
//   Icon { name: "search"; size: Icon.Size.Large }     // 26
//   Icon { name: "settings"; tint: Icon.Tint.Default }  // resting -> Theme.textSecondary
//   Icon { name: "settings"; tint: Icon.Tint.Active }   // active/selected -> Theme.accent
//   Icon { name: "trash";    tint: Icon.Tint.Disabled } // Theme.textSecondary @ low alpha
//   Icon { name: "close";    color: "#ffffff" }         // explicit color still wins (legacy)
//
// Resolves `name` -> ../assets/icons/<name>.svg and tints it via ColorOverlay.
// If the file is missing it shows a visible fallback box + warns (no crash).
//
// BACKWARD COMPATIBLE: `tint` defaults to Inherit, so every existing call that
// sets `color:` (or relies on the old default) behaves exactly as before.
Item {
    id: root

    // --- Standard sizes (single source of truth) ---------------------------
    // Bind to these so rails, headers and toolbars share one icon scale.
    //   Small  18  -> title-bar / window controls / inline
    //   Medium 22  -> header & toolbar action icons
    //   Large  26  -> primary navigation rail
    enum Size { Small = 18, Medium = 22, Large = 26 }

    // --- Tint roles (systematic active / inactive / disabled tinting) ------
    //   Inherit  -> use the explicit `color` below (legacy / one-off). DEFAULT.
    //   Default  -> Theme.textSecondary           (resting state)
    //   Active   -> Theme.accent                  (active / selected ONLY)
    //   Disabled -> Theme.textSecondary @ low alpha
    enum Tint { Inherit, Default, Active, Disabled }

    property string name: ""
    property int size: Icon.Size.Medium
    property int tint: Icon.Tint.Inherit

    // Explicit color, used only when tint === Inherit. Kept for back-compat and
    // one-off colors (e.g. the close button's white-on-hover).
    property color color: Theme.text

    // Alpha applied to the Disabled role.
    property real disabledOpacity: 0.4

    // Resolved tint color for the current role (the single tint pipeline).
    readonly property color _roleColor: {
        switch (tint) {
        case Icon.Tint.Active:
            return Theme.accent
        case Icon.Tint.Disabled:
            return Qt.rgba(Theme.textSecondary.r, Theme.textSecondary.g,
                           Theme.textSecondary.b, root.disabledOpacity)
        case Icon.Tint.Default:
            return Theme.textSecondary
        default: // Inherit
            return root.color
        }
    }

    implicitWidth: size
    implicitHeight: size
    width: size
    height: size

    Image {
        id: img
        anchors.fill: parent
        // Qt.resolvedUrl keeps paths relative to THIS file regardless of caller.
        source: root.name ? Qt.resolvedUrl("../assets/icons/" + root.name + ".svg") : ""
        sourceSize.width: root.size * 2
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
        color: root._roleColor
        antialiasing: true
        visible: img.status === Image.Ready
        // Animate active-state tint changes (Default <-> Active) so selection
        // feels smooth instead of snapping. 120ms OutCubic per the icon spec.
        Behavior on color {
            ColorAnimation { duration: 120; easing.type: Easing.OutCubic }
        }
    }

    // Graceful fallback glyph when the SVG can't load.
    Rectangle {
        anchors.fill: parent
        radius: Theme.radius.sm
        color: "transparent"
        border.width: 1
        border.color: root._roleColor
        visible: img.status === Image.Error
        Text {
            anchors.centerIn: parent
            text: "?"
            color: root._roleColor
            font.pixelSize: Math.max(8, Math.round(root.size * 0.6))
        }
    }
}
