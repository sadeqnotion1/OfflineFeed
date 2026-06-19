// OfflineFeed — components/Badge.qml   (NEW FILE)
// -----------------------------------------------------------------------------
// Reusable, Telegram-style unread badge.
//
// This is the SINGLE SOURCE OF TRUTH for unread-badge geometry and color.
// Both the channel list (ChatRow.qml) and the left rail (FolderRail.qml)
// consume it, so badges can never drift apart again.
//
// Public API:
//   count      : int   - number to show. Badge auto-hides when count <= 0.
//   muted      : bool  - true => neutral/quiet badge (for muted chats).
//   overflowAt : int   - show "N+" once count exceeds this (default 99).
//
// Color logic:
//   active / unmuted -> Theme.accent background + white text
//   muted            -> neutral gray (derived from Theme.textSecondary) +
//                       Theme.textSecondary text
// All colors come from theme tokens — no hard-coded hex values.
// -----------------------------------------------------------------------------
import QtQuick
import QtQuick.Layouts
import "../themes"

Rectangle {
    id: root

    // ---- Public API ---------------------------------------------------------
    property int  count: 0
    property bool muted: false
    property int  overflowAt: 99

    // ---- Geometry: one source of truth --------------------------------------
    readonly property int badgeHeight: 18      // ~18-20 per spec
    readonly property int hPadding: 6          // horizontal padding each side

    // ---- Derived display value ----------------------------------------------
    readonly property string displayText:
        count > overflowAt ? (overflowAt + "+") : count.toString()

    // ---- Layout -------------------------------------------------------------
    implicitHeight: badgeHeight
    // min-width == height (circle for single digits), grows for wider text.
    implicitWidth: Math.max(badgeHeight, label.implicitWidth + hPadding * 2)
    height: implicitHeight
    width: implicitWidth
    radius: Theme.radius.pill

    // Hide (and take no row space) when there is nothing to show.
    visible: count > 0
    Layout.preferredHeight: badgeHeight
    Layout.preferredWidth: visible ? implicitWidth : 0

    // Active/unmuted = accent; muted = neutral gray derived from textSecondary
    // so it tracks the active (dark/light) theme without a hard-coded color.
    color: muted
        ? Qt.rgba(Theme.textSecondary.r, Theme.textSecondary.g, Theme.textSecondary.b, 0.30)
        : Theme.accent

    // Match Telegram's gentle state cross-fade (see Theme.qml / DESIGN_SYSTEM).
    Behavior on color { ColorAnimation { duration: 120 } }

    Text {
        id: label
        anchors.centerIn: parent
        text: root.displayText
        color: root.muted ? Theme.textSecondary : "white"
        font.pixelSize: 12                 // 11-12 per spec
        font.bold: true
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
