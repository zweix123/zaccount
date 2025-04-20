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
        print(f"日期格式不合法: {row['date']}")
        print(e)
        print(row)
        exit()

    if row["type"] not in CATEGORY_TREE.keys():  # "type": 类型字段合法
        print(f"类型不合法: {row['type']}")
        print(row)
        exit()

    if row["amount"] < 0:  # amount: 金额合法
        print(f"金额不合法: {row['amount']}")
        print(row)
        exit()

    if pd.notna(row["categorys"]):  # categorys: 类别字段合法, 是约定好的枚举和结构
        if row["categorys"] == "":
            # print(f"类别为空: {row['categorys']}")
            # print(row)
            pass
        else:
            if not tree_has_path(
                CATEGORY_TREE[row["type"]], row["categorys"].split(",")
            ):
                print(f"类别不合法: {row['categorys']}")
                print(row)
                # exit()
    else:
        # print(f"类别为空: {row['categorys']}")
        # print(row)
        pass


def check_date_increment_pandas(csv_file):  # code by AI
    # 读取CSV，保留原始行号，不自动跳过空行
    df = pd.read_csv(csv_file, dtype={"date": str}, skip_blank_lines=False)
    df["original_line"] = df.index + 1  # 记录原始行号（从1开始）

    # 过滤空行（所有字段均为空的行）
    df = df.dropna(how="all")

    # 转换日期列为datetime类型，无效日期转为NaT
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")

    # 收集错误
    errors = []

    # 检查无效日期
    invalid_dates = df[df["date"].isna()]
    for _, row in invalid_dates.iterrows():
        errors.append(
            {
                "line": row["original_line"],
                "error": f"无效日期格式: {row.iloc[0]}",  # row['date']为NaT，取原始字符串值
            }
        )

    # 仅保留有效日期行
    df_valid = df[df["date"].notna()].copy()
    if df_valid.empty:
        print("无有效日期数据。")
        return

    # 检查日期递增：当前行日期必须 > 前一行日期
    df_valid["prev_date"] = df_valid["date"].shift(1)
    mask = (df_valid["date"] < df_valid["prev_date"]) & df_valid["prev_date"].notna()
    non_increasing = df_valid[mask]

    for _, row in non_increasing.iterrows():
        errors.append(
            {
                "line": row["original_line"],
                "date": row["date"].strftime("%Y-%m-%d"),
                "previous_date": row["prev_date"].strftime("%Y-%m-%d"),
            }
        )

    # 输出结果
    if errors:
        print("发现错误：")
        for error in errors:
            if "error" in error:
                print(f"行 {error['line']}: {error['error']}")
            else:
                print(
                    f"行 {error['line']}: 日期 {error['date']} 早于或等于前一行的 {error['previous_date']}"
                )
    else:
        # print("所有日期均严格递增。")
        pass


check_date_increment_pandas(filepath)


print("check success")
