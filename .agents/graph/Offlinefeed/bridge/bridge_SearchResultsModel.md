---
id: "bridge:SearchResultsModel"
label: "SearchResultsModel"
type: "class"
community: "bridge"
location: "frontend/bridge.py:SearchResultsModel"
degree: 3
---

# SearchResultsModel

- **Type**: `class`
- **Community**: `bridge`
- **Location**: `frontend/bridge.py:SearchResultsModel`
- **Degree**: `3`

## Summary
List model for global search results.

## Outgoing Connections
*None*

## Incoming Connections
- [[app_main|main()]] (type: `instantiates` (*evidence: search_results_model = SearchResultsModel()*))
- [[bridge|frontend/bridge.py]] (type: `contains` (*evidence: class SearchResultsModel*))
- [[bridge_ChatBridge|ChatBridge]] (type: `references` (*evidence: search_results_model: Optional[SearchResultsModel]*))