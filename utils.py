import datetime
import os
import shutil

import commentjson  # type: ignore
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.environ.get("DATA_DIR", "data")
PROJECT_DIR_PATH = os.path.dirname(os.path.abspath(__file__))


def _build_ctg_file_path() -> str:
    return os.path.join(PROJECT_DIR_PATH, "config", "ctg.jsonc")


ctg_cache: dict[str, dict] = {}


def load_ctg() -> dict:
    global ctg_cache
    if len(ctg_cache) == 0:
        with open(_build_ctg_file_path(), "r", encoding="utf-8") as f:
            ctg_cache = commentjson.load(f)
    return ctg_cache


def _build_data_file_path_from_date(date: datetime.datetime) -> str:
    return os.path.join(
        PROJECT_DIR_PATH,
        DATA_DIR,
        f"transaction_{date.year}-{date.month:02d}-{date.day:02d}.csv",
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

    raise FileNotFoundError("数据文件不存在")


def check_categorys(type: str, categorys: list[str]) -> bool:
    node = load_ctg()[type]
    for c in categorys:
        if c not in node:
            return False
        node = node[c]
    # return len(node) == 0  # 路径刚好到叶子
    return True  # 路径是一个前缀


if __name__ == "__main__":
    print(get_data_file_path())
    print(_build_ctg_file_path())
    print(load_ctg())
