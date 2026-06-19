import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

// Labelled slider with a live value readout. For interface scale set suffix="%"
// (value 1.0 reads as 100%).
Rectangle {
    id: ctl

    property string label: ""
    property real from: 0.8
    property real to: 1.4
    property real stepSize: 0.05
    property real value: 1.0
    property string suffix: ""

    signal moved(real value)

    width: parent ? parent.width : 400
    height: 66
    color: Theme.panel

    Column {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        anchors.topMargin: 10
        spacing: 4

        RowLayout {
            width: parent.width
            LayoutMirroring.enabled: Theme.rtl
            Text {
                Layout.fillWidth: true
                text: ctl.label
                color: Theme.text
                font.family: Theme.fontFamily
                font.pixelSize: 15
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Text {
                text: Math.round(slider.value * (ctl.suffix === "%" ? 100 : 1)) + ctl.suffix
                color: Theme.accent
                font.family: Theme.fontFamily
                font.pixelSize: 14
                font.bold: true
            }
        }

        Slider {
            id: slider
            width: parent.width
            from: ctl.from
            to: ctl.to
            stepSize: ctl.stepSize
            value: ctl.value
            onMoved: ctl.moved(value)

            background: Rectangle {
                x: slider.leftPadding
                y: slider.topPadding + slider.availableHeight / 2 - height / 2
                width: slider.availableWidth
                height: 4
                radius: Theme.radius.pill
                color: Theme.divider
                Rectangle {
                    width: slider.visualPosition * parent.width
                    height: parent.height
                    radius: Theme.radius.pill
                    color: Theme.accent
                    x: Theme.rtl ? parent.width - width : 0
                }
            }

            handle: Rectangle {
                x: slider.leftPadding + slider.visualPosition * (slider.availableWidth - width)
                y: slider.topPadding + slider.availableHeight / 2 - height / 2
                width: 18
                height: 18
                radius: Theme.radius.pill
                color: Theme.accent
                border.width: 2
                border.color: Theme.accentText
            }
        }
    }
}
