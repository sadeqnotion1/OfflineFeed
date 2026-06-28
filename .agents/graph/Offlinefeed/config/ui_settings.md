---
id: "ui_settings"
label: "offline_viewer/assets/ui_settings.json"
type: "config"
community: "config"
location: "offline_viewer/assets/ui_settings.json"
degree: 5
---

# offline_viewer/assets/ui_settings.json

- **Type**: `config`
- **Community**: `config`
- **Location**: `offline_viewer/assets/ui_settings.json`
- **Degree**: `5`

## Summary
Persisted UI settings (appearance, language, advanced.backend_port, pins, folders, bin). Read across launcher, app, bridge and doctor.

## Outgoing Connections
*None*

## Incoming Connections
- [[run_offlinefeed_main|main()]] (type: `reads` (*evidence: reads advanced.backend_port from offline_viewer/assets/ui_settings.json*))
- [[app_get_backend_port|get_backend_port() [app]]] (type: `reads` (*evidence: reads advanced.backend_port from ui_settings.json*))
- [[doctor_main|main()]] (type: `reads` (*evidence: reads advanced.backend_port from ui_settings.json*))
- [[bridge_ChatBridge|ChatBridge]] (type: `writes` (*evidence: _load_ui_settings/_save_ui_settings persist appearance/pins/folders/bin*))
- [[bridge_get_backend_port|get_backend_port() [bridge]]] (type: `reads` (*evidence: reads advanced.backend_port from ui_settings.json*))