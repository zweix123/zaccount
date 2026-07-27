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
            entry(type="初始", amount="500", categories=[]),
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

    assert result.summary.income == 100
    assert result.summary.expense == 25
    assert result.summary.net_change == 575
    assert [(item.label, item.amount) for item in result.accounts] == [
        ("银行卡", 545),
        ("微信", 30),
    ]
    assert [(item.label, item.amount) for item in result.tag_expense] == [
        ("聚餐", 25)
    ]
    assert result.count == 5


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

    assert result.count == 1
    assert result.summary.expense == 50
    assert [(item.label, item.amount) for item in result.monthly_expense] == [
        ("2026-02", 50)
    ]
    assert [(item.label, item.amount) for item in result.category_expense] == [
        ("购物", 50)
    ]


def test_category_filter_matches_a_path_prefix() -> None:
    entries = [
        entry(categories=["餐饮", "正餐"], amount="20"),
        entry(categories=["餐饮", "饮料"], amount="8"),
        entry(categories=["购物", "快消"], amount="30"),
    ]

    result = analyse(
        entries,
        LedgerFilter(category_path=("餐饮",)),
    )

    assert result.count == 2
    assert result.summary.expense == 28
