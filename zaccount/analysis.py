from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel

from .domain import EntryType, LedgerEntry


class LedgerFilter(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    account: str | None = None
    type: EntryType | None = None
    category: str | None = None
    tag: str | None = None
    query: str | None = None

    def matches(self, entry: LedgerEntry) -> bool:
        if self.start_date and entry.date < self.start_date:
            return False
        if self.end_date and entry.date > self.end_date:
            return False
        if self.account and entry.account != self.account:
            return False
        if self.type and entry.type is not self.type:
            return False
        if self.category and self.category not in entry.categories:
            return False
        if self.tag and self.tag not in entry.tags:
            return False
        if self.query and self.query.casefold() not in entry.description.casefold():
            return False
        return True


def analyse(
    entries: list[LedgerEntry], ledger_filter: LedgerFilter | None = None
) -> dict[str, Any]:
    ledger_filter = ledger_filter or LedgerFilter()
    filtered = [entry for entry in entries if ledger_filter.matches(entry)]

    income = sum(
        (entry.amount for entry in filtered if entry.type is EntryType.INCOME),
        Decimal("0"),
    )
    expense = sum(
        (entry.amount for entry in filtered if entry.type is EntryType.EXPENSE),
        Decimal("0"),
    )
    net_change = sum(
        (entry.signed_amount() for entry in filtered), Decimal("0")
    )

    account_totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    monthly_expense: defaultdict[str, Decimal] = defaultdict(Decimal)
    category_expense: defaultdict[str, Decimal] = defaultdict(Decimal)
    tag_expense: defaultdict[str, Decimal] = defaultdict(Decimal)

    for entry in filtered:
        account_totals[entry.account] += entry.signed_amount()
        if entry.type is not EntryType.EXPENSE:
            continue
        monthly_expense[entry.date.strftime("%Y-%m")] += entry.amount
        category_expense[entry.categories[0]] += entry.amount
        for tag in entry.tags:
            tag_expense[tag] += entry.amount

    def sorted_totals(values: dict[str, Decimal]) -> list[dict[str, Any]]:
        return [
            {"label": label, "amount": float(amount)}
            for label, amount in sorted(
                values.items(), key=lambda item: item[1], reverse=True
            )
        ]

    return {
        "count": len(filtered),
        "summary": {
            "income": float(income),
            "expense": float(expense),
            "netChange": float(net_change),
        },
        "accounts": sorted_totals(account_totals),
        "monthlyExpense": [
            {"label": label, "amount": float(amount)}
            for label, amount in sorted(monthly_expense.items())
        ],
        "categoryExpense": sorted_totals(category_expense),
        "tagExpense": sorted_totals(tag_expense),
    }
