# Repository Guidelines

## Product and Domain

Zaccount is a local-first personal ledger analysis tool. Python validates the
durable CSV ledger, calculates financial aggregates, and generates a versioned JSON
artifact plus a standalone interactive HTML report. The generated report runs
entirely in the browser without a server. Do not introduce cloud storage,
telemetry, remote assets, HTTP services, or multi-user concepts without an explicit
product decision.

Use the canonical terminology in `CONTEXT.md`: ledger entry, account, type,
category path, tag, description, transfer, and ledger. Product scope and module
decisions live in `docs/product-design.md` and `docs/adr/`.

## Project Structure and Module Organization

- `zaccount/__main__.py` is the report command entry point for
  `python -m zaccount`.
- `zaccount/domain.py` defines ledger entries, entry types, and signed amounts.
- `zaccount/ledger.py` is the only module that reads the durable CSV ledger. It
  owns daily pre-analysis snapshots plus field, ordering, category-path, and
  transfer-balance validation.
- `zaccount/analysis.py` owns shared filtering and financial aggregations.
- `zaccount/reporting.py` owns the versioned report data, source fingerprint,
  safe serialization, template rendering, and atomic artifact replacement.
- `zaccount/report.html` is the zero-dependency report adapter. It contains only
  local CSS and JavaScript.
- `zaccount/settings.py` resolves `DATA_DIR` and loads `config/ctg.jsonc`.
- `tests/` contains Python behavior tests.

Runtime data lives in the directory selected by `DATA_DIR`, defaulting to `data/`.
The working file is `transaction.csv`. Generated artifacts default to `output/`.
Never commit personal financial data, `.env`, report artifacts, screenshots of real
reports, generated output, or caches.

## Setup, Generation, and Verification

- `uv sync` installs the locked Python 3.13+ environment.
- `cp .env.example .env` creates local configuration; set `DATA_DIR` to the
  directory containing `transaction.csv`.
- `uv run python -m zaccount` generates `output/report.json` and
  `output/report.html`.
- `uv run python -m zaccount --open` generates and opens the HTML report.
- `uv run pytest` runs the complete behavior suite.
- `uv run python -m compileall zaccount` performs a quick syntax check.

Commit `uv.lock` when dependencies change.

## Data Invariants

The legacy CSV field order is:

```text
date,account,type,amount,categorys,tags,desc
```

Keep the misspelled `categorys` name at the CSV adapter seam. Use `categories` and
“category path” everywhere else. Do not change the durable schema without a
documented migration that preserves existing personal data.

Amounts are positive decimals. Initial balance, income, and transfer-in add funds;
expense and transfer-out subtract funds. Initial balances have no category and are
not income. Category paths must be valid prefixes of the tree for their type.
Ledger entries remain in ascending date order while preserving insertion order
within a date.

An internal transfer is one intent represented by equal `转出 / 内转` and
`转入 / 内转` totals. Report generation rejects an unbalanced ledger.

Reads and report generation must never modify the working ledger. Before analysis,
create `transaction_YYYY-MM-DD.csv` beside it if that day's snapshot does not
already exist; never overwrite an existing daily snapshot. Report artifacts are
written through temporary files in the output directory and atomically replaced.

## Python Style and Module Design

Follow standard Python style: four-space indentation, `snake_case` functions and
variables, `PascalCase` classes, uppercase constants, and type annotations on
public interfaces. Use UTF-8 for Chinese domain values.

Keep modules deep:

- callers express the intent to generate one report;
- the Report generation module hides loading, validation, calculation,
  fingerprinting, serialization, escaping, and output replacement;
- `load_ledger()` hides CSV rows and complete-ledger validation;
- `analyse()` hides aggregation details behind one filter-and-result interface.

Prefer `Decimal` for money. Report JSON serializes money as decimal strings.
Browser calculations must use integer minor units rather than binary floating-point
addition.

## Report HTML Style

The report uses semantic, accessible HTML and dependency-free JavaScript.

- Keep source filter state minimal and derive every view from the filtered entries.
- Treat the embedded JSON as untrusted text; never interpolate ledger values into
  `innerHTML`.
- Preserve keyboard focus, visible focus states, responsive layouts, printing, and
  reduced-motion behavior.
- Do not load web fonts, analytics, chart CDNs, frameworks, or other remote assets.
- Reuse the paper, ink, blue, expense, income, and rule tokens documented in
  `docs/product-design.md`.
- Selecting a category matches its complete path prefix and descendants.
- Selecting multiple tags uses all-selected semantics and must be stated in the
  interface.

## Testing Guidelines

Run:

```bash
uv run pytest
uv run python -m compileall zaccount
```

Use temporary directories for storage and report tests. Never read or write the
real ledger in automated tests. Cover successful behavior and invariant failures,
  especially daily snapshot preservation, invalid category paths, ordering,
  unbalanced transfers, decimal serialization, HTML data escaping, source-path
  privacy, and output replacement.

Browser verification uses synthetic data. Never include real ledger contents in
screenshots, fixtures, logs, or review descriptions.

## Commit and Pull Request Guidelines

Use concise, imperative Conventional Commit subjects such as `feat: ...`,
`fix: ...`, `docs: ...`, and scoped forms such as `refactor(report): ...`. Keep each
commit focused.

Pull requests should explain the user-visible effect, list verification commands,
and call out changes to the report schema, CSV schema, validation invariants,
`config/ctg.jsonc`, or the local-only guarantee.
