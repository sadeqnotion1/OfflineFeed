# OfflineFeed — Telegram Desktop UI Build Guide

<aside>
🎯

**Goal:** turn OfflineFeed (Python backend + Vanilla frontend) into a near pixel-perfect, *native* Telegram Desktop clone. **The language change:** retire the Vanilla HTML/CSS/JS frontend and rebuild the UI in **Qt via PySide6 + QML** — the same framework Telegram Desktop itself uses. Your Python backend stays.

</aside>

This guide contains ready-to-use files for each step of the approved plan. Create the files in the paths shown and run with `python frontend/app.py`.

## Step 1 — Scaffold the Qt frontend

Install the framework and create the project structure.

```bash
pip install PySide6
```

**`requirements.txt`** (add this line):

```
PySide6>=6.6
```

**Target structure:**

```
OfflineFeed/
├── backend/                # existing Python (unchanged)
├── frontend/
│   ├── app.py              # PySide6 entry point
│   ├── bridge.py           # Python↔QML bridge + models
│   └── qml/
│       ├── Main.qml
│       ├── themes/
│       │   ├── qmldir
│       │   └── Theme.qml   # singleton color tokens
│       ├── components/
│       │   ├── TitleBar.qml
│       │   ├── ChatList.qml
│       │   ├── ChatRow.qml
│       │   ├── ChatView.qml
│       │   ├── MessageBubble.qml
│       │   └── InfoPanel.qml
│       └── assets/
│           ├── fonts/      # Roboto + Vazirmatn .ttf
│           └── icons/      # SVGs
└── legacy/                 # old vanilla frontend (reference)
```

**`frontend/app.py`** — boots Qt, loads fonts, exposes the backend, opens a frameless window:

```python
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication, QFontDatabase, QFont
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl

from bridge import ChatBridge

def main() -> None:
    app = QGuiApplication(sys.argv)
    app.setApplicationName("OfflineFeed")

    # Bundle Telegram-style fonts (Roboto + Vazirmatn for Persian/RTL)
    fonts_dir = Path(__file__).parent / "qml" / "assets" / "fonts"
    if fonts_dir.exists():
        for f in fonts_dir.glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(f))
    app.setFont(QFont("Roboto", 10))

    engine = QQmlApplicationEngine()

    # Expose the Python backend to QML
    bridge = ChatBridge()
    ctx = engine.rootContext()
    ctx.setContextProperty("bridge", bridge)
    ctx.setContextProperty("chatModel", bridge.chat_model)
    ctx.setContextProperty("messageModel", bridge.message_model)

    qml_dir = Path(__file__).parent / "qml"
    engine.addImportPath(str(qml_dir))
    engine.load(QUrl.fromLocalFile(str(qml_dir / "Main.qml")))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

## Step 2 — The 3-pane layout

**`frontend/qml/Main.qml`** — frameless window + title bar + resizable panes:

```
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import "themes"
import "components"

Window {
    id: win
    width: 1100
    height: 720
    minimumWidth: 760
    minimumHeight: 480
    visible: true
    flags: Qt.Window | Qt.FramelessWindowHint
    color: Theme.bg

    Component.onCompleted: Theme.dark = (bridge.theme === "dark")

    property bool infoOpen: false

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        TitleBar { Layout.fillWidth: true }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            ChatList {
                Layout.preferredWidth: 360
                Layout.minimumWidth: 280
                Layout.maximumWidth: 420
                Layout.fillHeight: true
            }

            Rectangle {
                width: 1
                Layout.fillHeight: true
                color: Qt.darker(Theme.panel, 1.3)
            }

            ChatView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                onInfoRequested: win.infoOpen = !win.infoOpen
            }

            InfoPanel {
                Layout.preferredWidth: win.infoOpen ? 340 : 0
                Layout.fillHeight: true
                clip: true
                Behavior on Layout.preferredWidth {
                    NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
                }
            }
        }
    }
}
```

- <strong>frontend/qml/components/TitleBar.qml</strong> — custom frameless bar + window drag
    
    ```
    import QtQuick
    import QtQuick.Layouts
    import "../themes"
    
    Rectangle {
        id: bar
        height: 40
        color: Theme.panel
    
        // Drag the frameless window by the title bar
        MouseArea {
            anchors.fill: parent
            onPressed: Window.window.startSystemMove()
        }
    
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 12
            spacing: 8
    
            Text {
                text: "OfflineFeed"
                color: Theme.text
                font.pixelSize: 14
                font.bold: true
                Layout.fillWidth: true
            }
    
            // Theme toggle
            Text {
                text: Theme.dark ? "☀" : "🌙"
                color: Theme.textSecondary
                font.pixelSize: 16
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        Theme.dark = !Theme.dark
                        bridge.setTheme(Theme.dark ? "dark" : "light")
                    }
                }
            }
    
            Repeater {
                model: ["–", "☐", "✕"]
                Text {
                    required property int index
                    required property string modelData
                    text: modelData
                    color: Theme.textSecondary
                    font.pixelSize: 14
                    Layout.rightMargin: 8
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            if (index === 0) Window.window.showMinimized()
                            else if (index === 1) Window.window.visibility =
                                (Window.window.visibility === Window.Maximized
                                 ? Window.Windowed : Window.Maximized)
                            else Qt.quit()
                        }
                    }
                }
            }
        }
    }
    ```
    

## Step 3 — Theme engine (dark + light)

**`frontend/qml/themes/qmldir`**:

```
singleton Theme 1.0 Theme.qml
```

**`frontend/qml/themes/Theme.qml`** — single source of truth, animated swap, exact Telegram tokens:

```
pragma Singleton
import QtQuick

QtObject {
    property bool dark: true

    readonly property var darkTokens: ({
        "bg":            "#17212b",
        "panel":         "#232e3c",
        "selection":     "#2b5278",
        "accent":        "#5288c1",
        "bubbleOut":     "#2b5278",
        "bubbleIn":      "#182533",
        "text":          "#ffffff",
        "textSecondary": "#7f91a4"
    })

    readonly property var lightTokens: ({
        "bg":            "#ffffff",
        "panel":         "#f4f4f5",
        "selection":     "#e8f0fb",
        "accent":        "#3390ec",
        "bubbleOut":     "#effdde",
        "bubbleIn":      "#ffffff",
        "text":          "#000000",
        "textSecondary": "#707579"
    })

    readonly property var t: dark ? darkTokens : lightTokens

    property color bg:            t.bg
    property color panel:         t.panel
    property color selection:     t.selection
    property color accent:        t.accent
    property color bubbleOut:     t.bubbleOut
    property color bubbleIn:      t.bubbleIn
    property color text:          t.text
    property color textSecondary: t.textSecondary

    // Cross-fade colors when the theme flips
    Behavior on bg    { ColorAnimation { duration: 180 } }
    Behavior on panel { ColorAnimation { duration: 180 } }
}
```

## Step 4 — Sidebar & chat list

**`frontend/qml/components/ChatList.qml`** — search bar + scrollable list:

```
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

Rectangle {
    color: Theme.panel

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Rounded Telegram-style search
        Rectangle {
            Layout.fillWidth: true
            Layout.margins: 8
            height: 38
            radius: 19
            color: Qt.darker(Theme.panel, 1.25)
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 14
                spacing: 8
                Text { text: "🔍"; color: Theme.textSecondary; font.pixelSize: 14 }
                TextField {
                    Layout.fillWidth: true
                    placeholderText: "Search"
                    color: Theme.text
                    placeholderTextColor: Theme.textSecondary
                    background: Item {}
                }
            }
        }

        ListView {
            id: list
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: chatModel
            boundsBehavior: Flickable.OvershootBounds
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
            delegate: ChatRow { width: list.width }
        }
    }
}
```

**`frontend/qml/components/ChatRow.qml`** — avatar · name · preview · time · unread badge:

```
import QtQuick
import QtQuick.Layouts
import "../themes"

Rectangle {
    id: row
    height: 70
    color: hover.containsMouse ? Qt.lighter(Theme.panel, 1.15)
                               : (ListView.isCurrentItem ? Theme.selection : "transparent")
    Behavior on color { ColorAnimation { duration: 120 } }

    required property string name
    required property string lastMessage
    required property string time
    required property int unread

    MouseArea {
        id: hover
        anchors.fill: parent
        hoverEnabled: true
        onClicked: {
            row.ListView.view.currentIndex = index
            bridge.openChat(name)
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 10

        // Round avatar
        Rectangle {
            width: 54; height: 54; radius: 27
            color: Theme.accent
            Text {
                anchors.centerIn: parent
                text: row.name.length ? row.name[0].toUpperCase() : "?"
                color: "white"; font.pixelSize: 22; font.bold: true
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            RowLayout {
                Layout.fillWidth: true
                Text {
                    text: row.name; color: Theme.text
                    font.pixelSize: 15; font.bold: true
                    Layout.fillWidth: true; elide: Text.ElideRight
                }
                Text { text: row.time; color: Theme.textSecondary; font.pixelSize: 12 }
            }
            RowLayout {
                Layout.fillWidth: true
                Text {
                    text: row.lastMessage; color: Theme.textSecondary
                    font.pixelSize: 13; Layout.fillWidth: true; elide: Text.ElideRight
                }
                Rectangle {
                    visible: row.unread > 0
                    height: 20; width: Math.max(20, badge.width + 12); radius: 10
                    color: Theme.accent
                    Text {
                        id: badge; anchors.centerIn: parent
                        text: row.unread; color: "white"; font.pixelSize: 12
                    }
                }
            }
        }
    }
}
```

## Step 5 — Message bubbles & chat view

**`frontend/qml/components/ChatView.qml`** — header + bubble list + composer:

```
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

Rectangle {
    id: chat
    color: Theme.bg
    signal infoRequested()

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Chat header
        Rectangle {
            Layout.fillWidth: true
            height: 56
            color: Theme.panel
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 14
                spacing: 10
                Rectangle {
                    width: 40; height: 40; radius: 20; color: Theme.accent
                    Text { anchors.centerIn: parent; text: "O"; color: "white"; font.bold: true }
                }
                ColumnLayout {
                    Layout.fillWidth: true; spacing: 0
                    Text { text: "OfflineFeed Bot"; color: Theme.text; font.pixelSize: 15; font.bold: true }
                    Text { text: "last seen recently"; color: Theme.textSecondary; font.pixelSize: 12 }
                }
                Text {
                    text: "⋮"; color: Theme.textSecondary; font.pixelSize: 20
                    Layout.rightMargin: 14
                    MouseArea { anchors.fill: parent; onClicked: chat.infoRequested() }
                }
            }
        }

        // Messages
        ListView {
            id: messages
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: messageModel
            spacing: 4
            verticalLayoutDirection: ListView.BottomToTop
            delegate: MessageBubble { listWidth: messages.width }
            ScrollBar.vertical: ScrollBar {}
        }

        // Composer
        Rectangle {
            Layout.fillWidth: true
            height: 56
            color: Theme.panel
            RowLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8
                Text { text: "😊"; font.pixelSize: 20; color: Theme.textSecondary }
                TextField {
                    id: input
                    Layout.fillWidth: true
                    placeholderText: "Message"
                    color: Theme.text
                    placeholderTextColor: Theme.textSecondary
                    background: Rectangle { radius: 18; color: Qt.darker(Theme.panel, 1.2) }
                    leftPadding: 14
                }
                Text { text: "📎"; font.pixelSize: 18; color: Theme.textSecondary }
                // Send ↔ mic morph
                Rectangle {
                    width: 40; height: 40; radius: 20; color: Theme.accent
                    Text {
                        anchors.centerIn: parent
                        text: input.text.length ? "➤" : "🎤"; color: "white"; font.pixelSize: 16
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: if (input.text.length) { bridge.sendMessage(input.text); input.text = "" }
                    }
                }
            }
        }
    }
}
```

**`frontend/qml/components/MessageBubble.qml`** — aligned bubbles, tail, timestamp, read ticks, slide-in:

```
import QtQuick
import QtQuick.Layouts
import "../themes"

Item {
    id: bubble
    property real listWidth: 600
    width: listWidth
    height: content.height + 8

    required property string text
    required property string time
    required property bool outgoing
    required property bool read

    Rectangle {
        id: content
        radius: 13
        color: bubble.outgoing ? Theme.bubbleOut : Theme.bubbleIn
        width: Math.min(textItem.implicitWidth + 24, bubble.listWidth * 0.7)
        height: textItem.implicitHeight + meta.height + 16
        anchors.right: bubble.outgoing ? parent.right : undefined
        anchors.left: bubble.outgoing ? undefined : parent.left
        anchors.margins: 12

        Column {
            anchors.fill: parent
            anchors.margins: 8
            spacing: 2
            Text {
                id: textItem
                text: bubble.text
                color: Theme.text
                font.pixelSize: 14
                wrapMode: Text.Wrap
                width: parent.width
            }
            Row {
                id: meta
                anchors.right: parent.right
                spacing: 4
                Text { text: bubble.time; color: Theme.textSecondary; font.pixelSize: 11 }
                Text {
                    visible: bubble.outgoing
                    text: bubble.read ? "✓✓" : "✓"
                    color: bubble.read ? Theme.accent : Theme.textSecondary
                    font.pixelSize: 11
                }
            }
        }
    }

    // Slide-in on appear
    opacity: 0
    Component.onCompleted: appear.start()
    NumberAnimation on opacity { id: appear; running: false; from: 0; to: 1; duration: 160 }
}
```

## Step 6 — Icons, fonts & animations

<aside>
🔤

**Fonts:** drop `Roboto-*.ttf` (Telegram Desktop's UI font) and `Vazirmatn-*.ttf` (crisp Persian/RTL fallback) into `frontend/qml/assets/fonts/`. `app.py` already registers every `.ttf` there at startup.

</aside>

- **Icons** — place line-style SVGs in `assets/icons/` (search, menu, attach, emoji, send, mic, check, pin, mute). Recolor per theme with QML's `Image` + a `ColorOverlay` (from `Qt5Compat.GraphicalEffects`) bound to `Theme.textSecondary`. The emoji glyphs above are placeholders — swap them for your SVGs.
- **Animations already wired in this guide:** chat-row hover/selection color fade, theme cross-fade (`Behavior on bg/panel`), info-panel slide (`Behavior on Layout.preferredWidth`), bubble slide-in (`NumberAnimation on opacity`), and send↔mic morph. Use `easing.type: Easing.OutCubic` at ~150–200 ms to match Telegram's feel.

**RTL note (for Persian):** set `LayoutMirroring.enabled: Qt.application.layoutDirection === Qt.RightToLeft` on root items, and give `Text` blocks `horizontalAlignment: Text.AlignRight` when content is Persian so bubbles mirror correctly.

## Step 7 — Wire QML to the Python backend

**`frontend/bridge.py`** — exposes data + actions to QML via models, signals, and slots:

```python
from PySide6.QtCore import (
    QObject, Signal, Slot, Property,
    QAbstractListModel, QModelIndex, Qt,
)

class ChatListModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    LastMessageRole = Qt.UserRole + 2
    TimeRole = Qt.UserRole + 3
    UnreadRole = Qt.UserRole + 4

    def __init__(self, chats=None):
        super().__init__()
        self._chats = chats or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._chats)

    def data(self, index, role):
        if not index.isValid():
            return None
        c = self._chats[index.row()]
        return {
            self.NameRole: c.get("name"),
            self.LastMessageRole: c.get("last_message"),
            self.TimeRole: c.get("time"),
            self.UnreadRole: c.get("unread", 0),
        }.get(role)

    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.LastMessageRole: b"lastMessage",
            self.TimeRole: b"time",
            self.UnreadRole: b"unread",
        }

class MessageModel(QAbstractListModel):
    TextRole = Qt.UserRole + 1
    TimeRole = Qt.UserRole + 2
    OutgoingRole = Qt.UserRole + 3
    ReadRole = Qt.UserRole + 4

    def __init__(self, messages=None):
        super().__init__()
        self._messages = messages or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._messages)

    def data(self, index, role):
        if not index.isValid():
            return None
        m = self._messages[index.row()]
        return {
            self.TextRole: m.get("text"),
            self.TimeRole: m.get("time"),
            self.OutgoingRole: m.get("outgoing", False),
            self.ReadRole: m.get("read", False),
        }.get(role)

    def roleNames(self):
        return {
            self.TextRole: b"text",
            self.TimeRole: b"time",
            self.OutgoingRole: b"outgoing",
            self.ReadRole: b"read",
        }

    def add(self, text, outgoing=True, time="now"):
        self.beginInsertRows(QModelIndex(), 0, 0)
        self._messages.insert(0, {"text": text, "time": time,
                                  "outgoing": outgoing, "read": False})
        self.endInsertRows()

class ChatBridge(QObject):
    themeChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self._theme = "dark"
        # TODO: replace sample data with calls into your OfflineFeed backend
        self.chat_model = ChatListModel([
            {"name": "Saved Messages", "last_message": "Welcome!",
             "time": "09:41", "unread": 0},
            {"name": "OfflineFeed Bot", "last_message": "Feed synced.",
             "time": "08:12", "unread": 3},
        ])
        self.message_model = MessageModel([
            {"text": "Welcome to OfflineFeed 👋", "time": "09:40",
             "outgoing": False, "read": True},
            {"text": "Looks just like Telegram!", "time": "09:41",
             "outgoing": True, "read": True},
        ])

    @Property(str, notify=themeChanged)
    def theme(self):
        return self._theme

    @Slot(str)
    def setTheme(self, value):
        if value != self._theme:
            self._theme = value
            self.themeChanged.emit(value)
            # TODO: persist to your settings file via the backend

    @Slot(str)
    def openChat(self, chat_id):
        # TODO: load this chat's messages from the backend into message_model
        print("open chat:", chat_id)

    @Slot(str)
    def sendMessage(self, text):
        self.message_model.add(text, outgoing=True)
        # TODO: forward to your backend (and append the reply when it arrives)
```

- <strong>frontend/qml/components/InfoPanel.qml</strong> — slide-in contact/chat info
    
    ```
    import QtQuick
    import QtQuick.Layouts
    import "../themes"
    
    Rectangle {
        color: Theme.panel
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12
            Rectangle {
                Layout.alignment: Qt.AlignHCenter
                width: 90; height: 90; radius: 45; color: Theme.accent
                Text { anchors.centerIn: parent; text: "O"; color: "white"
                       font.pixelSize: 40; font.bold: true }
            }
            Text { Layout.alignment: Qt.AlignHCenter; text: "OfflineFeed Bot"
                   color: Theme.text; font.pixelSize: 18; font.bold: true }
            Text { Layout.alignment: Qt.AlignHCenter; text: "@offlinefeed_bot"
                   color: Theme.textSecondary; font.pixelSize: 13 }
            Item { Layout.fillHeight: true }
        }
    }
    ```
    

### Packaging (native desktop build)

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name OfflineFeed \
  --add-data "frontend/qml:qml" frontend/app.py
```

Then compare side-by-side against real Telegram Desktop (dark + light) and fine-tune spacing/colors against the tokens in Step 3.

---

## Closing the gap with Telegram — icons & more

<aside>
🧩

**What's still different from real Telegram (from your screenshot):** emoji glyphs instead of crisp line icons · folder tabs need labels + unread badges · flat avatars (Telegram uses per-user color gradients) · no reactions / view counts / forward button on channel posts · no pinned-message bar · header missing subscriber count + verified badge. Everything below fixes those.

</aside>

### 1. A real icon system (replaces every emoji)

Create a reusable, theme-tinted SVG icon component.

**`frontend/qml/components/Icon.qml`**

```
import QtQuick
import Qt5Compat.GraphicalEffects

Item {
    id: root
    property string name
    property color color: "#ffffff"
    property int size: 24
    width: size
    height: size

    Image {
        id: img
        anchors.fill: parent
        source: "../assets/icons/" + root.name + ".svg"
        sourceSize: Qt.size(root.size, root.size)
        smooth: true
        visible: false
    }
    ColorOverlay {
        anchors.fill: img
        source: img
        color: root.color
    }
}
```

Usage anywhere: `Icon { name: "search"; color: Theme.textSecondary; size: 18 }`

Save these SVGs into `frontend/qml/assets/icons/` (hand-drawn to match Telegram's thin line style). For any extras, the free **Lucide** / **Feather** icon sets drop in 1:1 with the same names.

- SVG icon files (copy each into its own <code>.svg</code>)
    
    **`menu.svg`**
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
    ```
    
    **`search.svg`**
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><line x1="16.5" y1="16.5" x2="21" y2="21"/></svg>
    ```
    
    **`settings.svg`**
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7 1.1V21a2 2 0 0 1-4 0v-.1A1.6 1.6 0 0 0 7 19.4a1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A1.6 1.6 0 0 0 3 14a2 2 0 0 1 0-4h.1A1.6 1.6 0 0 0 4.6 7a1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1A1.6 1.6 0 0 0 10 3a2 2 0 0 1 4 0v.1A1.6 1.6 0 0 0 17 4.6a1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1A1.6 1.6 0 0 0 21 10a2 2 0 0 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1z"/></svg>
    ```
    
    **`send.svg`** (paper plane)
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff"><path d="M2 12 22 3l-9 19-2.5-8.5L2 12z"/></svg>
    ```
    
    **`attach.svg`** (paperclip)
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11l-8.5 8.5a4 4 0 0 1-6-6L13 5a3 3 0 0 1 4 4l-7.6 7.6a1.5 1.5 0 0 1-2.1-2.1l7-7"/></svg>
    ```
    
    **`emoji.svg`** (smiley)
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M8 14a4 4 0 0 0 8 0"/><line x1="9" y1="9.5" x2="9" y2="9.5"/><line x1="15" y1="9.5" x2="15" y2="9.5"/></svg>
    ```
    
    **`mic.svg`**
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0"/><line x1="12" y1="18" x2="12" y2="21"/></svg>
    ```
    
    **`pin.svg`**
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6l-1 6 3 3v2h-5v6l-1 1-1-1v-6H5v-2l3-3-1-6z"/></svg>
    ```
    
    **`mute.svg`** (bell + slash)
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9a6 6 0 0 1 12 0c0 6 2.5 7 2.5 7H3.5S6 15 6 9z"/><path d="M10 20a2 2 0 0 0 4 0"/><line x1="3" y1="3" x2="21" y2="21"/></svg>
    ```
    
    **`chats.svg`** (folder-rail bubble)
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-11.5 7L3 21l2-6.5A8 8 0 1 1 21 12z"/></svg>
    ```
    
    **`saved.svg`** (bookmark)
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12v18l-6-4-6 4z"/></svg>
    ```
    
    **`folder.svg`**
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6a2 2 0 0 1 2-2h3.5l2 2H19a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
    ```
    
    **`eye.svg`** (view count)
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>
    ```
    
    **`forward.svg`**
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 6l6 6-6 6"/><path d="M19 12H7a4 4 0 0 0-4 4v1"/></svg>
    ```
    
    **`check-double.svg`** (read ticks)
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 13l4 4 8-9"/><path d="M9 16l1 1 8-9"/></svg>
    ```
    
    **`verified.svg`** (tint with `Theme.accent`)
    
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff"><path d="M12 1l2.6 2 3.2.2 1 3 2.6 1.9-1.2 3 1.2 3-2.6 1.9-1 3-3.2.2L12 23l-2.6-2-3.2-.2-1-3L2.6 16l1.2-3-1.2-3 2.6-1.9 1-3 3.2-.2L12 1z"/><path d="M7.5 12.2l3 3 6-6.6" fill="none" stroke="#17212b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
    ```
    

**Swap the emoji placeholders** in the existing files:

| In file | Replace this | With this |
| --- | --- | --- |
| `ChatList.qml` | `Text { text: "🔍" … }` | `Icon { name: "search"; color: Theme.textSecondary; size: 18 }` |
| `ChatView.qml` (composer) | `Text { text: "😊" … }` | `Icon { name: "emoji"; color: Theme.textSecondary; size: 22 }` |
| `ChatView.qml` (composer) | `Text { text: "📎" … }` | `Icon { name: "attach"; color: Theme.textSecondary; size: 20 }` |
| `ChatView.qml` (send) | `text: input.text.length ? "➤" : "🎤"` | `Icon { name: input.text.length ? "send" : "mic"; color: "white"; size: 18; anchors.centerIn: parent }` |
| `ChatView.qml` (header) | `Text { text: "⋮" … }` | `Icon { name: "menu"; color: Theme.textSecondary; size: 20 }` |

### 2. Gradient avatars (per-user color)

**`frontend/qml/components/Avatar.qml`** — Telegram's 7-palette gradient picked from the name:

```
import QtQuick

Item {
    id: root
    property string name: ""
    property int size: 54
    width: size; height: size

    readonly property var palettes: [
        ["#ff885e", "#ff516a"], ["#ffcd6a", "#ffa85c"],
        ["#a0de7e", "#54cb68"], ["#82b1ff", "#665fff"],
        ["#e0a2f3", "#d669ed"], ["#7accf2", "#3f9fff"],
        ["#ff8aac", "#ff5b95"]
    ]
    readonly property int idx: {
        var h = 0
        for (var i = 0; i < name.length; i++) h += name.charCodeAt(i)
        return h % palettes.length
    }

    Rectangle {
        anchors.fill: parent
        radius: width / 2
        gradient: Gradient {
            GradientStop { position: 0.0; color: root.palettes[root.idx][0] }
            GradientStop { position: 1.0; color: root.palettes[root.idx][1] }
        }
        Text {
            anchors.centerIn: parent
            text: root.name.length ? root.name[0].toUpperCase() : "?"
            color: "white"
            font.pixelSize: root.size * 0.42
            font.bold: true
        }
    }
}
```

Then replace each inline avatar `Rectangle { … radius: 27 … }` in `ChatRow.qml`, `ChatView.qml`, and `InfoPanel.qml` with `Avatar { name: row.name; size: 54 }` (adjust size per spot).

### 3. Folder rail with labels + unread badges

**`frontend/qml/components/FolderRail.qml`** — the labeled tab strip from real Telegram:

```
import QtQuick
import "../themes"

Rectangle {
    id: rail
    width: 68
    color: Qt.darker(Theme.panel, 1.15)

    property int current: 0
    property var folders: [
        { icon: "chats",  label: "All chats", unread: 0 },
        { icon: "folder", label: "G1",        unread: 1 },
        { icon: "folder", label: "Shop",      unread: 1 },
        { icon: "folder", label: "Ent",       unread: 1 },
        { icon: "folder", label: "Personal",  unread: 1 },
        { icon: "folder", label: "Bots",      unread: 8 }
    ]

    Column {
        anchors.fill: parent
        spacing: 2

        Item {
            width: parent.width; height: 50
            Icon { anchors.centerIn: parent; name: "menu"; color: Theme.textSecondary; size: 22 }
        }

        Repeater {
            model: rail.folders
            delegate: Item {
                id: cell
                required property var modelData
                required property int index
                width: rail.width
                height: 64
                property bool active: rail.current === index

                Rectangle {
                    anchors.fill: parent
                    color: cell.active ? Qt.lighter(Theme.panel, 1.12) : "transparent"
                }
                Rectangle {
                    visible: cell.active
                    width: 3; height: 34; radius: 2; color: Theme.accent
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                }
                Column {
                    anchors.centerIn: parent
                    spacing: 3
                    Icon {
                        anchors.horizontalCenter: parent.horizontalCenter
                        name: cell.modelData.icon
                        color: cell.active ? Theme.accent : Theme.textSecondary
                        size: 26
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: cell.modelData.label
                        color: cell.active ? Theme.text : Theme.textSecondary
                        font.pixelSize: 11
                    }
                }
                Rectangle {
                    visible: cell.modelData.unread > 0
                    anchors.right: parent.right; anchors.rightMargin: 12
                    anchors.top: parent.top;     anchors.topMargin: 8
                    width: Math.max(18, badge.width + 8); height: 18; radius: 9
                    color: Theme.accent
                    Text { id: badge; anchors.centerIn: parent
                           text: cell.modelData.unread; color: "white"; font.pixelSize: 11 }
                }
                MouseArea { anchors.fill: parent; onClicked: rail.current = cell.index }
            }
        }
    }

    Icon {
        name: "settings"; color: Theme.textSecondary; size: 22
        anchors.bottom: parent.bottom; anchors.bottomMargin: 16
        anchors.horizontalCenter: parent.horizontalCenter
    }
}
```

**Wire it into `Main.qml`** — add it as the first item inside the inner `RowLayout`, before `ChatList`:

```
RowLayout {
    Layout.fillWidth: true
    Layout.fillHeight: true
    spacing: 0

    FolderRail { Layout.fillHeight: true }      // <-- add this line

    ChatList { /* …unchanged… */ }
    // …rest unchanged…
}
```

### 4. Reactions, view count & forward (channel posts)

**`frontend/qml/components/ReactionsBar.qml`**

```
import QtQuick
import "../themes"

Flow {
    id: root
    spacing: 6
    // [{ emoji: "❤️", count: 199, chosen: true }, …]
    property var reactions: []

    Repeater {
        model: root.reactions
        delegate: Rectangle {
            required property var modelData
            height: 28
            width: inner.width + 18
            radius: 14
            color: modelData.chosen
                ? Theme.accent
                : Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.15)
            Row {
                id: inner
                anchors.centerIn: parent
                spacing: 4
                Text { text: modelData.emoji; font.pixelSize: 14 }
                Text {
                    text: modelData.count
                    color: modelData.chosen ? "white" : Theme.accent
                    font.pixelSize: 13; font.bold: true
                }
            }
        }
    }
}
```

**Add to the bottom of the bubble** in `MessageBubble.qml` (inside the `Column`, after the text, replacing the old `meta` row):

```
ReactionsBar {
    width: parent.width
    reactions: bubble.reactions   // add: required property var reactions
    visible: reactions.length > 0
}
Row {
    anchors.right: parent.right
    spacing: 5
    Icon { name: "eye"; color: Theme.textSecondary; size: 13; visible: bubble.views > 0 }
    Text { text: bubble.views > 0 ? bubble.viewsLabel : ""
           color: Theme.textSecondary; font.pixelSize: 11 }
    Text { text: bubble.time; color: Theme.textSecondary; font.pixelSize: 11 }
    Icon {
        name: "check-double"; size: 13; visible: bubble.outgoing
        color: bubble.read ? Theme.accent : Theme.textSecondary
    }
}
```

And a floating **forward** button beside channel posts (place inside the bubble's root `Item`, after the `content` Rectangle):

```
Rectangle {
    visible: !bubble.outgoing
    width: 30; height: 30; radius: 15
    color: Theme.panel
    anchors.left: content.right
    anchors.leftMargin: 6
    anchors.bottom: content.bottom
    Icon { anchors.centerIn: parent; name: "forward"; color: Theme.textSecondary; size: 16 }
}
```

Add these `required property` lines near the top of `MessageBubble.qml`: `property var reactions: []`, `property int views: 0`, `property string viewsLabel: ""`. Feed them from `MessageModel` in `bridge.py` (extra roles, same pattern as the others).

### 5. Pinned-message bar

Drop this directly **under the chat header** in `ChatView.qml`:

```
Rectangle {
    Layout.fillWidth: true
    height: 46
    color: Theme.bg
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 14
        spacing: 10
        Rectangle { width: 2; height: 30; radius: 1; color: Theme.accent }
        ColumnLayout {
            spacing: 0
            Layout.fillWidth: true
            Text { text: "Pinned message"; color: Theme.accent
                   font.pixelSize: 12; font.bold: true }
            Text { text: "All free internet tutorials are posted on my channel…"
                   color: Theme.textSecondary; font.pixelSize: 12; elide: Text.ElideRight
                   Layout.fillWidth: true }
        }
        Icon { name: "pin"; color: Theme.textSecondary; size: 18; Layout.rightMargin: 14 }
    }
}
```

### 6. Header polish — subscriber count, verified, action icons

Upgrade the header row in `ChatView.qml`:

```
ColumnLayout {
    Layout.fillWidth: true; spacing: 0
    RowLayout {
        spacing: 5
        Text { text: "Matin SenPai"; color: Theme.text; font.pixelSize: 15; font.bold: true }
        Icon { name: "verified"; color: Theme.accent; size: 15 }   // blue check
    }
    Text { text: "161,897 subscribers"; color: Theme.textSecondary; font.pixelSize: 12 }
}
// …then on the right side of the header:
Row {
    spacing: 18
    Icon { name: "search"; color: Theme.textSecondary; size: 19 }
    Icon { name: "menu";   color: Theme.textSecondary; size: 19 }   // info-panel toggle
}
```

<aside>
📋

**Chat-list rows** can use the same pieces: add a small `Icon { name: "mute" }` after muted names, an `Icon { name: "verified" }` after verified ones, and a media prefix (`Icon { name: "attach" }` / a tiny thumbnail) before the last-message preview — exactly like the photo/video markers in your reference screenshot.

</aside>

<aside>
✅

**End state:** a native, Python-driven desktop app whose layout, theming, bubbles, and motion mirror Telegram Desktop — built on the same Qt toolkit Telegram itself uses.

</aside>