from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from .domain import EntryType, LedgerEntry


def _to_camel(name: str) -> str:
    first, *rest = name.split("_")
    return first + "".join(part.capitalize() for part in rest)


class LedgerFilter(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    account: str | None = None
    type: EntryType | None = None
    category_path: tuple[str, ...] = ()
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
        if self.category_path and entry.categories[: len(self.category_path)] != (
            self.category_path
        ):
            return False
        if self.tag and self.tag not in entry.tags:
            return False
        if self.query and self.query.casefold() not in entry.description.casefold():
            return False
        return True


class AnalysisModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=_to_camel,
        frozen=True,
        populate_by_name=True,
    )


class AmountByLabel(AnalysisModel):
    label: str
    amount: Decimal


class AnalysisSummary(AnalysisModel):
    income: Decimal
    expense: Decimal
    net_change: Decimal


class AnalysisResult(AnalysisModel):
    count: int
    summary: AnalysisSummary
    accounts: tuple[AmountByLabel, ...]
    monthly_expense: tuple[AmountByLabel, ...]
    category_expense: tuple[AmountByLabel, ...]
    tag_expense: tuple[AmountByLabel, ...]


def analyse(
    entries: list[LedgerEntry], ledger_filter: LedgerFilter | None = None
) -> AnalysisResult:
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

    def sorted_totals(values: dict[str, Decimal]) -> tuple[AmountByLabel, ...]:
        return tuple(
            AmountByLabel(label=label, amount=amount)
            for label, amount in sorted(
                values.items(), key=lambda item: item[1], reverse=True
            )
        )

    return AnalysisResult(
        count=len(filtered),
        summary=AnalysisSummary(
            income=income,
            expense=expense,
            net_change=net_change,
        ),
        accounts=sorted_totals(account_totals),
        monthly_expense=tuple(
            AmountByLabel(label=label, amount=amount)
            for label, amount in sorted(monthly_expense.items())
        ),
        category_expense=sorted_totals(category_expense),
        tag_expense=sorted_totals(tag_expense),
    )
