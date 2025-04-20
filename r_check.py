import pandas as pd

from ctg import CATEGORY_TREE
from utils import get_data_file_path, tree_has_path


def check(topic: str, filtered_df: pd.DataFrame):
    if len(filtered_df) != 0:
        print(topic)
        print(filtered_df)
        exit(-1)


df = pd.read_csv(get_data_file_path())


check("存在空行", df[df.isna().all(axis=1)])

df["date"] = pd.to_datetime(
    df["date"], format="%Y-%m-%d", errors="coerce"
)  # 按格式转换日期
check("date字段（日期）格式不对", df[df["date"].isna()])

check("type字段（类型）存在未知枚举", df[~df["type"].isin(CATEGORY_TREE.keys())])
check("amount字段（金额）存在负数", df[df["amount"] < 0])
check("categorys字段（类别）存在空值", df[df["categorys"].isna()])
check("categorys字段（类别）存在空字符串", df[df["categorys"] == ""])
check(
    "categorys字段（类别）存在非法枚举表示",
    df[
        df.apply(
            lambda row: not tree_has_path(
                CATEGORY_TREE[row["type"]], row["categorys"].split(",")
            ),
            axis=1,
        )
    ],
)

df["prev_date"] = df["date"].shift(1)
check(
    "date字段（日期）非不递减序列",
    df[(df["date"] < df["prev_date"]) & df["prev_date"].notna()],
)

print("check pass")
