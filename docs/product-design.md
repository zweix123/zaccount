# Zaccount static analysis report

## Outcome

Zaccount turns a validated local CSV ledger into a disposable interactive report.
The owner edits the working data file directly, runs one fast command, and opens a
new snapshot without starting or maintaining an application service.

The report must let its owner:

1. understand income, expense, net change, account balances, monthly expense,
   category distribution, and tag distribution;
2. combine date, account, type, category-path, tag, and description filters;
3. trace every result back to the matching ledger entries;
4. regenerate the complete result from `transaction.csv` in one command;
5. keep all source data and generated artifacts local.

There is no entry form, write interface, HTTP server, cloud sync, authentication,
telemetry, multi-user model, or database.

## Product principles

- **Generation is the refresh action.** A report is a snapshot, not a long-running
  application that synchronizes itself.
- **Local is a data guarantee.** The report contains no remote assets or network
  requests.
- **Analysis leads back to evidence.** Every filter updates summaries, charts, and
  the visible entry list together.
- **One calculation model.** Initial rendering and browser interaction follow the
  same type signs and category-prefix rules.
- **The source is read-only.** Report generation validates but never modifies,
  copies, or backs up the ledger.
- **Generated output is private.** The report embeds the fields required for
  interactive analysis and must be protected like the source CSV.

## Domain rules

The canonical language is recorded in [`CONTEXT.md`](../CONTEXT.md).

- Amounts are positive decimal text.
- Initial balance, income, and transfer-in add funds.
- Expense and transfer-out subtract funds.
- Initial balance has no category and is not counted as income.
- Dates use `YYYY-MM-DD` and remain in ascending order.
- A category path is a valid prefix of the fixed tree for its type.
- Selecting a category in the report matches that path and every descendant.
- Selecting multiple tags requires a ledger entry to contain every selected tag.
- Internal transfer-in and transfer-out totals must balance.
- The durable header remains `date,account,type,amount,categorys,tags,desc`.

## Architecture

```text
transaction.csv + category tree
              │
              ▼
      Report generation module
      ├── read and validate ledger
      ├── calculate canonical totals
      ├── create versioned report data
      └── atomically write both artifacts
              │
              ├── report.json
              └── report.html
                    └── local browser filtering and rendering
```

The **Report generation module** is the principal deep module. Its interface accepts
the ledger path, category tree, and output directory. Callers do not manage CSV
rows, validation order, serialization, template escaping, fingerprints, or atomic
output replacement.

The **Ledger module** is a read-only adapter for the durable CSV seam. The
**Analysis module** is pure in-process calculation. The HTML renderer is an
offline adapter over the versioned report data; it does not become a second source
of durable truth.

## Report data contract

`report.json` has a top-level `schemaVersion`. Money is serialized as decimal
strings. It contains:

- generation time;
- source file name, date range, entry count, and SHA-256 fingerprint;
- the category tree;
- canonical full-ledger analysis;
- normalized entries required for arbitrary local filtering.

The absolute source path is deliberately excluded. The HTML embeds the exact same
JSON after escaping characters that could terminate its data script.

## Interaction

Filters apply immediately with no submit action:

- start and end dates, plus year shortcuts;
- one account and one type;
- one category path at any depth;
- any number of tags, with all-selected semantics;
- description text.

Changing a filter updates the funds scale, summary totals, account movements,
monthly expense, category drill-down, tag distribution, and evidence table.
When a start date is selected, account results are labelled as interval movement
instead of current balance.

## Visual direction

The report resembles a precise personal ledger rather than an administration
dashboard. It uses local system typefaces and these tokens:

- paper: `#F2F5F9`
- surface: `#FFFFFF`
- ink: `#17233B`
- ledger blue: `#3157D5`
- expense coral: `#D9584D`
- income teal: `#1D806E`
- rule: `#D9E0EB`

Its signature is the **funds scale**: expense extends left from zero and income
extends right, making the current filtered relationship visible before reading
individual values. Motion is limited to value and bar transitions and respects
reduced-motion preferences.

## Verification

- Domain and ledger tests cover decimal signs, initial balances, fields, ordering,
  category paths, and transfer balance.
- Analysis tests cover shared filters and category prefix semantics.
- Reporting tests cover schema version, decimal serialization, source privacy,
  template escaping, CLI output, and standalone artifacts.
- Browser verification covers combined date, tag, and category interaction at
  desktop and mobile widths using synthetic data.
