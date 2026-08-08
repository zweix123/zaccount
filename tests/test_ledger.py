from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from zaccount.domain import EntryType
from zaccount.ledger import CSV_FIELDS, LedgerError, load_ledger


CATEGORY_TREE = {
    "初始": {},
    "收入": {"工资": {}},
    "支出": {"餐饮": {"午饭": {}}},
    "转入": {"内转": {}},
    "转出": {"内转": {}},
}


def write_ledger(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def row(**overrides: str) -> dict[str, str]:
    values = {
        "date": "2026-01-01",
        "account": "银行卡",
        "type": "支出",
        "amount": "20",
        "categories": "餐饮,午饭",
        "tags": "工作日",
        "desc": "午饭",
    }
    values.update(overrides)
    return values


def test_loads_and_validates_a_read_only_ledger(tmp_path: Path) -> None:
    path = tmp_path / "transaction.csv"
    write_ledger(
        path,
        [
            row(type="初始", amount="500", categories=""),
            row(type="收入", amount="1000", categories="工资"),
            row(date="2026-01-02"),
        ],
    )

    entries = load_ledger(path, CATEGORY_TREE)

    assert len(entries) == 3
    assert entries[0].type is EntryType.INITIAL
    assert entries[0].signed_amount() == Decimal("500")
    assert entries[-1].categories == ("餐饮", "午饭")


def test_load_creates_one_daily_backup_before_analysis(tmp_path: Path) -> None:
    path = tmp_path / "transaction.csv"
    write_ledger(path, [row()])
    original = path.read_bytes()
    backup_path = tmp_path / f"transaction_{date.today().isoformat()}.csv"

    load_ledger(path, CATEGORY_TREE)

    assert backup_path.read_bytes() == original

    write_ledger(path, [row(amount="25")])
    load_ledger(path, CATEGORY_TREE)

    assert backup_path.read_bytes() == original


def test_rejects_unsorted_dates(tmp_path: Path) -> None:
    path = tmp_path / "transaction.csv"
    write_ledger(
        path,
        [
            row(date="2026-01-02"),
            row(date="2026-01-01"),
        ],
    )

    with pytest.raises(LedgerError, match="日期早于前一条"):
        load_ledger(path, CATEGORY_TREE)


def test_rejects_legacy_categorys_header(tmp_path: Path) -> None:
    path = tmp_path / "transaction.csv"
    path.write_text(
        "date,account,type,amount,categorys,tags,desc\n",
        encoding="utf-8",
    )

    with pytest.raises(
        LedgerError,
        match=r"期望 date,account,type,amount,categories,tags,desc",
    ):
        load_ledger(path, CATEGORY_TREE)


def test_rejects_invalid_category_path(tmp_path: Path) -> None:
    path = tmp_path / "transaction.csv"
    write_ledger(path, [row(categories="餐饮,不存在")])

    with pytest.raises(LedgerError, match="类别路径无效"):
        load_ledger(path, CATEGORY_TREE)


def test_rejects_unbalanced_internal_transfers(tmp_path: Path) -> None:
    path = tmp_path / "transaction.csv"
    write_ledger(
        path,
        [
            row(type="转出", amount="30", categories="内转"),
            row(type="转入", amount="20", categories="内转", account="微信"),
        ],
    )

    with pytest.raises(LedgerError, match="内转不平衡"):
        load_ledger(path, CATEGORY_TREE)
