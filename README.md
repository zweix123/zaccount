# zaccount

## Develop

### Database

目前只有一个表，其含义如下

#### transaction

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
