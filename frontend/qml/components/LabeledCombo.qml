import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../themes"

ColumnLayout {
    id: root
    property string label: ""
    property var options: []
    property alias currentIndex: comboBox.currentIndex
    property string value: comboBox.currentText
    spacing: 4
    Text { text: root.label; color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12 }
    ComboBox {
        id: comboBox
        Layout.fillWidth: true
        // Phase 2 - Task 1 (content-fit dropdowns):
        // Previously this used a hardcoded `implicitWidth: 240`, which clipped any
        // option label longer than 240px. WidestText makes the control's
        // implicitContentWidth track the LONGEST item, so the field sizes to its
        // content instead of a fixed width.
        implicitContentWidthPolicy: ComboBox.WidestText
        model: root.options
        font.family: Theme.fontFamily

        // Ensure the drop-down POPUP is at least as wide as the widest item, not
        // merely the (possibly narrower) field. Bind after creation so we don't
        // override the default popup styling.
        Component.onCompleted: popup.width = Qt.binding(function() {
            return Math.max(comboBox.width,
                            comboBox.implicitContentWidth + comboBox.leftPadding + comboBox.rightPadding)
        })
    }
}
