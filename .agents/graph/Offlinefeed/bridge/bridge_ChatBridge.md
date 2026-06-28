---
id: "bridge:ChatBridge"
label: "ChatBridge"
type: "class"
community: "bridge"
location: "frontend/bridge.py:ChatBridge"
degree: 19
---

# ChatBridge

- **Type**: `class`
- **Community**: `bridge`
- **Location**: `frontend/bridge.py:ChatBridge`
- **Degree**: `19`

## Summary
Imperative surface QML calls into (slots) and observes (properties/signals); owns settings, models and backend calls.

## Outgoing Connections
- [[bridge_ChatListModel|ChatListModel]] (type: `references` (*evidence: ChatBridge.__init__(chat_model: ChatListModel, ...)*))
- [[bridge_MessageModel|MessageModel]] (type: `references` (*evidence: ChatBridge.__init__(message_model: MessageModel, ...)*))
- [[bridge_SourcesModel|SourcesModel]] (type: `references` (*evidence: ChatBridge.__init__(sources_model: SourcesModel, ...)*))
- [[bridge_SearchResultsModel|SearchResultsModel]] (type: `references` (*evidence: search_results_model: Optional[SearchResultsModel]*))
- [[bridge_get|_get()]] (type: `calls` (*evidence: slots load data through the _get HTTP helper*))
- [[bridge_post|_post()]] (type: `calls` (*evidence: action slots persist through the _post HTTP helper*))
- [[ui_settings|offline_viewer/assets/ui_settings.json]] (type: `writes` (*evidence: _load_ui_settings/_save_ui_settings persist appearance/pins/folders/bin*))
- [[why_reader_font|Reader font separate from chat font]] (type: `explains` (*evidence: _readerFontFamily stored separately, falls back to chat font*))
- [[why_bin|Bin keeps deleted posts recoverable]] (type: `explains` (*evidence: _binned_items keep deleted posts recoverable across refresh*))
- [[ep_forward|POST /api/forward-to-telegram]] (type: `references` (*evidence: sendChannelToTelegram slot triggers the backend repost*))

## Incoming Connections
- [[app_main|main()]] (type: `instantiates` (*evidence: bridge = ChatBridge(chat_model, message_model, sources_model, ...)*))
- [[bridge|frontend/bridge.py]] (type: `contains` (*evidence: class ChatBridge in bridge.py*))
- [[Main.qml|frontend/qml/Main.qml]] (type: `references` (*evidence: bridge.theme/rtl/activeTab/currentChannelId + slot calls in Main.qml*))
- [[Theme|Theme (themes singleton)]] (type: `references` (*evidence: Binding { target: Theme; value: bridge.theme/rtl/fontFamily/... }*))
- [[FolderRail|FolderRail]] (type: `calls` (*evidence: onTabSelected -> bridge.setTab(tab)*))
- [[ChatList|ChatList]] (type: `calls` (*evidence: onOpenChat -> bridge.openChat(id)*))
- [[ChatView|ChatView]] (type: `calls` (*evidence: onForwardChannelRequested -> bridge.sendChannelToTelegram(id)*))
- [[ChatContextMenu|ChatContextMenu]] (type: `calls` (*evidence: onTogglePin/Mute/Archive/Delete -> bridge.**))
- [[SettingsView|SettingsView]] (type: `references` (*evidence: Settings page binds appearance/source settings to the bridge*))