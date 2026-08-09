# 多门店线上点单系统

一个面向小商家多门店场景的线上点单系统：顾客用**微信小程序**选店、看菜单、提前点单，商家用**网页后台**接单、出餐、管店，后端统一承载业务规则与数据。到店付款，原型阶段不接入在线支付。

> 许可证：[MIT](LICENSE) ｜ 测试：[CI](.github/workflows/ci.yml) ｜ 文档：[架构说明](#架构) ｜ [路线图](ROADMAP.md) ｜ [参与贡献](CONTRIBUTING.md)

## 功能特性

### 顾客端（微信小程序 `miniprogram/`）

- 门店列表（营业中门店）→ 门店菜单（分类/商品/轮播）→ 加购 → 确认下单 → 下单成功
- 完整订单状态机：待接单 → 已接单 → 已出单 → 顾客确认取单 → 已完成
- 待接单可取消（限库存商品自动回补）；查单需「手机号 + 订单号」
- 门店营业时间（支持跨天 22:00-02:00，打烊拒单）、门店电话 + 一键导航、下单成功页/详情页门店信息卡
- 菜单搜索、门店搜索、商品详情页（规格选择/数量/备注）直下单、结算页可编辑（库存不足自动修正）
- 「我的」个人主页（本地资料预填）、最近订单、历史记录（筛选/搜索/删除）、全局订单监控通知、首页通知入口
- 扫码直达菜单（编译模式模拟；真机小程序码需正式 AppID）、再来一单
- 门店主题换肤：四套主题（warm 熟食 / white 奶茶 / green 夜宵 / berry 甜品），后台可按门店切换

### 商家端（网页后台 `admin/`）

- 登录鉴权（JWT）、门店切换、个人中心（改密码/退出）
- 门店管理（开/关店、编辑、删除保护、营业时间、经纬度、封面图、主题）
- 菜单管理（分类与商品 CRUD、上下架、限库存、商品图片、规格组）
- 订单管理：按门店/状态/关键词/日期筛选、8 秒轮询、接单 → 出单单按钮推进、取消（未制作回补/已制作不回补）、标记到店付款、小票打印、CSV 导出（手机号脱敏 + 公式注入转义）
- 数据看板（近 7 天趋势 + 今日统计）、轮播图管理、订单操作审计（列表/日期筛选/分页/导出）
- 订单搜索、新订单声音 + 桌面提醒、低库存高亮

### 后端（FastAPI `backend/`）

- 统一 `/api/v1` 接口：门店、菜单、下单、查单、顾客取消/取单、商家登录与管理
- 金额一律服务端按数据库价格重算（分存储）；订单状态机仅服务层可迁移
- 幂等下单（客户端幂等键 + 服务端唯一索引兜底）、限库存原子扣减防超卖
- 顾客查单收紧为「手机号 + 订单号」；商家列表手机号脱敏；所有管理接口校验门店归属（越权 403）
- SQLite（WAL）+ Alembic 迁移；方言隔离，上线可切换 PostgreSQL

## 技术栈

| 端 | 技术 |
| --- | --- |
| 顾客小程序 | 微信原生小程序（JS），微信开发者工具 + 测试号 |
| 商家后台 | Vue 3 + TypeScript + Vite + Element Plus + Pinia + vue-router |
| 后端 | Python 3.11 + FastAPI + SQLAlchemy 2.0 + SQLite + PyJWT + bcrypt + Alembic |
| 测试 | pytest（后端）、vitest（后台）、node:test（小程序纯逻辑） |

## 架构

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
              SQLite（原型，Alembic 迁移）
              （生产可切 PostgreSQL，方言隔离）
```

### 开源边界（open-core 预留）

本项目**先全量开源**当前原型能力，同时为商业能力预留接入缝（不写假实现）：

- 在线支付、微信登录、美团/抖音团购券核销、外卖配送：**不在本仓库实现**，订单保留 `payment_status`、用户表保留 `openid` 等占位字段，阶段四接入时按官方文档另行设计。
- 本仓库不含真实密钥、生产配置与内部开发文档（`dev-docs/` 本地保留，不随仓库推送）。

## 项目结构

```text
.
├── backend/          # FastAPI 后端（app/api、app/services、app/models、app/schemas、app/core、migrations）
├── admin/            # 商家网页后台（Vue 3 + Element Plus）
├── miniprogram/      # 顾客微信小程序（原生 JS）
├── .github/          # CI 工作流、issue/PR 模板
├── AGENTS.md         # 项目协作约定
├── CONTRIBUTING.md   # 贡献指南
├── ROADMAP.md        # 路线图
├── SECURITY.md       # 安全说明
└── LICENSE           # MIT 许可证
```

## 快速开始

环境要求：Python 3.11+、Node.js 20+（建议 24）、npm、微信开发者工具（预览小程序时）。

### 1. 启动后端（FastAPI，端口 8000）

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
Copy-Item .env.example .env        # 生成环境变量文件（必做，含密钥与种子管理员密码）
.\.venv\Scripts\python.exe -m app.seed     # Alembic 迁移 + 演示数据（幂等，可重跑）
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- 健康检查：<http://127.0.0.1:8000/api/v1/health>
- 接口文档：<http://127.0.0.1:8000/docs>

### 2. 启动商家后台（Vite，端口 5173）

```powershell
cd admin
npm install
npm run dev
```

浏览器访问 <http://localhost:5173/login>（注意用 localhost，Vite 监听 IPv6）。

### 3. 运行顾客小程序（微信开发者工具）

1. 微信开发者工具「导入项目」，目录选 `miniprogram/`，AppID 用测试号；
2. 「详情 → 本地设置」勾选「不校验合法域名」（本地 http 接口）；
3. 接口地址在 `miniprogram/config.js` 的 `BASE_URL`：模拟器用 `http://127.0.0.1:8000/api/v1`，真机预览改为电脑局域网 IP（后端需 `--host 0.0.0.0` 启动并放行 8000 端口防火墙）；
4. 模拟扫码：编译模式启动页 `pages/menu/menu`，参数 `store_id=1`（不带 entry_type，缺省到店点单）。

## 演示账号（仅本地开发）

| 账号 | 密码 | 绑定门店 |
| --- | --- | --- |
| admin1 | admin123456 | 中山路店（熟食/warm）、夜宵摊（夜宵/green） |
| admin2 | admin123456 | 万达店（奶茶/white）、甜品店（甜品/berry） |

演示店铺共四家，对应四种主题与餐饮模式（熟食/奶茶/夜宵/甜品），菜单已配齐。**默认密码仅用于本地演示，首次登录系统会要求修改；正式使用前必须更换 `.env` 中的 `JWT_SECRET` 与种子密码。**

## 截图

> 主题走查截图与商品/门店/轮播实拍图正在补充归档，完成后更新本节。

## 订单状态机

```text
待接单 ──商家接单──▶ 已接单 ──商家出单──▶ 已出单 ──顾客确认取单──▶ 已完成
   │                  │
   └──── 取消 ────────┘（顾客仅限待接单；商家限待接单/已接单，出单后不可取消）
```

## 测试

```powershell
cd backend && .\.venv\Scripts\python.exe -m pytest -q     # 123 passed（2026-08-09 基线）
cd admin && npm run test && npm run build                 # vitest 16 passed + 构建通过
cd miniprogram && npm test                                # node:test 76 passed
```

## 已知边界与未验证项

- 真机扫码直达（小程序码生成与 scene 解析）需正式 AppID，属原型外能力。
- 4 位订单号按门店每日唯一、隔天可复用；上线前应换正式单号方案。
- 无在线支付、微信登录、美团/抖音核销、外卖配送、会员营销（阶段四/五，待资质）。
- 真机图片显示依赖 HTTPS（本地 http 图片在真机不渲染，后端已确认正常），列入阶段四部署前。
- 本地数据库 `backend/data/ordering.db` 与图片 `backend/uploads/` 不入库，删除后重跑 seed 即可。
- `dev-docs/` 为内部开发真源，仅本地保留，不随仓库推送；本仓库提供脱敏公开版文档（README/架构/路线图）。

## 路线图

- 阶段一（已完成）：后端搭建（FastAPI 全部能力）
- 阶段二（已完成 2.1-2.8）：小程序功能搭建与体验、商家后台随做
- 阶段三（进行中）：项目 UI 重构（A/B 批基本完成，走查截图归档中）
- 阶段四/五（挂起，待资质）：部署前准备（支付/登录/核销/部署物料）与正式上线

完整规划见 [ROADMAP.md](ROADMAP.md)。

## 参与贡献

欢迎提交 issue 与 PR，请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [SECURITY.md](SECURITY.md)。
