import QtQuick
import QtQuick.Layouts
import "../themes"

// Horizontal pill row of reactions (emoji + count). Telegram uses small rounded
// chips that highlight when the current user has reacted.
Flow {
    id: root
    property var reactions: []
    property bool outgoing: false
    signal reacted(int index)

    spacing: 6
    visible: reactions && reactions.length > 0

    Repeater {
        model: root.reactions
        delegate: Rectangle {
            required property var modelData
            required property int index
            height: 26
            width: chip.implicitWidth + 18
            radius: Theme.radius.pill
            color: modelData.active
                   ? Theme.accent
                   : (root.outgoing ? Qt.lighter(Theme.outBubble, 1.25)
                                    : Qt.lighter(Theme.inBubble, 1.6))

            Behavior on color { ColorAnimation { duration: Theme.animFast } }

            RowLayout {
                id: chip
                anchors.centerIn: parent
                spacing: 4
                Text {
                    text: modelData.emoji
                    font.pixelSize: 13
                }
                Text {
                    text: modelData.count > 0 ? modelData.count : ""
                    color: modelData.active ? Theme.accentText : Theme.text
                    font.family: Theme.fontFamily
                    font.pixelSize: 12
                    font.bold: true
                }
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: root.reacted(index)
            }
        }
    }
}
