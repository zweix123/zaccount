import pandas as pd

from ctg import CATEGORY_TREE
from utils import get_data_file_path, tree_has_path


def check_data(df: pd.DataFrame):
    copy_df = df.copy()

    def check_and_raise(topic: str, filtered_df: pd.DataFrame):
        if len(filtered_df) != 0:
            raise Exception(topic)

    check_and_raise("存在空行", copy_df[copy_df.isna().all(axis=1)])

    # date字段(日期)
    copy_df["date"] = pd.to_datetime(
        copy_df["date"], format="%Y-%m-%d", errors="coerce"
    )  # 按格式转换日期
    check_and_raise("date字段(日期)格式不对", copy_df[copy_df["date"].isna()])
    copy_df["prev_date"] = copy_df["date"].shift(1)
    check_and_raise(
        "date字段(日期)非不递减序列",
        copy_df[
            (copy_df["date"] < copy_df["prev_date"]) & copy_df["prev_date"].notna()
        ],
    )

    # type字段(类型)
    check_and_raise(
        "type字段(类型)存在未知枚举",
        copy_df[~copy_df["type"].isin(CATEGORY_TREE.keys())],
    )

    # amount字段(金额)
    check_and_raise("amount字段(金额)存在负数", copy_df[copy_df["amount"] < 0])

    # categorys字段(类别)
    check_and_raise("categorys字段(类别)存在空值", copy_df[copy_df["categorys"].isna()])
    check_and_raise(
        "categorys字段(类别)存在空字符串", copy_df[copy_df["categorys"] == ""]
    )
    check_and_raise(
        "categorys字段(类别)存在非法枚举表示",
        copy_df[
            copy_df.apply(
                lambda row: not tree_has_path(
                    CATEGORY_TREE[row["type"]], row["categorys"].split(",")
                ),
                axis=1,
            )
        ],
    )


def check_apply_data(pre_df: pd.DataFrame, next_df: pd.DataFrame):
    check_data(pre_df)
    check_data(next_df)

    # pre_df的最后的日期应该**小于等于**next_df的第一个日期 -> 保证数据在date上面顺序
    pre_df["date"] = pd.to_datetime(pre_df["date"])
    next_df["date"] = pd.to_datetime(next_df["date"])
    if pre_df["date"].iloc[-1] > next_df["date"].iloc[0]:
        print("pre ", pre_df["date"].iloc[-1])
        print("next", next_df["date"].iloc[0])
        raise Exception("pre_df的最后的日期大于next_df的第一个日期")


if __name__ == "__main__":
    check_data(pd.read_csv(get_data_file_path()))
