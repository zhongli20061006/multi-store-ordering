# AGENTS.md（项目宪法）

任何时候使用中文，除非用户明确要求英文输出。

## 工作约定（2026-08-04 用户确认）

- 凡涉及架构设计、功能增添、项目规划：必须先讨论、达成一致后再动手；未讨论清楚不得写实现代码。
- 角色分工：sliver-vibe-coding 负责项目规划与项目管理（产品经理角色）；superpowers（brainstorming → writing-plans → TDD 等）负责写代码阶段的流程指导。
- 固定节奏：方向确认 → 分步架构讨论并逐段确认 → 设计定稿与评审 → 实施计划 → 实施。

## 项目边界

- 产品：多门店线上点单系统。顾客端微信小程序（原生）+ 商家网页后台 + Python FastAPI 后端；当前为本地原型，无支付、无微信登录、无第三方核销、不部署上线。
- 明确不做（本阶段）：在线支付、微信登录、美团/抖音核销、外卖配送、会员/营销/库存。订单模型保留支付状态占位，用户表保留 openid 占位，但不得提前实现。
- 已确认下一阶段：美团/抖音团购券核销（实施前必须核查平台官方文档与资质）。抖音/支付宝点单客户端为 speculative，不得为它增加当前复杂度。

## 真源优先

判断和改代码前先读 `dev-docs/README.md` 指向的当前真源：

- 产品边界与演进：`dev-docs/project-brief.md`
- 功能与大阶段：`dev-docs/function-list.md`、`dev-docs/stage-plan.md`
- 技术选型（唯一 owner）：`dev-docs/technical-selection.md`
- 架构与 owner map：`dev-docs/architecture.md`
- 数据模型/状态机：`dev-docs/database-design.md`
- 前端规则：`dev-docs/frontend-architecture.md`
- API 合同与后端责任：`dev-docs/backend-boundary.md`
- 安全边界：`dev-docs/security-boundary.md`
- 验收：`dev-docs/acceptance.md`
- 当前阶段实施：`dev-docs/stages/stage-1.md`

聊天中的决定不生效，写回对应真源后才生效。文档与代码冲突时先修真源。

## 工作流程

1. 每个改动先判断任务深度与测试门禁；稳定可自动化的行为变更先 RED 再 GREEN。
2. 前端：先读前端架构真源；UI 原型必须归档到 `dev-docs/design/` 并记录批准版本，未批准的不得实现；文字/按钮/表单用真实语义元素，禁止整图/截图冒充交互 UI。
3. 后端：路由薄、服务层持有业务规则（金额计算、订单状态机、门店归属校验），UI/controller 不得私藏业务规则。
4. 标准/高风险大功能只使用一份 `sliver-stage/v1` 阶段真源；plan → execute → closeout 按门禁推进，收尾不自动授权下一子阶段。
5. 验收和回写后再提交 Git 检查点；提交信息用中文，说明改动与验证证据。

## 技术规则

- 顾客端：微信原生小程序（JS），微信开发者工具测试号预览；不在小程序端实现金额计算与状态流转。
- 商家后台：Vue 3 + TypeScript + Element Plus；金额输入以元、提交转分；JWT 由 axios 拦截器注入，401 跳登录。
- 后端：Python 3.11 + FastAPI + SQLAlchemy 2.0 + SQLite；目录 app/api、app/services、app/models、app/schemas、app/core。
- 数据库：金额一律用分（int）；订单明细保存商品名/单价快照；删除被订单引用的商品转为下架。
- 禁止：微服务、队列、缓存层、自定义 ORM 封装、补丁式 if/fallback/mock/假成功。
- 禁止给本阶段不存在的支付/微信登录/核销写「预留接口」之外的实现。

## 安全红线

- 前端输入不可信；身份、金额、状态、数据归属必须由服务端重新验证。
- 用户输入不得直接进 SQL/HTML/命令；接口限制可写字段。
- 密钥（JWT 密钥、种子密码、未来第三方凭据）只进 `.env`，禁止进源码、日志、截图、Git 历史；提供 `.env.example`。
- 管理接口校验门店归属；越权返回 403。
- 顾客电话为个人信息，仅用于订单联系与查询；不导出不营销。
- 缺失证据标 `未验证`；未经本轮验证不得声称安全或可上线。
- 安全审计只读；修复需用户授权。

## 验证命令

阶段一实施后生效（写入 runtime.md）：

- 后端测试：`cd backend && python -m pytest`
- 后端启动：`cd backend && uvicorn app.main:app --reload`（端口 8000）
- 后台启动：`cd admin && npm run dev`（端口 5173）
- 小程序：微信开发者工具导入 `miniprogram/`，测试号预览

## Git 与隐私

- 仓库根为当前目录；`.gitignore` 已排除 `.env`、`*.db`、`node_modules`、构建产物。
- `dev-docs/` 为内部真源，推送到远端前需与用户确认是否公开。
- 首次提交需用户确认检查点。

## 停止并询问用户

- 技术栈/框架/数据库/权限模型/支付/第三方服务/部署方式要改变。
- 用户要求进入支付、微信登录、核销、上线等本阶段外能力（先确认资质与范围）。
- 第一闭环、MVP 或非目标边界不清楚。
- 当前证据与真源、用户说法或代码冲突。
- 验证需要真实密钥、生产数据、外部账号、远程部署或破坏性操作。
