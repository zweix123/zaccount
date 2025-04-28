"""
从input.xlsx(从模版中复制, 模板和数据库表结构相同)中读取数据, 追加到数据文件末尾
! 没有检测重复写入的手段
"""

import os

import pandas as pd

from r_check import check_apply_data
from utils import get_data_file_path

INPUT_FILE_NAME = "input.xlsx"
if not os.path.exists(INPUT_FILE_NAME):
    raise FileNotFoundError(f"文件 {INPUT_FILE_NAME} 不存在")


filepath = get_data_file_path()
table = pd.read_csv(filepath, dtype={0: str})  # （保持原始字符串格式）
input_table = pd.read_excel(INPUT_FILE_NAME)

input_table.iloc[:, 0] = pd.to_datetime(
    input_table.iloc[:, 0], errors="coerce"
).dt.strftime("%Y-%m-%d")

print(input_table)

check_apply_data(table, input_table)

answer = input("确定追加(y/n)?")
if answer != "y":
    print("取消追加")
    exit()

table = pd.concat([table, input_table], ignore_index=True)
table.to_csv(filepath, index=False)
