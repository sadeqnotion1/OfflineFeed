import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

// Labelled dropdown. `options` is an array of { value, label } objects.
// D6: width is content-aware. The combo measures its widest option label with a
// hidden TextMetrics and sizes itself between a sensible MIN and MAX so every
// dropdown renders as a proper, readable box instead of a thin 170px sliver.
// This single shared component fixes dropdown width app-wide.
Rectangle {
    id: ctl

    property string label: ""
    property var options: []
    property string value: ""

    // D6: tunables (kept local so no other component is affected).
    property int minComboWidth: 200
    property int maxComboWidth: 360

    signal activatedValue(string value)

    width: parent ? parent.width : 400
    height: 56
    color: Theme.panel

    function indexOfValue(v) {
        for (var i = 0; i < options.length; i++)
            if (options[i].value === v) return i
        return -1
    }

    // D6: measure the widest label so the box fits its content.
    TextMetrics {
        id: optMetrics
        font.family: Theme.fontFamily
        font.pixelSize: 14
    }
    function longestOptionWidth() {
        var w = 0
        for (var i = 0; i < options.length; i++) {
            optMetrics.text = (options[i] && options[i].label !== undefined) ? String(options[i].label) : ""
            if (optMetrics.width > w) w = optMetrics.width
        }
        return w
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 12
        spacing: 12
        LayoutMirroring.enabled: Theme.rtl

        Text {
            Layout.fillWidth: true
            text: ctl.label
            color: Theme.text
            font.family: Theme.fontFamily
            font.pixelSize: 15
            horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
        }

        ComboBox {
            id: combo
            // D6: content-fit width with min/max clamps (was a fixed 170).
            // +72 leaves room for left padding, the chevron indicator and breathing space.
            Layout.minimumWidth: ctl.minComboWidth
            Layout.preferredWidth: {
                var _count = ctl.options.length          // re-evaluate when options change
                var _font = Theme.fontFamily             // re-evaluate when the UI font changes
                return Math.min(ctl.maxComboWidth, Math.max(ctl.minComboWidth, ctl.longestOptionWidth() + 72))
            }
            Layout.alignment: Qt.AlignVCenter
            model: ctl.options
            textRole: "label"
            valueRole: "value"
            currentIndex: ctl.indexOfValue(ctl.value)
            font.family: Theme.fontFamily
            font.pixelSize: 14
            onActivated: {
                if (currentIndex >= 0 && currentIndex < ctl.options.length)
                    ctl.activatedValue(ctl.options[currentIndex].value)
            }

            contentItem: Text {
                leftPadding: 10
                rightPadding: 28
                text: combo.displayText
                color: Theme.text
                font: combo.font
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                elide: Text.ElideRight
            }

            background: Rectangle {
                radius: 6
                color: Theme.bg
                border.width: 1
                border.color: combo.activeFocus ? Theme.accent : Theme.divider
            }

            indicator: Icon {
                name: "chevron"
                size: 14
                rotation: 90
                color: Theme.textSecondary
                x: Theme.rtl ? 8 : combo.width - width - 8
                y: (combo.height - height) / 2
            }

            delegate: ItemDelegate {
                id: deleg
                required property var model
                required property int index
                width: combo.width
                highlighted: combo.highlightedIndex === index
                contentItem: Text {
                    text: deleg.model.label
                    color: Theme.text
                    font: combo.font
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                }
                background: Rectangle { color: deleg.highlighted ? Theme.hover : "transparent" }
            }

            popup: Popup {
                y: combo.height + 2
                width: combo.width
                implicitHeight: Math.min(listView.contentHeight + 2, 260)
                padding: 1
                background: Rectangle { radius: 8; color: Theme.panel; border.width: 1; border.color: Theme.divider }
                contentItem: ListView {
                    id: listView
                    clip: true
                    implicitHeight: contentHeight
                    model: combo.delegateModel
                    currentIndex: combo.highlightedIndex
                    ScrollIndicator.vertical: ScrollIndicator {}
                }
            }
        }
    }

    Rectangle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        color: Theme.divider
        opacity: 0.4
    }
}
