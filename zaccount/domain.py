from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class EntryType(StrEnum):
    INITIAL = "初始"
    INCOME = "收入"
    EXPENSE = "支出"
    TRANSFER_IN = "转入"
    TRANSFER_OUT = "转出"


SUM_FACTOR: dict[EntryType, Decimal] = {
    EntryType.INITIAL: Decimal("1"),
    EntryType.INCOME: Decimal("1"),
    EntryType.EXPENSE: Decimal("-1"),
    EntryType.TRANSFER_IN: Decimal("1"),
    EntryType.TRANSFER_OUT: Decimal("-1"),
}


class LedgerEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    date: date
    account: str
    type: EntryType
    amount: Decimal = Field(gt=0)
    categories: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    description: str = ""

    @field_validator("account")
    @classmethod
    def validate_account(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("账户不能为空")
        return value

    @field_validator("categories", "tags", mode="before")
    @classmethod
    def normalize_labels(cls, value: Any) -> tuple[str, ...]:
        if value is None:
            return ()
        if isinstance(value, str):
            value = value.split(",")
        return tuple(label.strip() for label in value if str(label).strip())

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: Any) -> str:
        return "" if value is None else str(value).strip()

    @model_validator(mode="after")
    def validate_categories_for_type(self) -> "LedgerEntry":
        if self.type is EntryType.INITIAL:
            if self.categories:
                raise ValueError("初始账目不能填写类别")
        elif not self.categories:
            raise ValueError("类别不能为空")
        return self

    @classmethod
    def from_csv_row(cls, row: dict[str, str | None]) -> "LedgerEntry":
        return cls(
            date=row.get("date"),
            account=row.get("account"),
            type=row.get("type"),
            amount=row.get("amount"),
            categories=row.get("categories"),
            tags=row.get("tags"),
            description=row.get("desc"),
        )

    def signed_amount(self) -> Decimal:
        return SUM_FACTOR[self.type] * self.amount
