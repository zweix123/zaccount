from __future__ import annotations

import csv
from pathlib import Path

import check_ledger
from zaccount.ledger import CSV_FIELDS


CATEGORY_TREE = {
    "收入": {"工资": {}},
    "支出": {"餐饮": {"午饭": {}}},
    "转入": {"内转": {}},
    "转出": {"内转": {}},
}


def write_ledger(path: Path, *, category: str = "工资") -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "date": "2026-01-01",
                "account": "银行卡",
                "type": "收入",
                "amount": "1000",
                "categorys": category,
                "tags": "",
                "desc": "月初工资",
            }
        )


def configure_checker(monkeypatch, data_dir: Path) -> None:
    monkeypatch.setattr(
        check_ledger,
        "get_ledger_path",
        lambda: data_dir / "transaction.csv",
    )
    monkeypatch.setattr(
        check_ledger,
        "load_category_tree",
        lambda: CATEGORY_TREE,
    )


def test_main_accepts_valid_ledger(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    write_ledger(tmp_path / "transaction.csv")
    configure_checker(monkeypatch, tmp_path)

    exit_code = check_ledger.main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "账单校验通过" in captured.out
    assert "共 1 条账目" in captured.out
    assert captured.err == ""


def test_main_rejects_category_outside_config(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    write_ledger(tmp_path / "transaction.csv", category="不存在")
    configure_checker(monkeypatch, tmp_path)

    exit_code = check_ledger.main()

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "账单校验失败" in captured.err
    assert "类别路径无效" in captured.err


def test_main_reports_config_load_failure(monkeypatch, capsys) -> None:
    def fail_to_load_config() -> dict[str, dict]:
        raise OSError("无法读取类别配置")

    monkeypatch.setattr(
        check_ledger,
        "load_category_tree",
        fail_to_load_config,
    )

    exit_code = check_ledger.main()

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "账单校验失败：无法读取类别配置" in captured.err
