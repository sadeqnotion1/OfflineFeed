import QtQuick
import QtQuick.Controls
import "../themes"

// ─────────────────────────────────────────────────────────────────────────
//  AppButton — the shared, theme-driven action button for OfflineFeed.
//
//  Variants:
//    "primary"  accent-filled pill   -> the main affirmative action
//    "subtle"   quiet panel-tinted   -> secondary / low-emphasis action
//    "icon"     borderless square    -> toolbar / header icon action
//
//  Everything is derived from Theme tokens (accent pipeline, radius scale,
//  fonts, timings) so a custom accent recolors it automatically and it never
//  introduces a one-off bright hex. Hover / pressed are animated 120ms OutCubic.
//
//  Usage:
//    AppButton { variant: "primary"; iconName: "send"; label: qsTr("Send");
//                onClicked: doThing() }
//    AppButton { variant: "subtle";  label: qsTr("Cancel"); onClicked: ... }
//    AppButton { variant: "icon";    iconName: "search";   onClicked: ... }
// ─────────────────────────────────────────────────────────────────────────
Item {
    id: ctl

    // ----- Public API -----
    property string variant: "primary"            // "primary" | "subtle" | "icon"
    property string label: ""                      // text (ignored for "icon")
    property string iconName: ""                   // optional leading / icon-only glyph
    property bool bold: false                      // restrained by default (no shouty bold)
    property bool active: true                      // soft-disable without breaking layout
    property int controlHeight: 34                  // ~32-36 comfortable touch target
    property int iconSize: variant === "icon" ? 20 : 16
    signal clicked()

    readonly property bool isIcon: variant === "icon"
    readonly property int hPad: 14                  // comfortable horizontal padding

    // ----- Sizing (intrinsic; plays nicely inside Layouts) -----
    implicitHeight: controlHeight
    implicitWidth: isIcon ? controlHeight
                          : Math.round(contentRow.implicitWidth + hPad * 2)
    width: implicitWidth
    height: implicitHeight

    // ----- Fill per variant (single accent pipeline; no one-off reds) -----
    function _baseColor() {
        if (isIcon) return "transparent"
        if (variant === "subtle") return Theme.panelAlt
        return Theme.accent                         // primary: standard accent token
    }
    function _hoverColor() {
        if (isIcon) return Theme.hoverFill
        if (variant === "subtle") return Theme.hover
        return Theme.accentHover                    // derived, not an arbitrary brighter red
    }
    function _pressColor() {
        if (isIcon) return Theme.selectionFill
        if (variant === "subtle") return Theme.selection
        return Theme.accentPressed
    }

    readonly property color _fill: !ctl.active   ? Theme.panelAlt
                                   : mouse.pressed       ? _pressColor()
                                   : mouse.containsMouse ? _hoverColor()
                                   :                       _baseColor()

    // Contrast-safe foreground for each variant / state.
    readonly property color _fg: !ctl.active ? Theme.textSecondary
                                 : variant === "primary" ? Theme.accentText
                                 : (mouse.containsMouse || mouse.pressed) ? Theme.accent
                                 :                                          Theme.textSecondary

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: ctl.isIcon ? Theme.radius.md : Theme.radius.pill
        color: ctl._fill
        antialiasing: true
        opacity: ctl.active ? 1.0 : 0.6
        Behavior on color { ColorAnimation { duration: 120; easing.type: Easing.OutCubic } }

        Row {
            id: contentRow
            anchors.centerIn: parent
            // Positioners skip invisible children, so spacing collapses cleanly
            // for icon-only or label-only buttons.
            spacing: (ctl.label !== "" && ctl.iconName !== "") ? 8 : 0

            Icon {
                visible: ctl.iconName !== ""
                anchors.verticalCenter: parent.verticalCenter
                name: ctl.iconName
                size: ctl.iconSize
                color: ctl._fg
            }
            Text {
                visible: !ctl.isIcon && ctl.label !== ""
                anchors.verticalCenter: parent.verticalCenter
                text: ctl.label
                color: ctl._fg
                font.family: Theme.fontFamily
                font.pixelSize: 14
                font.bold: ctl.bold
            }
        }
    }

    // Cheap, smooth press feedback (transform/opacity only).
    scale: (mouse.pressed && ctl.active) ? 0.97 : 1.0
    Behavior on scale { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        enabled: ctl.active
        cursorShape: Qt.PointingHandCursor
        onClicked: ctl.clicked()
    }
}
