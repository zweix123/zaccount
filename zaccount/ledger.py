from __future__ import annotations

import csv
import os
import shutil
import stat
import tempfile
import threading
from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from .domain import EntryDraft, EntryType, LedgerEntry, TransferDraft

CSV_FIELDS = ["date", "account", "type", "amount", "categorys", "tags", "desc"]


class LedgerError(Exception):
    """A user-correctable ledger or storage failure."""


class LedgerStore:
    def __init__(self, data_dir: Path, category_tree: dict[str, dict]) -> None:
        self.data_dir = data_dir
        self.category_tree = category_tree
        self.path = data_dir / "transaction.csv"
        self._lock = threading.Lock()

    def load(self) -> list[LedgerEntry]:
        if not self.path.exists():
            raise LedgerError(f"找不到数据文件：{self.path}")

        entries: list[LedgerEntry] = []
        with self.path.open(encoding="utf-8-sig", newline="") as file:
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

        self._validate(entries, require_sorted=True)
        return entries

    def add_entry(self, draft: EntryDraft) -> LedgerEntry:
        entry = draft.to_entry()
        self._commit_additions([entry])
        return entry

    def add_transfer(
        self, draft: TransferDraft
    ) -> tuple[LedgerEntry, LedgerEntry]:
        try:
            entries = draft.to_entries()
        except ValueError as error:
            raise LedgerError(str(error)) from error
        self._commit_additions(entries)
        return entries

    def _commit_additions(self, additions: Iterable[LedgerEntry]) -> None:
        with self._lock:
            entries = self.load()
            candidate = sorted([*entries, *additions], key=lambda entry: entry.date)
            self._validate(candidate, require_sorted=True)
            self._backup()
            self._atomic_write(candidate)

    def _validate(
        self, entries: list[LedgerEntry], *, require_sorted: bool
    ) -> None:
        previous_date = None
        internal_in = Decimal("0")
        internal_out = Decimal("0")

        for index, entry in enumerate(entries, start=2):
            if require_sorted and previous_date and previous_date > entry.date:
                raise LedgerError(f"第 {index} 行日期早于前一条账目")
            previous_date = entry.date

            node = self.category_tree.get(entry.type.value)
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

    def _backup(self) -> None:
        backup_dir = self.data_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S_%f")
        shutil.copy2(self.path, backup_dir / f"transaction_{stamp}.csv")

    def _atomic_write(self, entries: list[LedgerEntry]) -> None:
        temporary_path: Path | None = None
        mode = stat.S_IMODE(self.path.stat().st_mode)
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                prefix=".transaction_",
                suffix=".tmp",
                dir=self.data_dir,
                delete=False,
            ) as file:
                temporary_path = Path(file.name)
                writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
                writer.writeheader()
                writer.writerows(entry.to_csv_row() for entry in entries)
                file.flush()
                os.fsync(file.fileno())
            os.chmod(temporary_path, mode)
            os.replace(temporary_path, self.path)
        except OSError as error:
            raise LedgerError(f"保存账本失败：{error}") from error
        finally:
            if temporary_path and temporary_path.exists():
                temporary_path.unlink()
