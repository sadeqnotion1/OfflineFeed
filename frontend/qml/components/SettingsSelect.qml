import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

// Labelled dropdown. `options` is an array of { value, label } objects.
// The closed box has a FIXED compact width so long labels (e.g. font names)
// never stretch it; the open list can be wider and shows a live search box
// when the option list is long.
Rectangle {
    id: ctl

    property string label: ""
    property var options: []
    property string value: ""

    // Fixed closed-box width (compact + consistent across every dropdown).
    property int comboWidth: 200
    // Open-list width (independent of the closed box, so long names fit).
    property int popupWidth: 300

    // Show the in-popup search box once the list gets long.
    property int searchThreshold: 8
    readonly property bool searchable: options.length > searchThreshold

    signal activatedValue(string value)

    width: parent ? parent.width : 400
    height: 56
    color: Theme.panel

    function indexOfValue(v) {
        for (var i = 0; i < options.length; i++)
            if (options[i].value === v) return i
        return -1
    }

    function filteredOptions(q) {
        if (!q || q.length === 0) return options
        var ql = q.toLowerCase()
        var out = []
        for (var i = 0; i < options.length; i++) {
            var lbl = (options[i] && options[i].label !== undefined) ? String(options[i].label) : ""
            if (lbl.toLowerCase().indexOf(ql) !== -1) out.push(options[i])
        }
        return out
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
            // FIXED width  no longer grows with content.
            Layout.preferredWidth: ctl.comboWidth
            Layout.maximumWidth: ctl.comboWidth
            Layout.alignment: Qt.AlignVCenter
            model: ctl.options
            textRole: "label"
            valueRole: "value"
            currentIndex: ctl.indexOfValue(ctl.value)
            font.family: Theme.fontFamily
            font.pixelSize: 14

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
                border.color: combo.activeFocus || comboPopup.visible ? Theme.accent : Theme.divider
            }

            indicator: Icon {
                name: "chevron"
                size: 14
                rotation: 90
                color: Theme.textSecondary
                x: Theme.rtl ? 8 : combo.width - width - 8
                y: (combo.height - height) / 2
            }

            popup: Popup {
                id: comboPopup
                // Align the (wider) list to the box, kept on-screen for RTL.
                x: Theme.rtl ? (combo.width - width) : 0
                y: combo.height + 2
                width: Math.max(combo.width, ctl.popupWidth)
                height: Math.min(
                    320,
                    (ctl.searchable ? 40 : 0) + Math.max(filtList.count, 1) * 36 + 12)
                padding: 6

                onOpened: { searchField.text = ""; if (ctl.searchable) searchField.forceActiveFocus() }
                onClosed: searchField.text = ""

                background: Rectangle { radius: 8; color: Theme.panel; border.width: 1; border.color: Theme.divider }

                contentItem: ColumnLayout {
                    spacing: 6

                    Rectangle {
                        visible: ctl.searchable
                        Layout.fillWidth: true
                        Layout.preferredHeight: visible ? 34 : 0
                        radius: 6
                        color: Theme.bg
                        border.width: 1
                        border.color: searchField.activeFocus ? Theme.accent : Theme.divider
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 8; anchors.rightMargin: 8
                            spacing: 6
                            LayoutMirroring.enabled: Theme.rtl
                            Icon { name: "search"; size: 14; color: Theme.textSecondary }
                            TextField {
                                id: searchField
                                Layout.fillWidth: true
                                placeholderText: qsTr("Search\u2026")
                                color: Theme.text
                                font.family: Theme.fontFamily
                                font.pixelSize: 14
                                background: null
                                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                            }
                        }
                    }

                    ListView {
                        id: filtList
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: ctl.filteredOptions(searchField.text)
                        ScrollBar.vertical: ScrollBar {}

                        delegate: ItemDelegate {
                            id: deleg
                            required property var modelData
                            width: filtList.width
                            height: 36
                            highlighted: modelData.value === ctl.value
                            contentItem: Text {
                                text: modelData.label
                                color: Theme.text
                                font.family: Theme.fontFamily
                                font.pixelSize: 14
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                                elide: Text.ElideRight
                            }
                            background: Rectangle { radius: 6; color: deleg.highlighted ? Theme.hover : "transparent" }
                            onClicked: { ctl.activatedValue(modelData.value); comboPopup.close() }
                        }
                    }
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
