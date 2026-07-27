#!/usr/bin/env -S uv run
from __future__ import annotations

import sys

from zaccount.ledger import LedgerError, load_ledger
from zaccount.settings import get_ledger_path, load_category_tree


def main() -> int:
    try:
        path = get_ledger_path()
        entries = load_ledger(path, load_category_tree())
    except (LedgerError, OSError, ValueError) as error:
        print(f"账单校验失败：{error}", file=sys.stderr)
        return 1

    print(f"账单校验通过：{path}（共 {len(entries)} 条账目）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
