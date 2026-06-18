import QtQuick
import "../themes"

// Per-peer gradient avatar. If avatarPath points to a real image it is shown,
// otherwise a deterministic Telegram-style 2-stop gradient with initials is
// drawn. Special keys "bookmark" and "logs" render the corresponding icon.
Item {
    id: root
    property string name: ""
    property string avatarPath: ""
    property int size: Theme.avatarSize
    property string seed: name

    implicitWidth: size
    implicitHeight: size
    width: size
    height: size

    readonly property bool isImage: avatarPath !== ""
                                    && avatarPath !== "bookmark"
                                    && avatarPath !== "logs"
    readonly property var grad: Theme.gradientFor(seed)

    function initials(n) {
        if (!n) return "#";
        var parts = n.trim().split(/\s+/);
        if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
        return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
    }

    // Gradient disc (also the fallback when an avatar image fails to load)
    Rectangle {
        id: disc
        anchors.fill: parent
        radius: width / 2
        visible: !root.isImage || avatarImg.status !== Image.Ready
        gradient: Gradient {
            orientation: Gradient.Vertical
            GradientStop { position: 0.0; color: root.grad[0] }
            GradientStop { position: 1.0; color: root.grad[1] }
        }

        Text {
            anchors.centerIn: parent
            visible: root.avatarPath !== "bookmark" && root.avatarPath !== "logs"
            text: root.initials(root.name)
            color: "#ffffff"
            font.family: Theme.fontFamily
            font.pixelSize: Math.round(root.size * 0.4)
            font.bold: true
        }

        Icon {
            anchors.centerIn: parent
            visible: root.avatarPath === "bookmark" || root.avatarPath === "logs"
            name: root.avatarPath === "bookmark" ? "bookmark" : "logs"
            color: "#ffffff"
            size: root.size * 0.5
        }
    }

    // Real image avatar, clipped to a circle
    Rectangle {
        anchors.fill: parent
        radius: width / 2
        visible: root.isImage && avatarImg.status === Image.Ready
        clip: true
        color: "transparent"
        Image {
            id: avatarImg
            anchors.fill: parent
            source: root.isImage ? root.avatarPath : ""
            fillMode: Image.PreserveAspectCrop
            smooth: true
            asynchronous: true
            cache: true
            // QML can't directly mask; the parent radius + clip approximates a
            // circular crop well enough for square source images.
        }
    }
}
