import pandas as pd

from utils import get_data_file_path

table = pd.read_csv(get_data_file_path())

total_amount = (
    table[table["type"] == "收入"][
        "amount"
    ].sum()  # 假如type字段为"收入", 则对amount字段累加;
    - table[table["type"] == "支出"][
        "amount"
    ].sum()  # 假如type字段为"支出", 则对amount字段累减;
)

# 以人类可读的方式输出
print(f"{total_amount:,.2f}元人民币")
