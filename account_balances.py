#!/usr/bin/env -S uv run
from __future__ import annotations

import sys
from decimal import Decimal

from zaccount.analysis import analyse
from zaccount.ledger import LedgerError, load_ledger
from zaccount.settings import get_ledger_path, load_category_tree


def format_money(amount: Decimal) -> str:
    sign = "-" if amount < 0 else ""
    return f"{sign}¥{abs(amount):,.2f}"


def main() -> int:
    try:
        analysis = analyse(
            load_ledger(get_ledger_path(), load_category_tree())
        )
    except (LedgerError, OSError, ValueError) as error:
        print(f"账户余额计算失败：{error}", file=sys.stderr)
        return 1

    accounts = analysis.accounts
    if not accounts:
        print("账单中没有账户。")
        return 0

    print("账户余额：")
    for account in accounts:
        print(f"{account.label}：{format_money(account.amount)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
