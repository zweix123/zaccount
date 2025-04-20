import pandas as pd

from ctg import CATEGORY_TREE
from utils import get_data_file_path, tree_has_path

filepath = get_data_file_path()
try:
    table = pd.read_csv(filepath)  # csv格式合法
except Exception as e:
    print(e)
    exit()


for index, row in table.iterrows():
    try:
        pd.to_datetime(row["date"])  # date: 日期格式合法
    except Exception as e:
        print(e)
        print(row)
        exit()

    if row["type"] not in CATEGORY_TREE.keys():  # "type": 类型字段合法
        print(row)
        exit()

    if row["amount"] < 0:  # amount: 金额合法
        print(row)
        exit()

    if pd.notna(row["categorys"]):  # categorys: 分类字段合法, 是约定好的枚举和结构
        if row["categorys"] == "":
            print(row)
        else:
            if not tree_has_path(
                CATEGORY_TREE[row["type"]], row["categorys"].split(",")
            ):
                print(row)
                exit()

print("check success")
