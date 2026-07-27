# Zaccount

Zaccount 是一个完全本地运行的私人账本分析工具。它读取并校验
`transaction.csv`，生成一份版本化 JSON 数据和一份可直接双击打开的交互式
HTML 报告。报告不需要服务器，不会上传账目，也不会加载远程资源。

## 能做什么

- 汇总收入、支出、净变化和账户余额。
- 查看月度支出、支出类别和 tag 分布。
- 在报告中组合筛选日期、账户、类型、任意层级 category path、多个 tag 和描述。
- 查看筛选结果对应的账目明细。
- 生成带 SHA-256 账本指纹的 `report.json` 和独立 `report.html`。
- 在读取时校验 CSV 字段、日期顺序、category path 和内部转账平衡。

项目不再提供录入页面或本地服务。账目增删改直接在工作 CSV 中完成，生成报告的
过程只读，不会修改或备份账本。

产品范围、领域规则和架构见：

- [产品与架构设计](docs/product-design.md)
- [领域语言](CONTEXT.md)
- [静态交互报告决策](docs/adr/0002-static-interactive-report.md)

## 初始化

需要 Python 3.13+ 和 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync
cp .env.example .env
```

在 `.env` 中配置包含 `transaction.csv` 的目录：

```dotenv
DATA_DIR=/absolute/path/to/account-data
```

## 生成报告

使用 `.env` 中的账本，默认输出到忽略版本控制的 `output/`：

```bash
uv run python -m zaccount
```

生成完成后自动打开：

```bash
uv run python -m zaccount --open
```

也可以显式指定输入与输出：

```bash
uv run python -m zaccount \
  --ledger "/absolute/path/to/transaction.csv" \
  --output-dir "/absolute/path/to/report"
```

产物包括：

- `report.json`：稳定、带 `schemaVersion` 的分析数据；金额为十进制字符串。
- `report.html`：嵌入相同数据、CSS 和 JavaScript 的单文件交互报告。

报告包含账目明细，因此应像原始账本一样作为私人数据保管。不要提交
`report.json`、`report.html`、真实账本或截图。

## 验证

```bash
uv run pytest
uv run python -m compileall zaccount entry.py utils.py
```

测试只使用临时目录，不会读写 `.env` 指向的个人账本。

## 数据格式

工作文件字段顺序保持兼容：

```text
date,account,type,amount,categorys,tags,desc
```

`categorys` 是历史 CSV 字段拼写，只存在于适配层；代码和界面使用
`categories` 与 “category path”。类别树由
[config/ctg.jsonc](config/ctg.jsonc) 管理。

## 项目结构

```text
zaccount/
  __main__.py          报告命令入口
  domain.py            账目、类型和金额语义
  ledger.py            CSV 读取与完整校验
  analysis.py          筛选与财务聚合
  reporting.py         报告数据契约、生成与原子写入
  report.html          零依赖交互报告模板
  settings.py          数据目录与类别配置
tests/                 Python 行为测试
config/ctg.jsonc       固定类别树
```
