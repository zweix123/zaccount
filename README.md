# zaccount

个人记账工具，基于 CSV 文件存储交易数据，支持按账户汇总资产、按标签聚合查询，以及通过 Jupyter Notebook 生成可视化报表。

## 快速开始

```bash
# 安装依赖
poetry install

# 查看资产总额（按账户分别汇总）
python dryadsfile sum

# 查看所有标签
python dryadsfile tags

# 按标签聚合查询
python dryadsfile group-by-tag <tag>
```

## 项目结构

```
zaccount/
├── entry.py         # 数据模型（Entry / EntryList）
├── utils.py         # 工具函数（数据文件路径、类别校验等）
├── dryadsfile       # CLI 命令入口（基于 dryads）
├── report.ipynb     # 可视化报表（Jupyter Notebook + Plotly）
├── config/
│   └── ctg.jsonc    # 类型与类别的树形枚举配置
├── data/            # 交易数据（CSV 文件，按日期快照）
└── output/          # 报表输出（HTML 图表）
```

## 数据模型

### transaction

交易表，以 CSV 文件存储在 `data/` 目录下，文件名格式为 `transaction_YYYY-MM-DD.csv`。

| field     | type    | description                                    |
| --------- | ------- | ---------------------------------------------- |
| date      | date    | 日期                                           |
| account   | varchar | 账户（如：招商银行）                           |
| type      | varchar | 类型(枚举)                                     |
| amount    | decimal | 金额, 大于 0 的浮点数                          |
| categorys | varchar | 类别(逗号分隔的枚举), 通过前后位置表示父子结构 |
| tags      | varchar | 标签(逗号分割的枚举), 标签之间无关, 用于聚类   |
| desc      | varchar | 描述                                           |

### type 与 categorys

type 与 categorys 枚举见 [config/ctg.jsonc](config/ctg.jsonc)，通过 dict 表示树形结构。

type 共四种：`收入`、`支出`、`转入`、`转出`。资产计算时，`收入`/`转入` 为正，`支出`/`转出` 为负。

## CLI 命令

基于 [dryads](https://github.com/zweix123/dryads) 构建的命令行工具：

| 命令           | 说明                               |
| -------------- | ---------------------------------- |
| `sum`          | 计算资产总额（按账户分别汇总）     |
| `tags`         | 查看所有标签                       |
| `group-by-tag` | 按标签筛选并计算资产总额           |
