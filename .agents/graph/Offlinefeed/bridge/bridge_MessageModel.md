---
id: "bridge:MessageModel"
label: "MessageModel"
type: "class"
community: "bridge"
location: "frontend/bridge.py:MessageModel"
degree: 4
---

# MessageModel

- **Type**: `class`
- **Community**: `bridge`
- **Location**: `frontend/bridge.py:MessageModel`
- **Degree**: `4`

## Summary
List model backing the right pane: articles/posts of the selected channel.

## Outgoing Connections
*None*

## Incoming Connections
- [[app_main|main()]] (type: `instantiates` (*evidence: message_model = MessageModel()*))
- [[bridge|frontend/bridge.py]] (type: `contains` (*evidence: class MessageModel*))
- [[bridge_ChatBridge|ChatBridge]] (type: `references` (*evidence: ChatBridge.__init__(message_model: MessageModel, ...)*))
- [[ChatView|ChatView]] (type: `references` (*evidence: ChatView renders messageModel posts*))