---
status: accepted
---

# Use a local web application with CSV as the durable ledger

The application runs only on `127.0.0.1`: a Vue interface handles interaction while a thin Python application owns validation, analysis, backups, and atomic file replacement. The existing CSV schema remains the durable, human-readable source of truth because it is portable and already contains the complete history; a browser-only application was rejected because it cannot reliably reopen the configured file, preserve the existing Python invariants, or perform safe writes across browsers. A hosted application and database were rejected because a single-person ledger does not justify remote data custody or operational overhead.
