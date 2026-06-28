---
id: "bridge:ChatListModel"
label: "ChatListModel"
type: "class"
community: "bridge"
location: "frontend/bridge.py:ChatListModel"
degree: 5
---

# ChatListModel

- **Type**: `class`
- **Community**: `bridge`
- **Location**: `frontend/bridge.py:ChatListModel`
- **Degree**: `5`

## Summary
List model backing the channel list (incl. Saved Messages + System Logs).

## Outgoing Connections
*None*

## Incoming Connections
- [[app_main|main()]] (type: `instantiates` (*evidence: chat_model = ChatListModel()*))
- [[bridge|frontend/bridge.py]] (type: `contains` (*evidence: class ChatListModel*))
- [[bridge_ChatBridge|ChatBridge]] (type: `references` (*evidence: ChatBridge.__init__(chat_model: ChatListModel, ...)*))
- [[ChatList|ChatList]] (type: `references` (*evidence: ChatList is bound to chatModel exposed from bridge*))
- [[avatar_fetcher_backfill_avatars|backfill_avatars()]] (type: `references` (*evidence: avatars backfilled are shown via ChatListModel avatarPath*))