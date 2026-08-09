# 多门店点单 · 后端服务

多门店线上点单系统的后端：负责门店、菜单、订单、商家登录等全部业务规则与数据存储，为微信小程序（顾客端）和网页后台（商家端）提供统一接口。

## 技术栈

- Python 3.11 + FastAPI（接口框架，自带 OpenAPI 文档）
- SQLAlchemy 2.0（ORM）+ SQLite（本地开发，WAL 模式）；上线可切换 PostgreSQL
- PyJWT + bcrypt（登录令牌与密码加密）
- pytest + httpx（接口测试）

## 目录结构

```text
backend/
├── app/
│   ├── main.py          # 应用入口：路由挂载、异常处理、CORS
│   ├── core/            # 配置、数据库、安全、响应格式
│   ├── models/          # 数据表定义（用户/门店/菜单/订单）
│   ├── schemas/         # 请求与响应契约
│   ├── services/        # 业务规则唯一 owner（金额/状态机/取消回补/归属校验）
│   ├── api/v1/          # 接口路由（公共 + 商家管理）
│   └── seed.py          # 演示数据初始化
├── migrations/          # Alembic 迁移（0001 幂等基线 / 0002 首启改密字段）
├── tests/               # pytest 测试
├── data/                # 本地 SQLite 数据库（不入库）
├── alembic.ini
├── requirements.txt
└── .env.example         # 环境变量示例（复制为 .env 使用）
```

## 快速开始

环境要求：Python 3.11+，Windows 下在 `backend/` 目录执行以下命令。

```powershell
# 1. 创建虚拟环境并安装依赖
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt

# 2. 配置环境变量（密钥、种子管理员密码）
Copy-Item .env.example .env

# 3. 初始化本地数据库与演示数据（自动执行 Alembic 迁移；幂等，重复执行会跳过）
.\.venv\Scripts\python -m app.seed

# 4. 启动服务
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000

# 5. 运行测试
.\.venv\Scripts\python -m pytest
```

启动后接口文档：<http://127.0.0.1:8000/docs>；健康检查：<http://127.0.0.1:8000/api/v1/health>

## 演示账号（仅本地开发）

| 账号 | 密码 | 绑定门店 |
| --- | --- | --- |
| admin1 | admin123456 | 中山路店 |
| admin2 | admin123456 | 万达店 |

默认密码仅用于本地演示：种子账号带 `must_change_password` 标记，首次登录后台会强制要求修改密码；正式使用前还必须修改 `.env` 中的 JWT 密钥。

## 数据库迁移（Alembic）

- 启动/种子自动执行：`app.core.database.init_db()` 调用 `alembic upgrade head`。
- 手动执行：`.\.venv\Scripts\python -m alembic upgrade head`。
- 生成新迁移：先改模型，再执行 `.\.venv\Scripts\python -m alembic revision --autogenerate -m "描述"`，人工复核后提交。
- 存量演示库兼容：`0001` 基线迁移幂等（跳过已有表、补历史缺失列），存量库首次升级不会重建数据。

## API 概览

统一前缀 `/api/v1`；成功返回 `{"code":0,"message":"ok","data":...}`，失败返回 `{"code":<http状态>,"message":"..."}`。

### 公共接口（顾客小程序）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | /health | 健康检查 |
| GET | /stores | 营业中门店列表 |
| GET | /stores/{id}/menu | 门店菜单（分类 + 上架商品） |
| POST | /orders | 创建订单（服务端重算金额、幂等防重、限库存原子扣减） |
| POST | /orders/{order_no}/cancel | 顾客取消待接单订单（校验手机号；回补库存） |
| GET | /orders?phone=&order_no= | 查单（手机号 + 订单号缺一不可） |

### 管理接口（商家后台，需 JWT）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | /auth/login | 登录 |
| GET | /auth/me | 当前用户 |
| GET/POST | /admin/stores | 门店列表 / 新建 |
| PUT/DELETE | /admin/stores/{id} | 编辑 / 删除（有订单禁止删除） |
| PATCH | /admin/stores/{id}/status | 开/关店 |
| GET/POST/PUT/DELETE | /admin/stores/{id}/categories | 分类管理（删除连带下架分类内商品） |
| GET/POST/PUT/DELETE | /admin/stores/{id}/items | 商品管理（删除=下架；可设限库存） |
| GET | /admin/orders | 订单列表（store_id/order_status 筛选；手机号脱敏） |
| GET | /admin/orders/{id} | 订单详情（含明细与完整电话） |
| PATCH | /admin/orders/{id}/status | 接单 / 完成 |
| POST | /admin/orders/{id}/cancel | 商家取消（原因：未制作 / 已制作） |
| PATCH | /admin/orders/{id}/payment | 标记到店付款 |

## 核心业务规则

- **金额可信**：订单总额由服务端按数据库商品价格重算，前端提交的金额字段被忽略；金额一律以“分”存储。
- **订单状态机**：待接单 → 已接单 → 已完成；取消走专用取消接口，禁止跳步。
- **取消与库存回补**：顾客取消仅限待接单；商家取消需选择“未制作/已制作”。未制作的取消在事务内回补限库存商品的库存，已制作不回补；重复取消幂等，不会重复回补。
- **防超卖**：限库存商品下单时数据库原子扣减（`stock >= quantity`），不足整单拒绝；订单幂等键防止连点重复下单。
- **门店隔离**：商品、菜单、订单全部带门店标记；商家只能操作自己绑定的门店，越权返回 403。
- **隐私**：顾客查单必须“手机号 + 订单号”；商家订单列表手机号脱敏，详情显示完整号码（限有权限账号）。
- **SQLite 配置**：WAL 模式、busy_timeout、单连接池，本地原型足够；上线切换 PostgreSQL。

## 二期预留（当前不实现）

- 支付：订单保留“未付款/已付款”状态；支付记录表按渠道（微信/支付宝）记录，回调自动更新。
- 美团/抖音团购券核销：新增核销记录表，一张券只核销一次，入口在商家后台。
- 微信登录（顾客/商家）、隐私号加密通话：列入演进评估。

## 安全注意事项

- `.env` 不入库；`.env.example` 仅作模板。
- 演示密码与默认 JWT 密钥只用于本地开发，正式部署前必须更换。
- CORS 当前为本地调试全开，上线前收紧。
- 更多边界见 `../dev-docs/security-boundary.md`（内部文档，默认不随代码公开推送）。
