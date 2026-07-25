# Zaccount

Zaccount 是一个完全本地运行的私人账本。它使用 Vue 提供录入、浏览和分析界面，使用 Python 校验并安全写入 CSV；应用只监听 `127.0.0.1`，不会上传账目或加载远程页面资源。

## 功能

- 录入收入、支出、转入和转出账目。
- 将账户转账作为一次操作，自动写入平衡的转出和转入记录。
- 按日期、账户、类型、类别、标签和描述筛选账目。
- 查看收入、支出、净变化、账户余额、月度趋势、类别和标签分布。
- 每次写入前创建时间戳备份，并通过临时文件原子替换工作 CSV。
- 保持原有 `transaction.csv` 字段和类别配置兼容。

产品范围、领域规则和架构见：

- [产品与架构设计](docs/product-design.md)
- [领域语言](CONTEXT.md)
- [本地 Web 与 CSV 决策](docs/adr/0001-local-web-csv-ledger.md)

## 初始化

需要 Python 3.13+、[uv](https://docs.astral.sh/uv/) 和 Node.js 22+。

```bash
uv sync
cd frontend
npm install
npm run build
cd ..
```

复制环境配置并设置账目目录：

```bash
cp .env.example .env
```

```dotenv
DATA_DIR=/absolute/path/to/account-data
```

该目录中需要存在 `transaction.csv`。个人数据、备份和构建产物均由 `.gitignore` 排除。

## 使用

```bash
uv run python -m zaccount
```

应用默认打开 [http://127.0.0.1:8000](http://127.0.0.1:8000)。如果不希望自动打开浏览器：

```bash
uv run python -m zaccount --no-browser
```

前后端开发模式：

```bash
# 终端一
uv run python -m zaccount --no-browser --reload

# 终端二
cd frontend
npm run dev
```

Vite 开发页面位于 `http://127.0.0.1:5173`，并将 `/api` 转发到 Python 应用。

## 验证

```bash
uv run pytest
cd frontend
npm run test:run
npm run build
```

测试只使用临时目录，不会读写 `.env` 指向的个人账本。生产构建会输出到忽略的 `frontend/dist/`，由 Python 应用直接提供。

## 数据格式

工作文件为 `transaction.csv`，字段顺序保持兼容：

| 字段 | 含义 |
| --- | --- |
| `date` | `YYYY-MM-DD` 日期 |
| `account` | 账户 |
| `type` | `收入`、`支出`、`转入` 或 `转出` |
| `amount` | 大于零的金额 |
| `categorys` | 用逗号连接的类别路径；历史拼写保持不变 |
| `tags` | 用逗号连接的独立标签 |
| `desc` | 自由描述 |

类别树由 [config/ctg.jsonc](config/ctg.jsonc) 管理。成功写入前，候选账本会完整检查日期顺序、类别路径和内部转账余额。旧文件保存在数据目录的 `backups/` 中。

## 项目结构

```text
zaccount/
  __main__.py          本地应用入口
  domain.py            账目、类型和转账语义
  ledger.py            CSV 校验、备份与原子写入
  analysis.py          统一筛选与聚合
  api.py               本地 HTTP 和静态页面
  settings.py          数据目录与类别配置
frontend/
  src/                 Vue 3 + TypeScript 界面
tests/                 Python 行为测试
config/ctg.jsonc       固定类别树
```
