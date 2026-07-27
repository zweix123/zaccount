from __future__ import annotations

import csv
from pathlib import Path

import account_balances
from zaccount.ledger import CSV_FIELDS


CATEGORY_TREE = {
    "收入": {"工资": {}},
    "支出": {"餐饮": {}},
    "转入": {"内转": {}},
    "转出": {"内转": {}},
}


def write_ledger(path: Path) -> None:
    rows = [
        {
            "date": "2026-01-01",
            "account": "银行卡",
            "type": "收入",
            "amount": "100",
            "categorys": "工资",
            "tags": "",
            "desc": "",
        },
        {
            "date": "2026-01-02",
            "account": "银行卡",
            "type": "支出",
            "amount": "25",
            "categorys": "餐饮",
            "tags": "",
            "desc": "",
        },
        {
            "date": "2026-01-03",
            "account": "银行卡",
            "type": "转出",
            "amount": "30",
            "categorys": "内转",
            "tags": "",
            "desc": "",
        },
        {
            "date": "2026-01-03",
            "account": "微信",
            "type": "转入",
            "amount": "30",
            "categorys": "内转",
            "tags": "",
            "desc": "",
        },
        {
            "date": "2026-01-04",
            "account": "微信",
            "type": "支出",
            "amount": "40",
            "categorys": "餐饮",
            "tags": "",
            "desc": "",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def configure_script(monkeypatch, data_dir: Path) -> None:
    monkeypatch.setattr(
        account_balances,
        "get_ledger_path",
        lambda: data_dir / "transaction.csv",
    )
    monkeypatch.setattr(
        account_balances,
        "load_category_tree",
        lambda: CATEGORY_TREE,
    )


def test_main_prints_each_account_balance(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    write_ledger(tmp_path / "transaction.csv")
    configure_script(monkeypatch, tmp_path)

    exit_code = account_balances.main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.splitlines() == [
        "账户余额：",
        "银行卡：¥45.00",
        "微信：-¥10.00",
    ]
    assert captured.err == ""


def test_main_reports_invalid_ledger(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    write_ledger(tmp_path / "transaction.csv")
    configure_script(monkeypatch, tmp_path)
    monkeypatch.setattr(
        account_balances,
        "load_category_tree",
        lambda: {**CATEGORY_TREE, "收入": {}},
    )

    exit_code = account_balances.main()

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "账户余额计算失败" in captured.err
    assert "类别路径无效" in captured.err
