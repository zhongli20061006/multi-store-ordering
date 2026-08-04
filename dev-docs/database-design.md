# 数据库设计真源

> 本文件为数据模型、字段、关系与状态机唯一 owner。原型使用 SQLite + SQLAlchemy 2.0；生产切换 PostgreSQL 时字段保持兼容。

## 表结构（v1）

### users（管理员/商家账号）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | int PK | |
| username | str unique | 登录名 |
| password_hash | str | bcrypt 哈希，禁止存明文 |
| display_name | str | 显示名 |
| openid | str nullable | 预留：微信登录绑定（本阶段不启用） |
| is_active | bool | 禁用位 |
| created_at / updated_at | datetime | |

### stores（门店）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | int PK | |
| name | str | 门店名 |
| address | str | 地址 |
| phone | str | 联系电话 |
| status | enum(open, closed) | 营业状态；打烊门店顾客端不可下单 |
| sort_order | int | 列表排序 |
| created_at / updated_at | datetime | |

### store_admins（门店-管理员关联）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| store_id | int FK | |
| user_id | int FK | |

联合唯一。原型期种子数据给管理员绑定全部门店；接口按此表校验归属。

### menu_categories（菜单分类）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | int PK | |
| store_id | int FK | 分类归属门店 |
| name | str | |
| sort_order | int | |
| is_active | bool | |

### menu_items（商品）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | int PK | |
| store_id | int FK | 商品归属门店 |
| category_id | int FK nullable | |
| name | str | |
| description | str nullable | |
| price_cents | int | 单价，单位分（避免浮点误差） |
| image_url | str nullable | 原型可空 |
| stock | int nullable | 库存；null=不限量；非空时下单原子扣减，不足拒绝（防超卖） |
| is_active | bool | 下架后顾客端不可见、不可下单 |
| sort_order | int | |

删除策略：商品被订单引用时禁止硬删除，仅下架（is_active=false）。

防超卖规则（唯一 owner：order_service.create_order）：

- 仅当 `stock is not null` 时启用限量；用条件更新 `stock >= quantity` 原子扣减，受影响行数为 0 即库存不足，整单回滚。
- 同一商品同单不重复提交（重复商品 id 拒绝）。
- 订单幂等键保证客户端重复提交只生成一单。
- 二期美团/抖音券核销执行同类原则：券码唯一 + 状态机一次性核销，禁止重复核销。

### orders（订单）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | int PK | |
| order_no | str unique | 业务单号（可读） |
| store_id | int FK | 订单归属门店 |
| customer_name | str | 联系人 |
| customer_phone | str | 电话（原型身份凭据） |
| remark | str nullable | 备注 |
| entry_type | enum(preorder, dinein) | 点单入口：提前点单 / 到店扫码点单；本质同一下单流程 |
| item_count | int | 总件数 |
| total_cents | int | 总额（服务端按库中单价计算） |
| status | enum(pending, accepted, completed, cancelled) | 状态机见下 |
| payment_status | enum(unpaid, paid) | 占位；到店付款由商家标记，阶段二接真实支付 |
| idempotency_key | str unique nullable | 防重复下单（客户端生成） |
| source | str default 'wechat_miniprogram' | 下单来源 |
| created_at / updated_at | datetime | |

### order_items（订单明细）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | int PK | |
| order_id | int FK | |
| menu_item_id | int FK nullable | 商品可软删除，快照保留 |
| item_name | str | 下单时名称快照 |
| unit_price_cents | int | 下单时单价快照 |
| quantity | int | |
| subtotal_cents | int | |

明细必须保存快照，商品后续改名/改价不影响历史订单。

点单入口说明：到店扫码 = 二维码携带 store_id，小程序直接进入该门店菜单，下单时 entry_type=dinein；提前点单 entry_type=preorder。两者共用同一下单接口与状态机。

## 订单状态机

```text
pending ──接单──▶ accepted ──完成──▶ completed
   │
   └──取消──▶ cancelled
```

- 仅服务层可迁移状态；非法迁移返回错误。
- 取消限制：已 completed 不可取消；本阶段取消无金额退款逻辑（无支付）。

## 索引

- orders(store_id, status, created_at)
- menu_items(store_id, is_active)
- menu_categories(store_id)
- order_items(order_id)

## 二期预留（不建表）

- 核销记录表：id、平台(meituan/douyin)、券码、第三方订单号、核销状态、核销时间、操作人、门店。
- 支付单表：id、订单、渠道、金额、状态、回调证据。
- 用户表 openid 字段已预留。

## 迁移策略

- 原型：SQLAlchemy `create_all` + 种子脚本，不引入 Alembic。
- 上线前：引入 Alembic，SQLite→PostgreSQL 数据迁移另立计划（见 technical-selection.md 触发条件）。

## 缓存决策

- 本阶段不加缓存中间件（无读并发压力，避免陈旧数据与运维成本）。
- 预留位置：公开菜单接口为将来可缓存点；若流量上来，在后端接口层加缓存，菜单/价格变更时失效，不改业务代码。
