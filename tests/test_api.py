from __future__ import annotations

import csv
from pathlib import Path

from fastapi.testclient import TestClient

from zaccount.api import create_app
from zaccount.ledger import CSV_FIELDS


def prepare_data(path: Path) -> None:
    with (path / "transaction.csv").open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "date": "2026-01-01",
                "account": "银行卡",
                "type": "收入",
                "amount": "100",
                "categorys": "工资",
                "tags": "",
                "desc": "",
            }
        )


def test_bootstrap_and_create_entry(tmp_path: Path) -> None:
    prepare_data(tmp_path)
    client = TestClient(create_app(data_dir=tmp_path, frontend_dir=tmp_path / "ui"))

    bootstrap = client.get("/api/bootstrap")
    created = client.post(
        "/api/entries",
        json={
            "date": "2026-01-02",
            "account": "银行卡",
            "type": "支出",
            "amount": 18,
            "categories": ["餐饮", "午饭"],
            "tags": ["工作日"],
            "description": "午饭",
        },
    )
    refreshed = client.get("/api/bootstrap")

    assert bootstrap.status_code == 200
    assert bootstrap.json()["analysis"]["count"] == 1
    assert created.status_code == 201
    assert refreshed.json()["analysis"]["summary"]["expense"] == 18.0
    assert len(refreshed.json()["entries"]) == 2
