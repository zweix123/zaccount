from zaccount.analysis import LedgerFilter, analyse
from zaccount.domain import LedgerEntry


def entry(**overrides: object) -> LedgerEntry:
    values = {
        "date": "2026-01-01",
        "account": "银行卡",
        "type": "支出",
        "amount": "10",
        "categories": ["餐饮"],
        "tags": [],
        "description": "",
    }
    values.update(overrides)
    return LedgerEntry(**values)


def test_analysis_uses_signed_totals_and_ignores_empty_tags() -> None:
    result = analyse(
        [
            entry(type="收入", amount="100", categories=["工资"]),
            entry(amount="25", tags=["聚餐"]),
            entry(
                type="转出",
                amount="30",
                categories=["内转"],
                account="银行卡",
            ),
            entry(
                type="转入",
                amount="30",
                categories=["内转"],
                account="微信",
            ),
        ]
    )

    assert result["summary"] == {
        "income": 100.0,
        "expense": 25.0,
        "netChange": 75.0,
    }
    assert result["tagExpense"] == [{"label": "聚餐", "amount": 25.0}]
    assert result["count"] == 4


def test_analysis_filter_is_shared_by_every_aggregation() -> None:
    entries = [
        entry(date="2026-01-01", amount="20", tags=["工作日"]),
        entry(
            date="2026-02-01",
            amount="50",
            account="微信",
            categories=["购物"],
            tags=["周末"],
        ),
    ]

    result = analyse(entries, LedgerFilter(account="微信", tag="周末"))

    assert result["count"] == 1
    assert result["summary"]["expense"] == 50.0
    assert result["monthlyExpense"] == [{"label": "2026-02", "amount": 50.0}]
    assert result["categoryExpense"] == [{"label": "购物", "amount": 50.0}]
