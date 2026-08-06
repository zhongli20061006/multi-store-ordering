# 多门店线上点单系统

一个本地原型的多门店线上点单系统：顾客用微信小程序选店点单，商家用网页后台接单管理，后端统一承载业务规则与数据。

> 当前状态：阶段一（本地原型）已完成并通过验收。本阶段不包含在线支付、微信登录、第三方核销、外卖配送与线上部署，均为二期/明确非目标。

## 功能特性

### 顾客端（微信小程序 `miniprogram/`）

- 门店列表（营业中门店）→ 门店菜单（分类/商品）→ 加购 → 确认下单 → 下单成功
- 4 位随机订单号（1000–9999，按门店每天唯一，隔天可复用）
- 最近 5 单本地历史：下单成功自动写入，我的订单页直接展示并每 8 秒静默刷新状态
- 完整订单状态机：待接单 → 已接单 → 已出单 → 顾客确认取单 → 已完成
- 待接单可取消（限库存商品自动回补）；查单需「手机号 + 订单号」
- 扫码直达菜单（编译模式模拟；真机小程序码需正式 AppID）
- 菜单搜索（按商品名即时过滤）与商品图片展示
- 门店营业时间展示（打烊时段后端拒绝下单）
- 门店搜索（按店名过滤）、订单详情页（本地秒开+静默刷新）、再来一单
- 「我的」个人主页（本地资料、订单状态筛选、本地通知）、菜单页轮播图
- 历史记录（按类别筛选/订单号搜索）、首页通知入口（未读角标）

### 商家端（网页后台 `admin/`）

- 登录鉴权（JWT）、门店切换、个人中心（改密码/退出）
- 门店管理（开/关店、编辑、删除保护、营业时间维护）
- 菜单管理（分类与商品，删除商品转下架，支持限库存、商品图片上传）
- 订单管理：按门店/状态筛选、8 秒轮询、单按钮状态推进（接单 → 出单）、取消（未制作回补/已制作不回补）、标记到店付款、详情查看（手机号脱敏列表 / 详情完整）、小票打印
- 数据看板：近 7 天营业额趋势与今日统计

### 后端（FastAPI `backend/`）

- 全部 v1 接口：门店、菜单、下单、查单、顾客取消/取单、商家登录与管理接口
- 金额一律服务端按数据库价格重算（分存储）；订单状态机仅服务层可迁移
- 幂等下单（客户端幂等键 + 服务端唯一索引兜底）、限库存原子扣减防超卖
- 顾客查单收紧为「手机号 + 订单号」；商家列表手机号脱敏
- SQLite WAL + 单连接池，本地原型足够，上线可切换 PostgreSQL

## 技术栈

| 端 | 技术 |
| --- | --- |
| 顾客小程序 | 微信原生小程序（JS），微信开发者工具 + 测试号 |
| 商家后台 | Vue 3 + TypeScript + Vite + Element Plus + Pinia + vue-router |
| 后端 | Python 3.11 + FastAPI + SQLAlchemy 2.0 + SQLite + PyJWT + bcrypt |
| 测试 | pytest（后端）、vitest（后台）、node:test（小程序纯逻辑） |

## 项目结构

```text
.
├── backend/          # FastAPI 后端（app/api、app/services、app/models、app/schemas、app/core）
├── admin/            # 商家网页后台（Vue 3 + Element Plus）
├── miniprogram/      # 顾客微信小程序（原生 JS，双 tab + 5 页面）
├── dev-docs/         # 内部开发真源（本地保留，不进 Git、不推送远端）
├── AGENTS.md         # 项目协作约定
└── .gitignore
```

## 快速开始

环境要求：Windows，Python 3.11+，Node.js 20+，npm，微信开发者工具。

### 1. 后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
Copy-Item .env.example .env        # 配置密钥与种子密码（本地开发）
.\.venv\Scripts\python.exe -m app.seed
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- 健康检查：<http://127.0.0.1:8000/api/v1/health>
- 接口文档：<http://127.0.0.1:8000/docs>

### 2. 商家后台

```powershell
cd admin
npm install
npm run dev
```

浏览器访问 <http://localhost:5173/login>（注意用 localhost，Vite 监听 IPv6）。

### 3. 顾客小程序

1. 微信开发者工具「导入项目」，目录选 `miniprogram/`，AppID 用测试号；
2. 「详情 → 本地设置」勾选「不校验合法域名」（本地 http 接口）；
3. 接口地址在 `miniprogram/config.js` 的 `BASE_URL` 配置：模拟器用 `127.0.0.1:8000`，真机预览改为电脑局域网 IP（后端需 `--host 0.0.0.0` 启动并放行 8000 端口防火墙）；
4. 模拟扫码：编译模式启动 `pages/menu/menu`，参数 `store_id=1`（不带 entry_type，缺省到店点单）。

## 演示账号（仅本地开发）

| 账号 | 密码 | 绑定门店 |
| --- | --- | --- |
| admin1 | admin123456 | 中山路店 |
| admin2 | admin123456 | 万达店 |

正式使用前必须修改 `.env` 中的 JWT 密钥与种子密码。

## 订单状态机

```text
待接单 ──商家接单──▶ 已接单 ──商家出单──▶ 已出单 ──顾客确认取单──▶ 已完成
   │                  │
   └──── 取消 ────────┘（顾客仅限待接单；商家限待接单/已接单，出单后不可取消）
```

## 测试

```powershell
cd backend && .\.venv\Scripts\python.exe -m pytest -q     # 72 passed
cd admin && npm run test && npm run build                 # vitest 7 passed + 构建通过
cd miniprogram && node --test tests/                      # 45 passed
```

> 沙箱受限环境下 node:test 需加 `--experimental-test-isolation=none` 并显式列出测试文件。

## 已知限制与未验证项

- 真机扫码直达（小程序码生成与 scene 解析）需正式 AppID，属原型外能力
- 4 位订单号隔天复用未做自然日实测（代码与测试覆盖；上线前换正式单号方案）
- 无在线支付、微信登录、美团/抖音核销、外卖配送、会员营销（二期）
- 本地开发数据库 `backend/data/ordering.db` 不入库，删除后重新执行 seed 即可
- 商品图片存本地 `backend/uploads/`（不入库），上线前评估切换对象存储

## 路线图

- 阶段一（已完成）：本地原型闭环 —— 顾客小程序点单 + 商家后台管理 + FastAPI 后端
- 阶段二（待确认）：美团/抖音团购券核销（实施前核查平台官方文档与资质）；上线部署相关能力

## 说明

- `dev-docs/` 为内部开发真源，仅本地保留，不随仓库推送
- 顾客手机号属于个人信息，仅用于订单联系与查询；原型期最近 5 单本地暂存手机号用于状态刷新，上线前评估移除/加密
