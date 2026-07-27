from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from .analysis import AnalysisResult, analyse
from .domain import LedgerEntry
from .ledger import load_ledger

REPORT_SCHEMA_VERSION = 1
REPORT_TEMPLATE = Path(__file__).with_name("report.html")


def _to_camel(name: str) -> str:
    first, *rest = name.split("_")
    return first + "".join(part.capitalize() for part in rest)


class ReportModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=_to_camel,
        frozen=True,
        populate_by_name=True,
    )


class ReportSource(ReportModel):
    file_name: str
    sha256: str
    entry_count: int
    first_entry_date: str | None
    last_entry_date: str | None


class ReportEntry(ReportModel):
    date: str
    account: str
    type: str
    amount: Decimal
    categories: tuple[str, ...]
    tags: tuple[str, ...]
    description: str

    @classmethod
    def from_ledger_entry(cls, entry: LedgerEntry) -> "ReportEntry":
        return cls(
            date=entry.date.isoformat(),
            account=entry.account,
            type=entry.type.value,
            amount=entry.amount,
            categories=entry.categories,
            tags=entry.tags,
            description=entry.description,
        )


class ReportData(ReportModel):
    schema_version: Literal[1] = REPORT_SCHEMA_VERSION
    generated_at: datetime
    source: ReportSource
    category_tree: dict[str, Any]
    analysis: AnalysisResult
    entries: tuple[ReportEntry, ...]


class GeneratedReport(ReportModel):
    data: ReportData
    json_path: Path
    html_path: Path


def build_report_data(
    entries: list[LedgerEntry],
    category_tree: dict[str, Any],
    ledger_path: Path,
    *,
    generated_at: datetime | None = None,
) -> ReportData:
    return ReportData(
        generated_at=generated_at or datetime.now().astimezone(),
        source=ReportSource(
            file_name=ledger_path.name,
            sha256=hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
            entry_count=len(entries),
            first_entry_date=entries[0].date.isoformat() if entries else None,
            last_entry_date=entries[-1].date.isoformat() if entries else None,
        ),
        category_tree=category_tree,
        analysis=analyse(entries),
        entries=tuple(ReportEntry.from_ledger_entry(entry) for entry in entries),
    )


def report_json(data: ReportData) -> str:
    return data.model_dump_json(by_alias=True, indent=2)


def render_report_html(data: ReportData) -> str:
    serialized = report_json(data)
    embedded = (
        serialized.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    template = REPORT_TEMPLATE.read_text(encoding="utf-8")
    marker = "__ZACCOUNT_REPORT_DATA__"
    if template.count(marker) != 1:
        raise ValueError("报告模板缺少唯一的数据标记")
    return template.replace(marker, embedded)


def generate_report(
    ledger_path: Path,
    category_tree: dict[str, Any],
    output_dir: Path,
    *,
    generated_at: datetime | None = None,
) -> GeneratedReport:
    entries = load_ledger(ledger_path, category_tree)
    data = build_report_data(
        entries,
        category_tree,
        ledger_path,
        generated_at=generated_at,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "report.json"
    html_path = output_dir / "report.html"
    _atomic_write_text(json_path, report_json(data) + "\n")
    _atomic_write_text(html_path, render_report_html(data))
    return GeneratedReport(data=data, json_path=json_path, html_path=html_path)


def _atomic_write_text(path: Path, content: str) -> None:
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=f".{path.stem}_",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()
