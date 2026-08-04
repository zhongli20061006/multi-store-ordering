# 阶段一：本地原型（实施真源）

## 阶段控制

- schema: sliver-stage/v1
- stage_status: execution_ready
- task_depth: 标准任务
- product_confirmation: confirmed: 用户 2026-08-04 确认原型范围（小程序点单闭环 + 简单商家后台 + 本地后端），并确认三点技术路线产品后果
- active_substage: 1.3 商家后台
- authorized_substage: pending: 待商家后台实施计划经用户确认后绑定
- substage_authorization: pending: 待商家后台实施计划经用户确认
- result_status: in_progress
- truth_writeback: pending

## 阶段目标与用户流程

目标用户：顾客（小程序）与商家（网页后台）。完整流程：顾客选门店 → 看菜单 → 加购 → 填写联系人/电话/备注 → 提交订单 → 商家后台登录 → 接单 → 完成/取消/标记付款；顾客凭电话查询订单状态。

本阶段可验收结果：以上闭环在本地全部跑通，数据落库，金额与状态正确，越权与非法输入被拒绝。

## 当前真相与 Owner

- 产品/功能/阶段：dev-docs/project-brief.md、function-list.md、stage-plan.md
- 技术选型：dev-docs/technical-selection.md（implementation_ready）
- 架构与 owner map：dev-docs/architecture.md
- 数据模型/状态机：dev-docs/database-design.md
- 前后端契约：dev-docs/backend-boundary.md、frontend-architecture.md
- 安全边界：dev-docs/security-boundary.md
- 验收：dev-docs/acceptance.md
- 禁止 owner：UI/controller 不得持有金额计算、状态机、归属校验。

## 调研决策

- research_status: completed: 2026-08-04 核查 FastAPI 0.129.x（Python≥3.10）、Element Plus 2.14.x、SQLAlchemy 2.0.51、微信开发者工具测试号可用；同类点单流程（瑞幸/蜜雪冰城等）为行业常识，无外部合同依赖

## 范围与非目标

范围：后端骨架与全部 v1 接口、商家后台、微信小程序顾客端、联调验收。
非目标：支付、微信登录、美团/抖音核销、外卖配送、会员/营销/库存、部署上线。

## 子阶段计划

| 子阶段 | 结果 | Owner | 完成标准 | 验证 | 不触碰 |
| --- | --- | --- | --- | --- | --- |
| 1.1 后端骨架 | FastAPI 服务可启动，/health 正常，配置/错误格式/DB 连接就绪，种子脚本可用 | backend/app/core、app/main.py、seed.py | 启动命令可用；/health 返回 ok；错误格式统一 | 启动 + 接口请求 + 日志 | 业务接口 |
| 1.2 数据模型与 API | 全部 v1 接口实现，金额服务端计算、状态机、归属校验 | backend/app/models、schemas、services、api/v1、tests | 接口测试全绿；越权/非法输入拒绝 | pytest + 手工请求 | 前端 |
| 1.2b 后端对齐设计稿 v3 | 订单字段更名、取消分类与库存回补、查单收紧、分类联动、索引、SQLite 配置 | backend/app、backend/tests | 实施计划 6 项任务全部测试通过 | pytest + 冒烟请求 | 商家后台与小程序 |
| 1.3 商家后台 | 登录/门店/菜单/订单四组页面 | admin/ | 浏览器走查通过 | 浏览器 + 截图 | 小程序 |
| 1.4 顾客小程序 | 门店/菜单/购物车/下单/查单页面 | miniprogram/ | 开发者工具走查通过 | 工具预览 + 截图 | 后台 |
| 1.5 联调与验收 | 端到端闭环贯通 | 三端 | 验收清单全部通过 | 验收走查 + 证据 | 本阶段外功能 |

## 测试、安全与影响

- 测试门禁：后端业务行为（金额、状态机、鉴权、归属、幂等）为 T2，先写契约测试观察 RED 再实现；前端页面走查为 T3/T0 组合（浏览器/工具证据）。
- 安全影响：涉及身份（商家登录）、授权（门店归属）、数据写入（订单）、个人信息（电话）、金额字段——按 security-boundary.md 处理，负面用例进测试。
- 基础影响：无（技术选型已确认，不改栈不改库）。
- 数据影响：本地 SQLite；测试用独立临时库，不污染开发库。

## 验证方法

- 后端：`cd backend && python -m pytest` 全绿；uvicorn 启动后 /health、登录、下单等关键接口请求输出。
- 前端：开发者工具/浏览器走查证据（后续子阶段补充）。
- 越权与非法状态负面用例必须在测试中覆盖。

## 停止条件与未验证

- 用户要求支付/核销/上线等本阶段外能力时停止并先确认资质与范围。
- 真源与代码冲突时先修真源再继续。
- 未验证：微信登录、支付、核销、正式部署相关证据均为未验证（本阶段不涉及）。
- 子阶段收尾不自动授权下一子阶段；下一子阶段需在本文档更新 active_substage 并记录授权。

## 实施回写

### 子阶段 1.1 + 1.2（后端骨架与数据模型/API）已实现并验证

- actual_result: FastAPI 服务可启动；/api/v1/health 正常；统一响应/错误格式生效；SQLite 建表与种子数据可用；全部 v1 接口实现（登录、门店、菜单、订单、管理接口），含服务端金额重算、订单状态机、门店归属校验、幂等键、限库存原子扣减、entry_type 入口类型
- changed_owners: backend/app（core/models/schemas/services/api/v1）、backend/tests、dev-docs/runtime.md
- plan_deviation: 1.1 与 1.2 合并完成（骨架与业务接口一起交付）；健康检查接口最初遗漏，测试发现后补齐；种子脚本按模块方式运行（python -m app.seed）
- evidence_status: verified
- fresh_evidence: 2026-08-04 后端 pytest 32 passed；实机请求：health ok、下单 total=2400/status=pending、admin1 查单 1 单、跨店访问 HTTP 403
- remaining_risk: 严格 TDD 的 RED 阶段未按规范先行（本次先实现后补测试，后续以测试失败驱动修复）；仅本地验证，未做真机/浏览器验证
- next_substage: 1.3 商家后台
- git_checkpoint: 规划文档 + 后端骨架与 API 首次提交（见提交记录）

### 子阶段 1.2b（后端对齐设计稿 v3）— 执行中

- actual_result: 待执行（实施计划 dev-docs/plans/2026-08-04-backend-align.md）
- changed_owners: backend/app、backend/tests
- plan_deviation: 无
- evidence_status: unverified
- fresh_evidence: 基线 32 passed（2026-08-04）
- remaining_risk: 无
- next_substage: 1.2b 完成后进入 1.3 商家后台
- git_checkpoint: 待执行完成后提交

### 子阶段 1.2b 已完成

- actual_result: 6 项任务全部完成——SQLite WAL/单连接池；order_status 更名与取消字段；顾客/商家取消分类、事务化库存回补、幂等；查单收紧为手机号+订单号；商家列表脱敏；删除分类连带下架商品；订单组合索引
- changed_owners: backend/app/core/database.py、models/order.py、schemas/order.py、services/order_service.py、services/menu_service.py、api/v1/orders.py、api/v1/admin_orders.py、backend/tests
- plan_deviation: Task 2 与 Task 3 合并提交（字段更名与取消逻辑互相依赖，避免中间红提交）；本地演示库因 schema 变更删除重建（仅种子数据）
- evidence_status: verified
- fresh_evidence: pytest 43 passed（2026-08-04）；冒烟：下单扣库存 5→4、顾客取消回补→5、列表脱敏 139****0001、详情完整、跨店取消 403（自动化用例）
- remaining_risk: 商家后台与小程序的联调尚未做；跨店取消冒烟脚本 JSON 转义错误返回 422（脚本问题，非应用问题，应用由自动化用例覆盖）
- next_substage: 1.3 商家后台（需先出实施计划并获用户确认）
- git_checkpoint: feat/backend-align 分支 5 个提交（8d75245…9ac6bd4）
