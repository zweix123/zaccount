import pandas as pd

from ctg import CATEGORY_TREE
from utils import get_data_file_path

FACTOR = {
    "收入": 1,
    "转入": 1,
    "支出": -1,
}
assert set(FACTOR.keys()) == set(CATEGORY_TREE.keys())

table = pd.read_csv(get_data_file_path())

all_types = table["type"].unique()
assert set(all_types) == set(CATEGORY_TREE.keys())

total_amount = 0
for t, factor in FACTOR.items():
    total_amount += factor * table[table["type"] == t]["amount"].sum()


print(f"{total_amount:,.2f}元人民币")  # 以人类可读的方式输出
