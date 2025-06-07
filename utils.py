import datetime
import os
import shutil

from ctg import CATEGORY_TREE

DATA_DIR = "data"


def _build_data_file_path_from_date(date: datetime.datetime) -> str:
    return os.path.join(
        DATA_DIR, f"data_{date.year}-{date.month:02d}-{date.day:02d}.csv"
    )


def get_data_file_path() -> str:
    today = datetime.datetime.now()
    today_file_path = _build_data_file_path_from_date(today)
    if os.path.exists(today_file_path):
        return today_file_path

    # 假如没有, 则向之前的日期寻找, 直到进入2024年
    date = today
    while date.year > 2024:
        date = date - datetime.timedelta(days=1)
        file_path = _build_data_file_path_from_date(date)
        if os.path.exists(file_path):
            shutil.copy(file_path, today_file_path)
            return today_file_path

    raise FileNotFoundError(f"数据文件不存在")


def check_categorys(type: str, categorys: list[str]) -> bool:
    node = CATEGORY_TREE[type]
    for c in categorys:
        if c not in node:
            return False
        node = node[c]
    # return len(node) == 0  # 路径刚好到叶子
    return True  # 路径是一个前缀


if __name__ == "__main__":
    print(get_data_file_path())
