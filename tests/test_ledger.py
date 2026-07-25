from __future__ import annotations

import csv
from pathlib import Path

import pytest

from zaccount.domain import EntryDraft, EntryType, TransferDraft
from zaccount.ledger import CSV_FIELDS, LedgerError, LedgerStore


CATEGORY_TREE = {
    "收入": {"工资": {}},
    "支出": {"餐饮": {"午饭": {}}},
    "转入": {"内转": {}},
    "转出": {"内转": {}},
}


def write_ledger(path: Path) -> None:
    rows = [
        {
            "date": "2026-01-01",
            "account": "银行卡",
            "type": "收入",
            "amount": "1000",
            "categorys": "工资",
            "tags": "",
            "desc": "月初工资",
        },
        {
            "date": "2026-01-02",
            "account": "银行卡",
            "type": "支出",
            "amount": "20",
            "categorys": "餐饮,午饭",
            "tags": "工作日",
            "desc": "午饭",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def store(tmp_path: Path) -> LedgerStore:
    write_ledger(tmp_path / "transaction.csv")
    return LedgerStore(tmp_path, CATEGORY_TREE)


def test_add_entry_sorts_and_creates_backup(store: LedgerStore) -> None:
    added = store.add_entry(
        EntryDraft(
            date="2025-12-31",
            account="银行卡",
            type=EntryType.EXPENSE,
            amount="12.50",
            categories=["餐饮"],
            tags=[],
            description="跨年前的一餐",
        )
    )

    entries = store.load()
    backups = list((store.data_dir / "backups").glob("transaction_*.csv"))

    assert entries[0] == added
    assert len(entries) == 3
    assert len(backups) == 1
    assert len(LedgerStore(store.data_dir, CATEGORY_TREE).load()) == 3


def test_transfer_is_committed_as_balanced_pair(store: LedgerStore) -> None:
    outgoing, incoming = store.add_transfer(
        TransferDraft(
            date="2026-01-03",
            source_account="银行卡",
            destination_account="微信",
            amount="300",
            tags=["调拨"],
            description="日常备用",
        )
    )

    entries = store.load()

    assert outgoing.type is EntryType.TRANSFER_OUT
    assert incoming.type is EntryType.TRANSFER_IN
    assert outgoing.amount == incoming.amount
    assert entries[-2:] == [outgoing, incoming]


def test_invalid_category_leaves_file_unchanged(store: LedgerStore) -> None:
    before = store.path.read_bytes()

    with pytest.raises(LedgerError, match="类别路径无效"):
        store.add_entry(
            EntryDraft(
                date="2026-01-03",
                account="银行卡",
                type=EntryType.EXPENSE,
                amount="99",
                categories=["不存在"],
            )
        )

    assert store.path.read_bytes() == before
    assert not (store.data_dir / "backups").exists()


def test_transfer_rejects_same_account(store: LedgerStore) -> None:
    with pytest.raises(LedgerError, match="不能相同"):
        store.add_transfer(
            TransferDraft(
                date="2026-01-03",
                source_account="银行卡",
                destination_account="银行卡",
                amount="1",
            )
        )
