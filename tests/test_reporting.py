from __future__ import annotations

import csv
import json
from datetime import date, datetime, timezone
from pathlib import Path

from zaccount.__main__ import main
from zaccount.ledger import CSV_FIELDS
from zaccount.reporting import generate_report


CATEGORY_TREE = {
    "初始": {},
    "收入": {"工资": {}},
    "支出": {"餐饮": {"正餐": {}, "饮料": {}}},
    "转入": {"内转": {}},
    "转出": {"内转": {}},
}


def write_ledger(path: Path) -> None:
    rows = [
        {
            "date": "2026-01-01",
            "account": "银行卡",
            "type": "初始",
            "amount": "1000.00",
            "categorys": "",
            "tags": "",
            "desc": "",
        },
        {
            "date": "2026-01-03",
            "account": "银行卡",
            "type": "收入",
            "amount": "123.45",
            "categorys": "工资",
            "tags": "一月",
            "desc": "工资",
        },
        {
            "date": "2026-01-04",
            "account": "银行卡",
            "type": "支出",
            "amount": "23.40",
            "categorys": "餐饮,正餐",
            "tags": "一月,工作日",
            "desc": "</script><script>不应执行</script>",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_generate_report_writes_versioned_json_and_standalone_html(
    tmp_path: Path,
) -> None:
    ledger_path = tmp_path / "private-ledger.csv"
    output_dir = tmp_path / "output"
    write_ledger(ledger_path)

    generated = generate_report(
        ledger_path,
        CATEGORY_TREE,
        output_dir,
        generated_at=datetime(2026, 7, 27, 12, tzinfo=timezone.utc),
    )

    payload = json.loads(generated.json_path.read_text(encoding="utf-8"))
    html = generated.html_path.read_text(encoding="utf-8")

    assert payload["schemaVersion"] == 1
    assert payload["source"]["fileName"] == "private-ledger.csv"
    assert payload["source"]["entryCount"] == 3
    assert payload["entries"][1]["amount"] == "123.45"
    assert payload["analysis"]["summary"]["netChange"] == "1100.05"
    assert str(tmp_path) not in generated.json_path.read_text(encoding="utf-8")
    assert "__ZACCOUNT_REPORT_DATA__" not in html
    assert "\\u003c/script\\u003e" in html
    assert "<script>不应执行</script>" not in html
    assert "Category path" in html


def test_cli_generates_report_from_explicit_paths(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    ledger_path = tmp_path / "transaction.csv"
    output_dir = tmp_path / "report"
    write_ledger(ledger_path)
    monkeypatch.setattr(
        "zaccount.__main__.load_category_tree",
        lambda: CATEGORY_TREE,
    )

    exit_code = main(
        [
            "--ledger",
            str(ledger_path),
            "--output-dir",
            str(output_dir),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "报告生成完成" in captured.out
    assert (
        tmp_path / f"transaction_{date.today().isoformat()}.csv"
    ).is_file()
    assert (output_dir / "report.html").is_file()
    assert (output_dir / "report.json").is_file()
