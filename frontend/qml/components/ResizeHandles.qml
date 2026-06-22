import QtQuick
import QtQuick.Window

// ---------------------------------------------------------------------------
//  ResizeHandles.qml  (NEW - drop-in)
// ---------------------------------------------------------------------------
//  The app window uses `Qt.FramelessWindowHint`, which removes the native
//  resize border. That is exactly why the window felt stuck at "one
//  screensize": there was nothing to grab to drag-resize it. This overlays
//  thin, INVISIBLE drag strips on every edge + corner that call the window's
//  startSystemResize(), restoring normal Telegram-style edge-drag resizing.
//
//  It only grabs the few pixels at each edge/corner, so every interior click
//  falls straight through to the UI underneath (no MouseArea fills the body).
//
//  Usage (Main.qml, as a DIRECT child of the ApplicationWindow, on top):
//      ResizeHandles {
//          anchors.fill: parent
//          targetWindow: win
//          z: 9999
//          onResizeStarted: win._isMaxed = false
//      }
// ---------------------------------------------------------------------------
Item {
    id: root

    // The ApplicationWindow / Window to resize. Bind to the root window id.
    property var targetWindow: null
    // Thickness of the edge grab strips (px).
    property int edgeSize: 6
    // Size of the square corner grab zones (px).
    property int cornerSize: 14

    // Resizing only makes sense while the window is in its normal state.
    readonly property bool _canResize: !!targetWindow
        && targetWindow.visibility !== Window.Maximized
        && targetWindow.visibility !== Window.FullScreen
        && targetWindow.visibility !== Window.Minimized

    // Emitted right before a system resize begins. Main.qml uses this to clear
    // its manual "maximized" bookkeeping so the restore size stays correct.
    signal resizeStarted()

    function _resize(edges) {
        if (root._canResize && targetWindow) {
            root.resizeStarted()
            targetWindow.startSystemResize(edges)
        }
    }

    // ---- Edges ----
    MouseArea {   // left
        anchors { left: parent.left; top: parent.top; bottom: parent.bottom }
        anchors.topMargin: root.cornerSize
        anchors.bottomMargin: root.cornerSize
        width: root.edgeSize
        enabled: root._canResize
        acceptedButtons: Qt.LeftButton
        cursorShape: Qt.SizeHorCursor
        onPressed: root._resize(Qt.LeftEdge)
    }
    MouseArea {   // right
        anchors { right: parent.right; top: parent.top; bottom: parent.bottom }
        anchors.topMargin: root.cornerSize
        anchors.bottomMargin: root.cornerSize
        width: root.edgeSize
        enabled: root._canResize
        acceptedButtons: Qt.LeftButton
        cursorShape: Qt.SizeHorCursor
        onPressed: root._resize(Qt.RightEdge)
    }
    MouseArea {   // top
        anchors { top: parent.top; left: parent.left; right: parent.right }
        anchors.leftMargin: root.cornerSize
        anchors.rightMargin: root.cornerSize
        height: root.edgeSize
        enabled: root._canResize
        acceptedButtons: Qt.LeftButton
        cursorShape: Qt.SizeVerCursor
        onPressed: root._resize(Qt.TopEdge)
    }
    MouseArea {   // bottom
        anchors { bottom: parent.bottom; left: parent.left; right: parent.right }
        anchors.leftMargin: root.cornerSize
        anchors.rightMargin: root.cornerSize
        height: root.edgeSize
        enabled: root._canResize
        acceptedButtons: Qt.LeftButton
        cursorShape: Qt.SizeVerCursor
        onPressed: root._resize(Qt.BottomEdge)
    }

    // ---- Corners (diagonal cursors) ----
    MouseArea {   // top-left  \
        anchors { left: parent.left; top: parent.top }
        width: root.cornerSize; height: root.cornerSize
        enabled: root._canResize
        acceptedButtons: Qt.LeftButton
        cursorShape: Qt.SizeFDiagCursor
        onPressed: root._resize(Qt.LeftEdge | Qt.TopEdge)
    }
    MouseArea {   // top-right  /
        anchors { right: parent.right; top: parent.top }
        width: root.cornerSize; height: root.cornerSize
        enabled: root._canResize
        acceptedButtons: Qt.LeftButton
        cursorShape: Qt.SizeBDiagCursor
        onPressed: root._resize(Qt.RightEdge | Qt.TopEdge)
    }
    MouseArea {   // bottom-left  /
        anchors { left: parent.left; bottom: parent.bottom }
        width: root.cornerSize; height: root.cornerSize
        enabled: root._canResize
        acceptedButtons: Qt.LeftButton
        cursorShape: Qt.SizeBDiagCursor
        onPressed: root._resize(Qt.LeftEdge | Qt.BottomEdge)
    }
    MouseArea {   // bottom-right  \
        anchors { right: parent.right; bottom: parent.bottom }
        width: root.cornerSize; height: root.cornerSize
        enabled: root._canResize
        acceptedButtons: Qt.LeftButton
        cursorShape: Qt.SizeFDiagCursor
        onPressed: root._resize(Qt.RightEdge | Qt.BottomEdge)
    }
}
