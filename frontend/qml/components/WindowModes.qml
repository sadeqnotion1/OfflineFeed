import QtQuick

// ---------------------------------------------------------------------------
//  WindowModes.qml  (NEW - drop-in)
// ---------------------------------------------------------------------------
//  Non-visual controller that turns the FIXED 3-pane shell into a responsive,
//  Telegram-style adaptive layout driven by the live window width.
//
//      width >= compactBreakpoint  ->  WIDE   : rail + chat list + chat view
//      width <  compactBreakpoint  ->  COMPACT (single pane):
//            detailActive == false ->  chat list, full width
//            detailActive == true  ->  the open chat, full width (+ Back arrow)
//
//  Usage (Main.qml):
//      WindowModes { id: modes; windowWidth: win.width }
// ---------------------------------------------------------------------------
QtObject {
    id: modes

    // Live window width. Bind to win.width in Main.qml.
    property int windowWidth: 0
    // Below this width we collapse to a single pane (px).
    property int compactBreakpoint: 720
    // True while a chat is open in compact mode (decides which pane shows).
    property bool detailActive: false

    readonly property bool compact: windowWidth > 0 && windowWidth < compactBreakpoint

    // Convenience flags (kept for readability / future use).
    readonly property bool listPaneVisible:  !compact || !detailActive
    readonly property bool detailPaneVisible: !compact || detailActive

    // Growing back to WIDE shows both panes again, so drop the single-pane
    // drill-in flag to avoid a stuck "detail only" state.
    onCompactChanged: if (!compact) detailActive = false
}
