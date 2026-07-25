from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EntryType(StrEnum):
    INCOME = "收入"
    EXPENSE = "支出"
    TRANSFER_IN = "转入"
    TRANSFER_OUT = "转出"


SUM_FACTOR: dict[EntryType, Decimal] = {
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
    categories: tuple[str, ...] = Field(min_length=1)
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

    @classmethod
    def from_csv_row(cls, row: dict[str, str | None]) -> "LedgerEntry":
        return cls(
            date=row.get("date"),
            account=row.get("account"),
            type=row.get("type"),
            amount=row.get("amount"),
            categories=row.get("categorys"),
            tags=row.get("tags"),
            description=row.get("desc"),
        )

    def to_csv_row(self) -> dict[str, str]:
        return {
            "date": self.date.isoformat(),
            "account": self.account,
            "type": self.type.value,
            "amount": format(self.amount, "f"),
            "categorys": ",".join(self.categories),
            "tags": ",".join(self.tags),
            "desc": self.description,
        }

    def signed_amount(self) -> Decimal:
        return SUM_FACTOR[self.type] * self.amount

    def to_public_dict(self, row_number: int | None = None) -> dict[str, Any]:
        result: dict[str, Any] = {
            "date": self.date.isoformat(),
            "account": self.account,
            "type": self.type.value,
            "amount": float(self.amount),
            "categories": list(self.categories),
            "tags": list(self.tags),
            "description": self.description,
        }
        if row_number is not None:
            result["rowNumber"] = row_number
        return result


class EntryDraft(BaseModel):
    date: date
    account: str
    type: EntryType
    amount: Decimal = Field(gt=0)
    categories: tuple[str, ...] = Field(min_length=1)
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

    def to_entry(self) -> LedgerEntry:
        return LedgerEntry(**self.model_dump())


class TransferDraft(BaseModel):
    date: date
    source_account: str
    destination_account: str
    amount: Decimal = Field(gt=0)
    tags: tuple[str, ...] = ()
    description: str = ""

    @field_validator("source_account", "destination_account")
    @classmethod
    def validate_account(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("账户不能为空")
        return value

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: Any) -> tuple[str, ...]:
        if value is None:
            return ()
        if isinstance(value, str):
            value = value.split(",")
        return tuple(label.strip() for label in value if str(label).strip())

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: Any) -> str:
        return "" if value is None else str(value).strip()

    def to_entries(self) -> tuple[LedgerEntry, LedgerEntry]:
        if self.source_account == self.destination_account:
            raise ValueError("转出账户和转入账户不能相同")
        shared = {
            "date": self.date,
            "amount": self.amount,
            "categories": ("内转",),
            "tags": self.tags,
            "description": self.description,
        }
        return (
            LedgerEntry(
                account=self.source_account,
                type=EntryType.TRANSFER_OUT,
                **shared,
            ),
            LedgerEntry(
                account=self.destination_account,
                type=EntryType.TRANSFER_IN,
                **shared,
            ),
        )
