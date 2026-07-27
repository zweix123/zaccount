---
status: accepted
---

# Generate a static interactive report instead of running a local web application

The owner edits a copied working CSV directly and uses the project primarily for
analysis. Zaccount therefore validates the configured ledger and generates
`report.json` plus a standalone interactive `report.html`. The HTML embeds the
normalized entries and category tree so combined filters can be evaluated locally
without a server or network access.

The former FastAPI and Vue application is removed, including all ledger write
interfaces. A pre-aggregated, non-interactive report was rejected because it cannot
support arbitrary combinations of time, account, type, category-path, tag, and
description filters. A Skill was rejected because generation is already fast and a
normal command is easier to test, reuse, and run outside an Agent.

Generated artifacts contain private ledger details and are treated with the same
care as `transaction.csv`. They remain outside version control.
