from __future__ import annotations

import csv
import os
import shutil
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

from .domain import EntryType, LedgerEntry

CSV_FIELDS = ["date", "account", "type", "amount", "categories", "tags", "desc"]


class LedgerError(Exception):
    """A user-correctable ledger or storage failure."""


def load_ledger(
    path: Path, category_tree: dict[str, dict]
) -> list[LedgerEntry]:
    if not path.exists():
        raise LedgerError(f"找不到数据文件：{path}")

    _ensure_daily_backup(path)

    entries: list[LedgerEntry] = []
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != CSV_FIELDS:
            raise LedgerError(
                f"CSV 字段不匹配，期望 {','.join(CSV_FIELDS)}，"
                f"实际 {','.join(reader.fieldnames or [])}"
            )
        for row in reader:
            try:
                entries.append(LedgerEntry.from_csv_row(row))
            except Exception as error:
                raise LedgerError(
                    f"第 {reader.line_num} 行无法读取：{error}"
                ) from error

    _validate_ledger(entries, category_tree)
    return entries


def _ensure_daily_backup(path: Path) -> None:
    backup_path = path.with_name(
        f"{path.stem}_{date.today().isoformat()}{path.suffix}"
    )
    if backup_path.exists():
        return

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{backup_path.stem}_",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
        shutil.copy2(path, temporary_path)
        try:
            os.link(temporary_path, backup_path)
        except FileExistsError:
            # Another analysis may have created today's backup concurrently.
            pass
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()


def _validate_ledger(
    entries: list[LedgerEntry], category_tree: dict[str, dict]
) -> None:
    previous_date = None
    internal_in = Decimal("0")
    internal_out = Decimal("0")

    for index, entry in enumerate(entries, start=2):
        if previous_date and previous_date > entry.date:
            raise LedgerError(f"第 {index} 行日期早于前一条账目")
        previous_date = entry.date

        node = category_tree.get(entry.type.value)
        if node is None:
            raise LedgerError(f"第 {index} 行类型不存在：{entry.type.value}")
        for category in entry.categories:
            if category not in node:
                path = " / ".join(entry.categories)
                raise LedgerError(
                    f"第 {index} 行类别路径无效：{entry.type.value} / {path}"
                )
            node = node[category]

        if (
            entry.type is EntryType.TRANSFER_IN
            and entry.categories[0] == "内转"
        ):
            internal_in += entry.amount
        if (
            entry.type is EntryType.TRANSFER_OUT
            and entry.categories[0] == "内转"
        ):
            internal_out += entry.amount

    if internal_in != internal_out:
        raise LedgerError(
            "内转不平衡："
            f"转入 {format(internal_in, 'f')}，"
            f"转出 {format(internal_out, 'f')}"
        )
