"""
工具包
+ get_data_file_path: 获取当天数据库文件, 假如没有, 则向之前的日期寻找, 直到进入2024年
+ tree_has_path: 判断一个类别"路径"是否在类别树上(不一定到叶子)
"""

import datetime
import os
import shutil

DATA_DIR = "data"


def _build_data_file_path_from_date(t: datetime.datetime) -> str:
    file_name_suffix = f"{t.year}-{t.month:02d}-{t.day:02d}"
    return os.path.join(DATA_DIR, f"data_{file_name_suffix}.csv")


def get_data_file_path() -> str:
    today = datetime.datetime.now()
    today_file_path = _build_data_file_path_from_date(today)
    if os.path.exists(today_file_path):
        return today_file_path

    # 假如没有, 则向之前的日期寻找, 直到进入2024年
    past = today
    while past.year > 2024:
        past = past - datetime.timedelta(days=1)
        past_file_path = _build_data_file_path_from_date(past)
        if os.path.exists(past_file_path):
            shutil.copy(past_file_path, today_file_path)
            return today_file_path

    raise FileNotFoundError(f"数据文件不存在")


def _dfs(root: dict, keys: list[str], cur_idx: int) -> bool:
    if cur_idx == len(keys):
        return isinstance(root, dict) and len(root) == 0  # 到达叶子
        # return True  # 没有到达叶子
    if keys[cur_idx] not in root.keys():
        return False
    return _dfs(root[keys[cur_idx]], keys, cur_idx + 1)


def tree_has_path(root: dict, keys: list[str]) -> bool:
    return _dfs(root, keys, 0)


if __name__ == "__main__":
    print(get_data_file_path())
