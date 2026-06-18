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
        implicitWidth: 240
        model: root.options
        font.family: Theme.fontFamily
    }
}
