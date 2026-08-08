---
status: accepted
---

# Rename the CSV category header to `categories`

The durable CSV ledger uses
`date,account,type,amount,categories,tags,desc`. This replaces the misspelled
`categorys` header so the adapter, domain model, report data, and interface share
one canonical term.

This is an explicit, one-time migration rather than a compatibility alias. Before
running this version, the owner renames only the `categorys` header cell in
`transaction.csv` to `categories`; ledger rows and values remain unchanged.
Zaccount rejects the old header and never rewrites the working ledger.
