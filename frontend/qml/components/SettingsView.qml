import QtQuick
import QtQuick.Controls
import "../themes"

// Master -> detail Settings flow. A StackView holds the root section list and
// pushes one dedicated page per section (each page gets its own SVG icon + own
// screen, with a back button in its header). Loaded by Main.qml in place of the
// old single SettingsPage whenever bridge.activeTab === "settings".
Item {
    id: settingsView
    anchors.fill: parent

    // ----- Section registry (id, label, icon, detail page) -----
    // icon = a white-stroke SVG in qml/assets/icons recolored at runtime by Icon.qml.
    property var sections: [
        { sid: "account",       label: qsTr("Account"),               icon: "user",    page: "AccountPage.qml" },
        { sid: "notifications", label: qsTr("Notifications & Sounds"), icon: "bell",    page: "NotificationsPage.qml" },
        { sid: "privacy",       label: qsTr("Privacy & Security"),     icon: "shield",  page: "PrivacyPage.qml" },
        { sid: "feed",          label: qsTr("Feed & Chat Settings"),   icon: "chat",    page: "FeedPage.qml" },
        { sid: "sources",      label: qsTr("News Sources"),           icon: "external", page: "SourcesPage.qml" },
        { sid: "folders",       label: qsTr("Folders"),                icon: "folder",  page: "FoldersPage.qml" },
        { sid: "advanced",      label: qsTr("Advanced"),               icon: "wrench",  page: "AdvancedPage.qml" },
        { sid: "appearance",    label: qsTr("Appearance"),             icon: "palette", page: "AppearancePage.qml" },
        { sid: "language",      label: qsTr("Language"),               icon: "globe",   page: "LanguagePage.qml" },
        { sid: "help",          label: qsTr("Help"),                   icon: "help",    page: "HelpPage.qml" }
    ]

    StackView {
        id: stack
        anchors.fill: parent
        initialItem: rootPage

        pushEnter: Transition { NumberAnimation { property: "x"; from: stack.width;  to: 0; duration: Theme.anim; easing.type: Theme.easing } }
        pushExit:  Transition { NumberAnimation { property: "x"; from: 0; to: -stack.width * 0.3; duration: Theme.anim; easing.type: Theme.easing } }
        popEnter:  Transition { NumberAnimation { property: "x"; from: -stack.width * 0.3; to: 0; duration: Theme.anim; easing.type: Theme.easing } }
        popExit:   Transition { NumberAnimation { property: "x"; from: 0; to: stack.width; duration: Theme.anim; easing.type: Theme.easing } }
    }

    // ----- Root section list -----
    Component {
        id: rootPage
        Item {
            anchors.fill: parent

            Rectangle {
                id: rootHeader
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: Theme.headerHeight
                color: Theme.panel
                Text {
                    anchors.fill: parent
                    anchors.leftMargin: 20
                    anchors.rightMargin: 20
                    verticalAlignment: Text.AlignVCenter
                    text: qsTr("Settings")
                    color: Theme.text
                    font.family: Theme.fontFamily
                    font.pixelSize: 20
                    font.bold: true
                    horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                }
                Rectangle {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: 1
                    color: Theme.divider
                }
            }

            ListView {
                anchors.top: rootHeader.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                clip: true
                model: settingsView.sections
                boundsBehavior: Flickable.StopAtBounds
                delegate: SettingsRow {
                    required property var modelData
                    width: ListView.view.width
                    iconName: modelData.icon
                    label: modelData.label
                    showChevron: true
                    onClicked: stack.push(Qt.resolvedUrl(modelData.page), { "stack": stack })
                }
            }
        }
    }
}
