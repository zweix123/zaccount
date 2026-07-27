from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

from .ledger import LedgerError
from .reporting import generate_report
from .settings import PROJECT_ROOT, get_ledger_path, load_category_tree


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成 Zaccount 交互式账本报告")
    parser.add_argument(
        "--ledger",
        type=Path,
        default=None,
        help="账本 CSV 路径；默认读取 DATA_DIR/transaction.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "output",
        help="报告输出目录；默认是项目的 output/",
    )
    parser.add_argument("--open", action="store_true", help="生成后打开 HTML 报告")
    args = parser.parse_args(argv)

    ledger_path = args.ledger or get_ledger_path()
    try:
        generated = generate_report(
            ledger_path,
            load_category_tree(),
            args.output_dir,
        )
    except (LedgerError, OSError, ValueError) as error:
        print(f"报告生成失败：{error}", file=sys.stderr)
        return 1

    print(
        f"报告生成完成：{generated.html_path}"
        f"（共 {generated.data.source.entry_count} 条账目）"
    )
    print(f"JSON 数据：{generated.json_path}")
    if args.open:
        webbrowser.open(generated.html_path.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
