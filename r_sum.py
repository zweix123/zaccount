import pandas as pd

from utils import get_data_file_path

filepath = get_data_file_path()

table = pd.read_csv(filepath)

# 假如type字段为"收入", 则对amount字段累加;
# 假如type字段为"支出", 则对amount字段累减;
total_amount = (
    table[table["type"] == "收入"]["amount"].sum()
    - table[table["type"] == "支出"]["amount"].sum()
)

print(f"资金: {total_amount}")
