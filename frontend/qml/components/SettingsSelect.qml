import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

// Labelled dropdown. `options` is an array of { value, label } objects.
// Content-aware width (min/max clamp). The popup uses a fixed compact row
// height and a hard height cap so long lists (e.g. the full system-font list)
// never overflow the page, and it shows a live search/filter box when the
// option list is long.
Rectangle {
    id: ctl

    property string label: ""
    property var options: []
    property string value: ""

    // Width tunables (kept local so no other component is affected).
    property int minComboWidth: 200
    property int maxComboWidth: 360

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

    // Live filter used by the popup list.
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

    // Measure the widest label so the closed box fits its content.
    TextMetrics {
        id: optMetrics
        font.family: Theme.fontFamily
        font.pixelSize: 14
    }
    function longestOptionWidth() {
        // Performance guard: if there are many options (e.g. font lists), measuring them all
        // synchronously using TextMetrics layout/font queries freezes the GUI thread.
        // We bypass the loop and return a safe maximum width.
        if (options.length > 30) {
            return maxComboWidth - 72
        }
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
            Layout.minimumWidth: ctl.minComboWidth
            Layout.preferredWidth: {
                var _count = ctl.options.length   // re-evaluate when options change
                var _font = Theme.fontFamily      // re-evaluate when the UI font changes
                return Math.min(ctl.maxComboWidth, Math.max(ctl.minComboWidth, ctl.longestOptionWidth() + 72))
            }
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

            // Custom popup: optional search box + compact, height-capped list.
            popup: Popup {
                id: comboPopup
                y: combo.height + 2
                x: Theme.rtl ? (combo.width - width) : 0
                width: Math.max(combo.width, 240)
                // Size to content (search + rows), capped so it never overflows.
                height: Math.min(
                    320,
                    (ctl.searchable ? 40 : 0) + Math.max(filtList.count, 1) * 36 + 12)
                padding: 6

                onOpened: {
                    searchField.text = ""
                    if (ctl.searchable) searchField.forceActiveFocus()
                }
                onClosed: searchField.text = ""

                background: Rectangle {
                    radius: 8
                    color: Theme.panel
                    border.width: 1
                    border.color: Theme.divider
                }

                contentItem: ColumnLayout {
                    spacing: 6

                    Rectangle {
                        id: searchBox
                        visible: ctl.searchable
                        Layout.fillWidth: true
                        Layout.preferredHeight: visible ? 34 : 0
                        radius: 6
                        color: Theme.bg
                        border.width: 1
                        border.color: searchField.activeFocus ? Theme.accent : Theme.divider
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 8
                            anchors.rightMargin: 8
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
                            background: Rectangle {
                                radius: 6
                                color: deleg.highlighted ? Theme.hover : "transparent"
                            }
                            onClicked: {
                                ctl.activatedValue(modelData.value)
                                comboPopup.close()
                            }
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
