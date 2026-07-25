# Repository Guidelines

## Product and Domain

Zaccount is a local-first personal ledger. A Vue interface handles entry, browsing, and analysis while a Python application owns validation, aggregation, backups, and CSV persistence. The application binds to `127.0.0.1`; do not introduce cloud storage, telemetry, remote assets, or multi-user concepts without an explicit product decision.

Use the canonical terminology in `CONTEXT.md`: ledger entry, account, type, category path, tag, description, transfer, and ledger. Product scope and module decisions live in `docs/product-design.md` and `docs/adr/`.

## Project Structure and Module Organization

- `zaccount/__main__.py` is the application entry point for `python -m zaccount`.
- `zaccount/domain.py` defines ledger entries, entry types, drafts, signed amounts, and paired transfers.
- `zaccount/ledger.py` is the only module that reads or writes the durable CSV ledger. It owns complete-ledger validation, sorting, backups, locking, and atomic replacement.
- `zaccount/analysis.py` owns shared filtering and all financial aggregations.
- `zaccount/api.py` is a thin FastAPI adapter. Keep domain and storage rules out of HTTP handlers.
- `zaccount/settings.py` resolves `DATA_DIR` and loads `config/ctg.jsonc`.
- `frontend/src/components/` is organized by feature: `entry`, `ledger`, `analysis`, and `shell`.
- `frontend/src/composables/useLedger.ts` owns remote state and mutation actions. `frontend/src/api.ts` is the HTTP adapter.
- `tests/` contains Python behavior tests. Vue component tests are colocated as `*.test.ts`.
- `entry.py` and `utils.py` are legacy compatibility modules. Do not add new application behavior to them.

Runtime transaction data lives in the directory selected by `DATA_DIR`, defaulting to `data/`. The working file is `transaction.csv`; mutation backups are written beneath that data directory. Never commit personal financial data, `.env`, backups, `frontend/dist`, `frontend/node_modules`, generated output, or caches.

## Setup, Build, and Development Commands

- `uv sync` installs the locked Python 3.13+ environment from `pyproject.toml` and `uv.lock`.
- `cp .env.example .env` creates local configuration; set `DATA_DIR` to the directory containing `transaction.csv`.
- `cd frontend && npm install` installs the exact frontend graph recorded in `package-lock.json`.
- `cd frontend && npm run build` type-checks Vue and creates the production bundle consumed by Python.
- `uv run python -m zaccount` starts the built local application and opens `http://127.0.0.1:8000`.
- `uv run python -m zaccount --no-browser --reload` starts the backend in development mode.
- `cd frontend && npm run dev` starts Vite on `127.0.0.1:5173` and proxies `/api` to port 8000.

Commit both lockfiles when dependencies change: `uv.lock` for Python and `frontend/package-lock.json` for Node.

## Data and Storage Invariants

The legacy CSV field order is:

```text
date,account,type,amount,categorys,tags,desc
```

Keep the misspelled `categorys` name at the CSV adapter seam. Use `categories` and “category path” everywhere else. Do not change the durable schema without a documented migration that preserves existing personal data.

Amounts are positive decimals. Their sign comes from the type: income and transfer-in add funds; expense and transfer-out subtract funds. Category paths must be valid prefixes of the tree for their type. Ledger entries remain in ascending date order while preserving insertion order within a date.

An internal transfer is one user intent represented by an equal `转出 / 内转` and `转入 / 内转` pair. Never expose or implement a write path that can commit only one side.

Every mutation must go through `LedgerStore` and retain this sequence:

1. lock the ledger;
2. load and validate the current complete ledger;
3. build, sort, and validate the complete candidate ledger;
4. back up the current CSV;
5. write and flush a temporary file in the same directory;
6. atomically replace `transaction.csv`.

Reads must not create backups or modify the ledger.

## Python Style and Module Design

Follow standard Python style: four-space indentation, `snake_case` functions and variables, `PascalCase` classes, uppercase constants, and type annotations on public interfaces. Use UTF-8 for Chinese domain values.

Keep modules deep:

- callers express entry, transfer, or analysis intent;
- `LedgerStore` hides CSV rows, ordering, validation, backup, and replacement mechanics;
- `analyse()` hides aggregation details behind one filter-and-result interface;
- FastAPI handlers translate JSON and errors only.

Prefer `Decimal` for money. Do not reintroduce float arithmetic into domain or storage logic; convert to JSON numbers only at the adapter seam.

## Vue and TypeScript Style

Use Vue 3 Composition API with `<script setup lang="ts">`. Keep `App.vue` and workspace components as composition surfaces. Split substantial forms, filters, lists, and charts into focused components.

- Keep source state minimal and derive display state with `computed`.
- Use props down and typed events up; do not mutate props.
- Put reusable or side-effect-heavy feature state in composables.
- Keep remote writes and refreshes in `useLedger`.
- Use stable keys and user-visible, accessible controls.
- Preserve keyboard focus, visible focus states, responsive layouts, and reduced-motion behavior.
- Do not load web fonts, analytics, chart CDNs, or other remote assets.

The visual language is defined in `docs/product-design.md` and `frontend/src/styles.css`. Reuse its paper, ink, blue, expense, income, and rule tokens rather than adding arbitrary near-duplicate colors.

## Testing Guidelines

Run the complete verification set for behavioral changes:

```bash
uv run pytest
cd frontend
npm run test:run
npm run build
```

Use temporary directories for every storage or API mutation test. Never write test entries to `.env`'s `DATA_DIR` or depend on the real ledger's contents. Test successful behavior and invariant failures, especially invalid category paths, ordering, unchanged files after failed validation, backups, and balanced transfer pairs.

Vue tests use Vitest and Vue Test Utils. Exercise components through visible controls and emitted events rather than internal state or private methods. Await user interactions and asynchronous refreshes.

For a quick Python syntax check, run:

```bash
uv run python -m compileall zaccount entry.py utils.py
```

## Commit and Pull Request Guidelines

Use concise, imperative Conventional Commit subjects such as `feat: ...`, `fix: ...`, `docs: ...`, and scoped forms such as `refactor(storage): ...`. Keep each commit focused.

Pull requests should explain the user-visible effect, list verification commands, and call out changes to the CSV schema, storage invariants, `config/ctg.jsonc`, or the local-only guarantee. Include screenshots when the interface or charts change. Never include real ledger contents in screenshots, fixtures, logs, or review descriptions.
