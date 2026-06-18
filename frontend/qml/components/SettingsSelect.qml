import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

// Labelled dropdown. `options` is an array of { value, label } objects.
Rectangle {
    id: ctl

    property string label: ""
    property var options: []
    property string value: ""

    signal activatedValue(string value)

    width: parent ? parent.width : 400
    height: 56
    color: Theme.panel

    function indexOfValue(v) {
        for (var i = 0; i < options.length; i++)
            if (options[i].value === v) return i
        return -1
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
            Layout.preferredWidth: 170
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
