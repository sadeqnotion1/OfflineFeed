---
id: "ReaderView"
label: "ReaderView"
type: "component"
community: "ui"
location: "frontend/qml/components/ReaderView.qml"
degree: 2
---

# ReaderView

- **Type**: `component`
- **Community**: `ui`
- **Location**: `frontend/qml/components/ReaderView.qml`
- **Degree**: `2`

## Summary
Full-body offline article reader overlay.

## Outgoing Connections
*None*

## Incoming Connections
- [[Main.qml|frontend/qml/Main.qml]] (type: `instantiates` (*evidence: ReaderView { id: reader }*))
- [[ChatView|ChatView]] (type: `calls` (*evidence: onReadArticleRequested -> reader.open(u,t,tx)*))