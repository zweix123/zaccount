import os

import pandas as pd

from utils import get_data_file_path

#! 没有检测重复写入的手段
# 从input.xlsx中读取数据, 然后追加到数据文件末尾, 保证两个文件的格式(表头)相同


# 读取数据文件
filepath = get_data_file_path()
table = pd.read_csv(filepath, dtype={0: str})  # （保持原始字符串格式）

# 读取input.xlsx
input_filepath = "input.xlsx"

if not os.path.exists(input_filepath):
    raise FileNotFoundError(f"文件 {input_filepath} 不存在")

input_table = pd.read_excel(input_filepath)

# 双保险格式化（处理异常值）
try:
    input_table.iloc[:, 0] = pd.to_datetime(
        input_table.iloc[:, 0], errors="coerce"
    ).dt.strftime("%Y-%m-%d")
except:
    input_table.iloc[:, 0] = input_table.iloc[:, 0].astype(str).str[:10]


# 合并前确保格式一致
table = pd.concat([table, input_table], ignore_index=True)

# 最终统一格式化（处理原数据可能存在的格式问题）
table.iloc[:, 0] = pd.to_datetime(table.iloc[:, 0], errors="coerce").dt.strftime(
    "%Y-%m-%d"
)

# 写入数据文件
table.to_csv(filepath, index=False)
