---
id: "run_offlinefeed:main"
label: "main()"
type: "function"
community: "bootstrap"
location: "run_offlinefeed.py:38"
degree: 7
---

# main()

- **Type**: `function`
- **Community**: `bootstrap`
- **Location**: `run_offlinefeed.py:38`
- **Degree**: `7`

## Summary
Parses flags (--doctor/--force/--refresh-avatars), runs the doctor, refuses to launch on FAIL, then runs the GUI as a child process.

## Outgoing Connections
- [[debug_run_diagnostics|run_diagnostics()]] (type: `calls` (*evidence: report = debug.run_diagnostics(port=port)*))
- [[debug_install_excepthooks|install_excepthooks()]] (type: `calls` (*evidence: debug.install_excepthooks()*))
- [[avatar_fetcher_backfill_avatars|backfill_avatars()]] (type: `calls` (*evidence: from frontend.avatar_fetcher import backfill_avatars; backfill_avatars(...)*))
- [[app|frontend/app.py]] (type: `depends_on` (*evidence: subprocess.run([sys.executable, '-m', 'frontend.app'])*))
- [[ui_settings|offline_viewer/assets/ui_settings.json]] (type: `reads` (*evidence: reads advanced.backend_port from offline_viewer/assets/ui_settings.json*))
- [[log_file|logs/offlinefeed_debug.log]] (type: `reads` (*evidence: _tail(debug.LOG_FILE) printed on non-zero exit*))

## Incoming Connections
- [[run_offlinefeed|run_offlinefeed.py]] (type: `contains` (*evidence: def main() in run_offlinefeed.py*))