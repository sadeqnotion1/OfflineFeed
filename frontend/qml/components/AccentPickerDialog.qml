import QtQuick
import QtQuick.Controls
import "../themes"

// Telegram-style "Choose accent color" picker.
//   - a saturation x value color map (drag the ring)
//   - a rainbow hue slider
//   - live H/S/L + R/G/B readouts and an editable hex field
//   - a live preview chip and Cancel / Save
//
// On Save it emits accepted(hex). AppearancePage wires that to
// `bridge.accentOverride = hex`, which the Theme singleton ALREADY consumes to
// re-tint the entire UI (accent, selection, hover, bubbles, dark surfaces).
// So this adds a real, arbitrary color picker with ZERO backend changes.
Popup {
    id: dlg

    // ---- HSV working state (the map is the canonical saturation x value square) ----
    property real hue: 0.58      // 0..1
    property real sat: 0.5       // 0..1  (HSV saturation -> map X)
    property real val: 0.85      // 0..1  (HSV value      -> map Y, inverted)
    readonly property color current: Qt.hsva(hue, sat, val, 1)
    property color _scratch: "#000000"   // string->color coercion helper (for hex parsing)

    signal accepted(string hex)

    function _h2(x) { var s = Math.round(x * 255).toString(16); return s.length < 2 ? "0" + s : s }
    function toHex(c) { return "#" + _h2(c.r) + _h2(c.g) + _h2(c.b) }
    function _clamp(v) { return v < 0 ? 0 : (v > 1 ? 1 : v) }

    function _applyColor(c) {
        if (c.hsvHue >= 0) dlg.hue = c.hsvHue   // keep prior hue for grays (hsvHue == -1)
        dlg.sat = c.hsvSaturation
        dlg.val = c.hsvValue
    }

    // Open preloaded from an existing hex (falls back to the live theme accent).
    function openWith(hex) {
        if (hex && /^#?[0-9a-fA-F]{6}$/.test(hex))
            dlg._scratch = (hex.charAt(0) === "#" ? hex : "#" + hex)
        else
            dlg._scratch = Theme.accent
        dlg._applyColor(dlg._scratch)
        hexField.text = dlg.toHex(dlg.current)
        dlg.open()
    }

    modal: true
    focus: true
    anchors.centerIn: Overlay.overlay
    width: 360
    padding: 0
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    background: Rectangle { radius: Theme.radius.lg; color: Theme.panel; border.width: 1; border.color: Theme.divider }

    contentItem: Column {
        spacing: 0

        // ---- Header ----
        Item {
            width: parent.width; height: 50
            Text {
                anchors.left: parent.left; anchors.leftMargin: 16; anchors.verticalCenter: parent.verticalCenter
                text: qsTr("Choose accent color")
                color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 16; font.bold: true
            }
            Icon {
                anchors.right: parent.right; anchors.rightMargin: 14; anchors.verticalCenter: parent.verticalCenter
                name: "close"; size: 16; color: Theme.textSecondary
                MouseArea { anchors.fill: parent; anchors.margins: -6; cursorShape: Qt.PointingHandCursor; onClicked: dlg.close() }
            }
        }
        Rectangle { width: parent.width; height: 1; color: Theme.divider }

        // ---- Body ----
        Column {
            width: parent.width
            topPadding: 14; bottomPadding: 8
            spacing: 12

            // Saturation / value map
            Item {
                x: 16
                width: parent.width - 32
                height: 168
                Rectangle {
                    id: satLayer
                    anchors.fill: parent
                    radius: Theme.radius.md
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: "#ffffff" }
                        GradientStop { position: 1.0; color: Qt.hsva(dlg.hue, 1, 1, 1) }
                    }
                }
                Rectangle {
                    anchors.fill: parent
                    radius: Theme.radius.md
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: "#00000000" }
                        GradientStop { position: 1.0; color: "#ff000000" }
                    }
                }
                // Drag ring
                Rectangle {
                    width: 16; height: 16; radius: 8
                    color: "transparent"
                    border.width: 2; border.color: "#ffffff"
                    x: dlg._clamp(dlg.sat) * parent.width - width / 2
                    y: (1 - dlg._clamp(dlg.val)) * parent.height - height / 2
                    Rectangle { anchors.fill: parent; anchors.margins: 2; radius: 6; color: "transparent"; border.width: 1; border.color: "#80000000" }
                }
                MouseArea {
                    id: mapArea
                    anchors.fill: parent
                    cursorShape: Qt.CrossCursor
                    function _pick() {
                        dlg.sat = dlg._clamp(mouseX / width)
                        dlg.val = dlg._clamp(1 - mouseY / height)
                        hexField.text = dlg.toHex(dlg.current)
                    }
                    onPressed: _pick()
                    onPositionChanged: if (pressed) _pick()
                }
            }

            // Hue slider
            Item {
                x: 16
                width: parent.width - 32
                height: 16
                Rectangle {
                    anchors.fill: parent
                    radius: Theme.radius.pill
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.000; color: "#ff0000" }
                        GradientStop { position: 0.167; color: "#ffff00" }
                        GradientStop { position: 0.333; color: "#00ff00" }
                        GradientStop { position: 0.500; color: "#00ffff" }
                        GradientStop { position: 0.667; color: "#0000ff" }
                        GradientStop { position: 0.833; color: "#ff00ff" }
                        GradientStop { position: 1.000; color: "#ff0000" }
                    }
                }
                Rectangle {
                    width: 6; height: parent.height + 6; radius: 3
                    color: "#ffffff"; border.width: 1; border.color: "#40000000"
                    y: -3
                    x: dlg._clamp(dlg.hue) * parent.width - width / 2
                }
                MouseArea {
                    id: hueArea
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    function _pick() {
                        dlg.hue = dlg._clamp(mouseX / width)
                        hexField.text = dlg.toHex(dlg.current)
                    }
                    onPressed: _pick()
                    onPositionChanged: if (pressed) _pick()
                }
            }

            // Preview chip + hex field
            Row {
                x: 16
                width: parent.width - 32
                spacing: 12
                LayoutMirroring.enabled: Theme.rtl
                Rectangle {
                    anchors.verticalCenter: parent.verticalCenter
                    width: 40; height: 40; radius: Theme.radius.md
                    color: dlg.current
                    border.width: 1; border.color: Theme.divider
                }
                Rectangle {
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width - 52; height: 40; radius: Theme.radius.md
                    color: Theme.bg
                    border.width: 1; border.color: hexField.activeFocus ? Theme.accent : Theme.divider
                    Behavior on border.color { ColorAnimation { duration: Theme.animFast } }
                    Row {
                        anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12; spacing: 4
                        LayoutMirroring.enabled: Theme.rtl
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: "#"; color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 15
                        }
                        TextField {
                            id: hexField
                            anchors.verticalCenter: parent.verticalCenter
                            width: parent.width - 20
                            text: dlg.toHex(dlg.current)
                            color: Theme.text; selectionColor: Theme.accent; selectedTextColor: Theme.accentText
                            font.family: Theme.fontFamily; font.pixelSize: 15
                            background: null
                            inputMethodHints: Qt.ImhPreferLatin
                            horizontalAlignment: Theme.rtl ? TextInput.AlignRight : TextInput.AlignLeft
                            onEditingFinished: {
                                var t = text.charAt(0) === "#" ? text : "#" + text
                                if (/^#[0-9a-fA-F]{6}$/.test(t)) { dlg._scratch = t; dlg._applyColor(dlg._scratch) }
                                text = dlg.toHex(dlg.current)
                            }
                        }
                    }
                }
            }

            // H / S / L  +  R / G / B readouts
            Row {
                x: 16
                width: parent.width - 32
                spacing: 8
                Repeater {
                    model: [
                        { k: "H", v: Math.max(0, Math.round((dlg.current.hslHue < 0 ? 0 : dlg.current.hslHue) * 360)) },
                        { k: "S", v: Math.round(dlg.current.hslSaturation * 100) },
                        { k: "L", v: Math.round(dlg.current.hslLightness * 100) },
                        { k: "R", v: Math.round(dlg.current.r * 255) },
                        { k: "G", v: Math.round(dlg.current.g * 255) },
                        { k: "B", v: Math.round(dlg.current.b * 255) }
                    ]
                    delegate: Rectangle {
                        required property var modelData
                        width: (parent.width - 5 * 8) / 6
                        height: 38
                        radius: Theme.radius.sm
                        color: Theme.bg
                        border.width: 1; border.color: Theme.divider
                        Column {
                            anchors.centerIn: parent
                            spacing: 0
                            Text { anchors.horizontalCenter: parent.horizontalCenter; text: modelData.k; color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 10 }
                            Text { anchors.horizontalCenter: parent.horizontalCenter; text: modelData.v; color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true }
                        }
                    }
                }
            }
        }

        Rectangle { width: parent.width; height: 1; color: Theme.divider }

        // ---- Footer ----
        Item {
            width: parent.width; height: 56
            Row {
                anchors.right: parent.right; anchors.rightMargin: 16; anchors.verticalCenter: parent.verticalCenter
                spacing: 10
                LayoutMirroring.enabled: Theme.rtl
                Rectangle {
                    width: 88; height: 34; radius: Theme.radius.sm
                    color: cancelMouse.containsMouse ? Theme.hover : "transparent"
                    Behavior on color { ColorAnimation { duration: Theme.animFast } }
                    Text { anchors.centerIn: parent; text: qsTr("Cancel"); color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 14 }
                    MouseArea { id: cancelMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: dlg.close() }
                }
                Rectangle {
                    width: 88; height: 34; radius: Theme.radius.sm
                    color: saveMouse.containsMouse ? Theme.accentHover : Theme.accent
                    Behavior on color { ColorAnimation { duration: Theme.animFast } }
                    Text { anchors.centerIn: parent; text: qsTr("Save"); color: Theme.accentText; font.family: Theme.fontFamily; font.pixelSize: 14; font.bold: true }
                    MouseArea {
                        id: saveMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                        onClicked: { dlg.accepted(dlg.toHex(dlg.current)); dlg.close() }
                    }
                }
            }
        }
    }
}
