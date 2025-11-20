# zaccount

你需要账单的什么功能？

- 首先所有的统计都是有一个时间范围的（范围足够大对你来说就相当于没有范围）

1. 分别以年月日为单位生成折线图表示每年月日的花销
2. 饼图，ctg 树的每个非叶子结点都要有一个饼图，饼图的每个部分是该结点子节点

## Develop

### Database

目前只有一个表，其含义如下

### transaction

交易表

| field     | type    | description                                    |
| --------- | ------- | ---------------------------------------------- |
| date      | date    | 日期                                           |
| type      | varchar | 类型(枚举)                                     |
| amount    | decimal | 金额, 大于 0 的浮点数                          |
| categorys | varchar | 类别(逗号分隔的枚举), 通过前后位置表示父子结构 |
| tags      | varchar | 标签(逗号分割的枚举), 标签之间无关, 用于聚类   |
| desc      | varchar | 描述                                           |

type 与 categorys 枚举见[config/ctg.jsonc](config/ctg.jsonc), 通过 dict 表示树形结构

### 文件结构

```
.
├── README.md
├── config         # 项目配置
│   └── ctg.jsonc  #
├── data           # 数据
├── backend        # 后端
├── web            # 前端
└── scripts        # 脚本
    ├── dryadsfile #
    └── pyproject.toml
```

### 后端实现

后端使用 Golang 语言实现，不使用任何后端框架

#### 运行 API 服务器

```bash
cd backend
go run cmd/api/main.go
```

服务器默认运行在 `http://localhost:8080`，可以通过环境变量 `PORT` 修改端口：

```bash
PORT=3000 go run cmd/api/main.go
```

### 前端实现

前端使用 Amis 和 ECharts，通过后端 API 服务器提供静态文件服务。

#### 快速开始

1. 启动后端 API 服务器（见上方）
2. 在浏览器中访问 `http://localhost:8080`
