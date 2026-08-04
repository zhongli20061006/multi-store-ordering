# 当前架构真源

> 本文件为宏观架构 owner；技术决策依据见 technical-selection.md，不复制其论证。

## 宏观拓扑

```text
┌─────────────────────┐   ┌─────────────────────┐
│ 微信小程序（顾客端）      │   │ Vue3 网页后台（商家端）    │
│ miniprogram/         │   │ admin/               │
└──────────┬──────────┘   └──────────┬──────────┘
           │         REST JSON API (JWT for admin)
           ▼                          ▼
┌──────────────────────────────────────────────┐
│ FastAPI 后端（单进程）  backend/app/            │
│ modules: auth / stores / menus / orders       │
└──────────────────────┬───────────────────────┘
                       │ SQLAlchemy
                       ▼
              SQLite 本地库（原型）
              （生产切 PostgreSQL，方言隔离）
```

## 进程与部署形态

- 本地开发：`uvicorn app.main:app`（后端，端口 8000）+ `npm run dev`（后台，端口 5173）+ 微信开发者工具（小程序，测试号）。
- 无队列、无定时任务、无微服务；唯一异步边界为微信开发者工具对本地后端的局域网访问。

## Owner Map

| 概念 | Owner |
| --- | --- |
| 产品定位/边界/演进 | dev-docs/project-brief.md |
| 功能与阶段 | dev-docs/function-list.md、stage-plan.md |
| 技术选型 | dev-docs/technical-selection.md |
| 前端路由/页面/组件/样式 | dev-docs/frontend-architecture.md |
| API 合同与后端责任 | dev-docs/backend-boundary.md |
| 数据模型/字段/状态机 | dev-docs/database-design.md |
| 身份/权限/数据归属 | dev-docs/security-boundary.md |
| 验收 | dev-docs/acceptance.md |
| 当前阶段实施真源 | dev-docs/stages/stage-1.md |

## 模块边界（后端）

- `app/api/v1/`：路由与请求校验（薄层）
- `app/services/`：业务规则唯一 owner（订单状态机、金额计算、门店归属校验）
- `app/models/`：SQLAlchemy 模型唯一 owner
- `app/schemas/`：请求/响应契约
- `app/core/`：配置、数据库会话、安全工具

UI/controller 只做展示与映射，不得私藏业务规则。

## 数据与信任边界

- 商品价格、订单金额、状态流转只信任后端数据库与服务层。
- 顾客端接口公开但只读门店/菜单；下单接口由后端校验门店营业与商品上架状态。
- 商家接口全部要求 JWT，且校验门店归属（原型期单管理员管理所有门店，规则仍按归属校验实现）。

## 共享契约

- REST JSON；统一错误格式 `{code, message, detail?}`。
- 订单状态枚举：pending / accepted / completed / cancelled（见 database-design.md）。
- API 清单见 backend-boundary.md。

## 验证命令

见 dev-docs/runtime.md（选型确认后物化）与 acceptance.md。
