from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .analysis import LedgerFilter, analyse
from .domain import EntryDraft, EntryType, TransferDraft
from .ledger import LedgerError, LedgerStore
from .settings import PROJECT_ROOT, get_data_dir, load_category_tree


def create_app(
    *,
    data_dir: Path | None = None,
    frontend_dir: Path | None = None,
) -> FastAPI:
    category_tree = load_category_tree()
    store = LedgerStore(data_dir or get_data_dir(), category_tree)
    app = FastAPI(title="Zaccount", docs_url="/api/docs")
    app.state.store = store
    app.state.category_tree = category_tree

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.exception_handler(LedgerError)
    async def handle_ledger_error(
        _request: Request, error: LedgerError
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(error)})

    @app.get("/api/bootstrap")
    def bootstrap() -> dict[str, Any]:
        entries = store.load()
        accounts = sorted({entry.account for entry in entries})
        tags = sorted({tag for entry in entries for tag in entry.tags})
        public_entries = [
            entry.to_public_dict(row_number=index)
            for index, entry in reversed(list(enumerate(entries, start=2)))
        ]
        return {
            "entries": public_entries,
            "meta": {
                "accounts": accounts,
                "tags": tags,
                "categoryTree": category_tree,
                "dataFile": str(store.path),
            },
            "analysis": analyse(entries),
        }

    @app.get("/api/analysis")
    def get_analysis(
        start_date: date | None = None,
        end_date: date | None = None,
        account: str | None = None,
        entry_type: Annotated[EntryType | None, Query(alias="type")] = None,
        category: str | None = None,
        tag: str | None = None,
        query: str | None = None,
    ) -> dict[str, Any]:
        ledger_filter = LedgerFilter(
            start_date=start_date,
            end_date=end_date,
            account=account or None,
            type=entry_type,
            category=category or None,
            tag=tag or None,
            query=query or None,
        )
        return analyse(store.load(), ledger_filter)

    @app.post("/api/entries", status_code=201)
    def add_entry(draft: EntryDraft) -> dict[str, Any]:
        entry = store.add_entry(draft)
        return {"entry": entry.to_public_dict()}

    @app.post("/api/transfers", status_code=201)
    def add_transfer(draft: TransferDraft) -> dict[str, Any]:
        outgoing, incoming = store.add_transfer(draft)
        return {
            "entries": [
                outgoing.to_public_dict(),
                incoming.to_public_dict(),
            ]
        }

    resolved_frontend = frontend_dir or PROJECT_ROOT / "frontend" / "dist"
    assets_dir = resolved_frontend / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{path:path}", include_in_schema=False, response_model=None)
    def serve_frontend(path: str) -> FileResponse | JSONResponse:
        index_path = resolved_frontend / "index.html"
        requested = (resolved_frontend / path).resolve()
        if (
            path
            and requested.is_relative_to(resolved_frontend.resolve())
            and requested.is_file()
        ):
            return FileResponse(requested)
        if index_path.is_file():
            return FileResponse(index_path)
        return JSONResponse(
            status_code=503,
            content={
                "detail": "前端尚未构建，请运行 cd frontend && npm install && npm run build"
            },
        )

    return app


app = create_app()
