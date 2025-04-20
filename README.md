# zaccount

账本/记账

## 表结构

### 交易表

transaction

| field     | type    | description                                  |
| --------- | ------- | -------------------------------------------- |
| date      | date    | 日期                                         |
| type      | varchar | 类型(枚举)                                   |
| amount    | decimal | 金额                                         |
| categorys | varchar | 类别(逗号分隔的枚举), 通过前后位置表父子结构 |
| tags      | varchar | 标签(逗号分割的枚举), 标签之间无关, 用于聚类 |
| desc      | varchar | 描述                                         |
