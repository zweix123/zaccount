# Zaccount local ledger

## Outcome

Zaccount becomes one local application that replaces both the command-oriented `dryadsfile` entry point and the exploratory `report.ipynb`.

The first usable release must let its owner:

1. record an income or expense without editing CSV;
2. record a transfer as one action that creates a balanced pair;
3. browse and filter the complete ledger;
4. understand totals, monthly expense movement, category distribution, tag distribution, and account balances;
5. keep `transaction.csv` portable and recoverable.

The application contains no cloud sync, authentication, multi-user concepts, budget planning, entry editing, or deletion in the first release.

## Product principles

- **Local is a data guarantee.** The server binds to `127.0.0.1`; the interface loads no remote assets and the ledger never leaves the machine.
- **One action, one intent.** Ordinary entries and transfers have separate forms because a transfer is not merely an entry with a different label.
- **Classification follows the model.** Type controls the available category tree; tags remain independent and optional.
- **The CSV is an export and a source of truth.** The interface never exposes CSV mechanics during normal use.
- **Analysis must lead back to evidence.** Filters apply consistently to summaries, charts, and the visible entry list.
- **Failed writes leave the ledger untouched.** The complete candidate ledger is validated before an atomic replacement.

## Domain rules

The canonical language is recorded in [`CONTEXT.md`](../CONTEXT.md).

- An amount is positive and stored as decimal text.
- Dates use `YYYY-MM-DD`.
- Ledger entries are kept in ascending date order. Entries on the same date preserve insertion order.
- A category path must be a valid prefix in the tree for its type.
- Tags are trimmed, independent labels; an empty tag collection is valid.
- Income and transfer-in add to an account balance.
- Expense and transfer-out subtract from an account balance.
- Every internal transfer is created as an equal transfer-out and transfer-in pair.
- The legacy CSV header remains `date,account,type,amount,categorys,tags,desc`. The misspelt `categorys` name is an adapter concern and does not enter the domain language.

## First-release journeys

### Record an ordinary entry

The amount field receives focus. The date defaults to today. The owner selects a type, account, category path, optional tags, and description, then chooses “保存账目”. The application validates the candidate ledger, makes a timestamped backup, replaces the working CSV, refreshes all views, and confirms the saved entry.

### Record a transfer

The owner switches to “账户转账”, selects different source and destination accounts, enters a positive amount, date, tags, and description, then chooses “保存转账”. One operation creates the matched `转出 / 内转` and `转入 / 内转` entries. No half-transfer can be written.

### Find entries

The owner filters by date range, account, type, category prefix, tag, or description text. The newest matching entries appear first. Clearing filters returns to the full ledger.

### Analyse spending

The same filters drive:

- income, expense, and net-change totals;
- account balances;
- monthly expense movement;
- expense totals by first-level category;
- expense totals by tag.

Selecting no tags does not create a fake “untagged” tag.

## Architecture

```text
Vue interface
    │  JSON over same-origin HTTP
    ▼
Local application
    ├── Ledger module
    │     validate → sort → back up → atomic replace
    ├── Analysis module
    │     filter → aggregate → serialize
    └── CSV adapter
          transaction.csv + timestamped backups
```

The **Ledger module** is the principal deep module. Its interface exposes loading the ledger, adding one ordinary entry, and adding one transfer. Callers do not manage CSV rows, ordering, full-ledger invariants, backups, temporary files, or replacement.

The **Analysis module** accepts ledger entries plus a filter and returns a single analysis result. Account, monthly, category, and tag aggregation are implementation details behind that interface.

The HTTP layer is an adapter. It translates JSON and errors but owns no ledger rules. Vue is also an adapter: it presents domain operations rather than reproducing their validation.

## Interface map

```text
App
├── AppNavigation
├── EntryWorkspace
│   ├── EntryModeSwitch
│   ├── EntryForm
│   └── TransferForm
├── LedgerWorkspace
│   ├── LedgerFilters
│   └── EntryTable
└── AnalysisWorkspace
    ├── SummaryRail
    ├── MonthlyTrend
    ├── CategoryBars
    ├── TagBars
    └── AccountBalances
```

- `App` composes views and owns navigation only.
- `useLedger` owns remote state, loading, saving, errors, and refresh actions.
- Forms own drafts and emit validated user intent upward.
- Filters are controlled state: values go down and changes come up.
- Analysis components receive immutable result data and contain no fetching logic.

## Visual direction

The interface resembles a precise personal ledger rather than a generic administration dashboard.

### Tokens

- paper: `#F4F6FA`
- surface: `#FFFFFF`
- ink: `#17233B`
- muted ink: `#68738A`
- ledger blue: `#3157D5`
- expense coral: `#DE6255`
- income teal: `#238674`
- rule: `#DDE3EE`

Chinese body text uses the local `PingFang SC` stack. Restrained headings use `Songti SC` to evoke a personal book without turning the interface into a newspaper. Amounts and compact labels use `SFMono-Regular` with tabular numerals.

The signature element is a horizontal **funds scale**: a fine ruled line with income and expense marks that becomes the monthly trend in the analysis view. Motion is limited to one view-entry sequence and respects reduced-motion preferences.

## Storage safety

For every mutation:

1. acquire the in-process ledger lock;
2. read and validate the existing complete ledger;
3. build and validate the complete candidate ledger;
4. copy the current CSV to `backups/` with a timestamped name;
5. write the candidate to a temporary file in the same directory;
6. flush and atomically replace `transaction.csv`;
7. return the committed result.

Read operations never create backups. Tests use a temporary directory and never touch the configured personal ledger.

## Verification

- Domain tests cover valid and invalid dates, amounts, category paths, and transfer pairs.
- Storage tests assert sorting, backups, atomic observable results, and unchanged files after validation failure.
- Analysis tests cover filters and signed totals.
- Vue component tests exercise forms and filters through visible controls and emitted events.
- One browser test covers loading the real application against a temporary ledger, adding an expense, and observing refreshed analysis.

## Later work

- Stable entry IDs followed by edit, delete, and undo.
- Saved entry templates and keyboard-first quick entry.
- Comparisons with previous month and previous year.
- Import review for payment-platform exports.
- Optional migration from CSV if write volume or cross-device use eventually makes a database worthwhile.
