import QtQuick
import "../themes"

// Per-peer gradient avatar. If avatarPath points to a real image it is shown,
// otherwise a deterministic Telegram-style 2-stop gradient with initials is
// drawn.
//
// The special sentinel keys "bookmark" (Saved Messages), "archive" (Archived
// Messages), "logs" (System & App Logs) and "trash" (Bin) render a DEDICATED,
// STABLE tinted gradient + a centered glyph instead of a flat single-color
// circle or a random hash color. The disc is ALWAYS a 2-stop gradient, so no
// flat single-color avatar circles remain anywhere in the QML UI.
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

    // Sentinel keys that denote a SYSTEM icon-avatar (not a real image / peer).
    readonly property bool isSystem: avatarPath === "bookmark"
                                     || avatarPath === "logs"
                                     || avatarPath === "trash"
                                     || avatarPath === "archive"

    // A real image is anything that is set and is NOT one of the sentinels.
    readonly property bool isImage: avatarPath !== "" && !isSystem

    // System entries use a fixed, purpose-tinted gradient (stable across
    // launches, independent of the hash) so Saved / Archived / Logs / Bin read
    // as intentional, branded discs. Peers keep the deterministic per-name
    // color from Theme.gradientFor(). Both paths return a valid 2-stop array.
    readonly property var grad: isSystem ? Theme.iconGradientFor(avatarPath)
                                          : Theme.gradientFor(seed)

    function initials(n) {
        if (!n) return "#";
        var parts = n.trim().split(/\s+/);
        if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
        return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
    }

    // Gradient disc (also the fallback when an avatar image fails to load).
    // NOTE: this is ALWAYS a 2-stop gradient - never a flat single-color fill.
    Rectangle {
        id: disc
        anchors.fill: parent
        radius: Theme.radius.pill
        visible: !root.isImage || avatarImg.status !== Image.Ready
        gradient: Gradient {
            orientation: Gradient.Vertical
            GradientStop { position: 0.0; color: root.grad[0] }
            GradientStop { position: 1.0; color: root.grad[1] }
        }

        // Initials - shown for peer / real entries (not the system icons).
        Text {
            anchors.centerIn: parent
            visible: !root.isSystem
            text: root.initials(root.name)
            color: Theme.onMedia
            font.family: Theme.fontFamily
            font.pixelSize: Math.round(root.size * 0.4)
            font.bold: true
        }

        // Glyph - shown for the system icon avatars. Glyph color reuses the
        // theme token so it stays legible on the tinted gradient.
        Icon {
            anchors.centerIn: parent
            visible: root.isSystem
            name: root.avatarPath === "bookmark" ? "bookmark"
                  : (root.avatarPath === "logs" ? "logs"
                  : (root.avatarPath === "trash" ? "trash" : "archive"))
            color: Theme.onMedia
            size: root.size * 0.5
        }
    }

    // Real image avatar, clipped to a circle via the parent radius + clip.
    Rectangle {
        anchors.fill: parent
        radius: Theme.radius.pill
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
