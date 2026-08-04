# 后端责任边界真源

## 职责

后端唯一拥有：商品价格、订单金额计算、订单状态机、门店/菜单归属校验、登录鉴权、数据持久化。前端只做展示与提交，不得私藏业务规则。

## API 合同（v1）

统一前缀 `/api/v1`；错误格式 `{ "code": <业务码>, "message": "...", "detail": {...} }`。

### 公开接口（小程序）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | /health | 健康检查 |
| GET | /stores | 营业中门店列表 |
| GET | /stores/{id}/menu | 门店菜单（分类+上架商品） |
| POST | /orders | 创建订单（服务端重算金额；幂等键防重；限库存原子扣减） |
| GET | /orders?phone=xxx | 按电话查订单摘要（原型身份方案，见 security-boundary） |

### 管理接口（JWT）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | /auth/login | 登录，返回 token |
| GET | /auth/me | 当前用户 |
| GET/POST | /admin/stores | 门店列表/新建 |
| PUT/DELETE | /admin/stores/{id} | 编辑/删除（有订单禁止删除） |
| PATCH | /admin/stores/{id}/status | 开/关店 |
| GET/POST/PUT/DELETE | /admin/stores/{id}/categories | 分类管理 |
| GET/POST/PUT/DELETE | /admin/stores/{id}/items | 商品管理（删除转下架） |
| GET | /admin/orders | 订单列表（store_id/status 筛选） |
| GET | /admin/orders/{id} | 订单详情（含明细） |
| PATCH | /admin/orders/{id}/status | 状态迁移（接单/完成/取消） |
| PATCH | /admin/orders/{id}/payment | 标记到店付款 |

## 归属校验规则

- 管理接口一律先解析 JWT，再校验目标门店 ∈ 当前用户门店集合；不符返回 403。
- 订单状态迁移必须走服务层状态机。
- 下单入口类型（preorder/dinein）由服务端记录，二维码只携带门店参数。

## 模块 owner

- `app/api/v1/*`：路由与参数校验（薄）
- `app/services/*`：业务规则唯一 owner
- `app/models/*`：数据模型唯一 owner
- `app/schemas/*`：请求/响应契约
- `app/core/*`：配置、DB、安全工具

## 错误码约定

- 400 参数错误；401 未登录；403 无权限；404 不存在；409 状态冲突；500 服务错误。
