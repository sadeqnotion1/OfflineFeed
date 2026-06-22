import QtQuick
import QtQuick.Layouts
import "../themes"

// Frameless custom title bar (issues #3, #4, #8):
//  - shows logo.svg + app name on the left
//  - SVG window controls (minimize / maximize / close), NO emoji
//  - drag-to-move + double-click maximize
//  - the day/night toggle has been MOVED to the Settings page (issue #8)
Rectangle {
    id: bar
    height: Theme.titleBarHeight
    color: Theme.panel

    // ---- Single source of truth for the window-control cluster ----------
    // ICON SIZE FIX: minimize / maximize / close ALL consume these tokens so
    // the close button can never drift from its siblings in icon size, hit-
    // area width or padding. windowIconSize binds to the shared Icon.Size
    // enum (Small = 18 -> the title-bar / window-controls tier) instead of a
    // bare magic number, keeping it on the one icon scale used app-wide.
    readonly property int windowIconSize: Icon.Size.Small   // 18px (title-bar tier)
    readonly property int windowButtonWidth: 46

    signal requestMinimize()
    signal requestToggleMaximize()
    signal requestClose()
    signal startSystemMove()

    Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.divider }

    // Drag area (whole bar except the buttons)
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton
        onPressed: bar.startSystemMove()
        onDoubleClicked: bar.requestToggleMaximize()
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 12
        spacing: 10
        LayoutMirroring.enabled: Theme.rtl

        Image {
            source: Qt.resolvedUrl("../assets/logo.svg")
            sourceSize.width: 48
            sourceSize.height: 48
            Layout.preferredWidth: 24
            Layout.preferredHeight: 24
            fillMode: Image.PreserveAspectFit
            smooth: true
        }
        Text {
            text: "OfflineFeed"
            color: Theme.text
            font.family: Theme.fontFamily
            font.pixelSize: 14
            font.bold: true
        }

        Item { Layout.fillWidth: true }

        // ---- Window controls (SVG, recolored, no emoji) ----
        WindowButton { iconName: "minimize"; onClicked: bar.requestMinimize() }
        WindowButton { iconName: "maximize"; onClicked: bar.requestToggleMaximize() }
        // R1.5: the WINDOW close control uses its own dedicated glyph
        // (window-close.svg) so it is visually distinct from the in-app `close`
        // icon used elsewhere (e.g. dialogs, search field).
        WindowButton { iconName: "window-close"; hoverColor: "#e0565b"; onClicked: bar.requestClose() }
    }

    component WindowButton: Rectangle {
        property string iconName: ""
        property color hoverColor: Theme.hover
        signal clicked()
        // Consume the bar-level tokens so all three controls share one width
        // and one icon size (the close button included).
        Layout.preferredWidth: bar.windowButtonWidth
        Layout.fillHeight: true
        color: hover.containsMouse ? hoverColor : "transparent"
        Behavior on color { ColorAnimation { duration: Theme.animFast } }
        Icon {
            anchors.centerIn: parent
            name: parent.iconName
            size: bar.windowIconSize
            // R1.5: keep the white-on-hover treatment for the window close glyph.
            color: ((parent.iconName === "close" || parent.iconName === "window-close") && hover.containsMouse) ? "#ffffff" : Theme.textSecondary
        }
        MouseArea {
            id: hover
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: parent.clicked()
        }
    }
}
