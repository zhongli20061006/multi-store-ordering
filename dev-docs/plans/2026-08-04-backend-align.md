# 后端对齐设计稿 v3 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把当前后端对齐已定稿的设计（订单状态字段命名、顾客/商家取消分类、库存回补、查单收紧、分类联动、索引与 SQLite 配置），全部通过自动化测试。

**Architecture:** 保持现有 FastAPI 分层（api → services → models/schemas）不变；订单取消收敛为“专用取消接口 + 事务内状态机 + 按取消原因回补库存”；顾客查单改为手机号+订单号联合；商家列表脱敏。

**Tech Stack:** Python 3.11 / FastAPI 0.141 / SQLAlchemy 2.0 / SQLite（WAL）/ pytest。

---

## 环境注意

- 本机 Git 需要安全目录参数：`git -c safe.directory='C:/Users/g/Documents/多门店点单小程序' ...`
- 全部命令在 `backend/` 目录执行，虚拟环境 `.venv` 已就绪。
- 每个任务独立提交；提交前先 `git status --short` 确认暂存范围。

## 文件结构

| 文件 | 职责 |
| --- | --- |
| `backend/app/core/database.py` | 引擎与 SQLite 配置 |
| `backend/app/models/order.py` | 订单表字段与索引 |
| `backend/app/schemas/order.py` | 订单相关请求/响应契约 |
| `backend/app/services/order_service.py` | 订单业务规则唯一 owner（含取消与回补） |
| `backend/app/services/menu_service.py` | 菜单规则（分类下架联动） |
| `backend/app/api/v1/orders.py` | 顾客下单/取消/查单 |
| `backend/app/api/v1/admin_orders.py` | 商家订单管理 |
| `backend/tests/*` | 各行为回归门禁 |

---

### Task 1: SQLite 并发配置（WAL、busy_timeout、连接池=1）

**Files:**
- Modify: `backend/app/core/database.py`
- Test: `backend/tests/test_database.py`

- [ ] **Step 1: 写失败测试**

`backend/tests/test_database.py`:
```python
from app.core.database import create_db_engine


def test_sqlite_engine_enables_wal_and_busy_timeout(tmp_path):
    engine = create_db_engine(f"sqlite:///{tmp_path / 'cfg.db'}")
    with engine.connect() as conn:
        journal = conn.exec_driver_sql("PRAGMA journal_mode").scalar_one()
        timeout = conn.exec_driver_sql("PRAGMA busy_timeout").scalar_one()
    assert journal == "wal"
    assert timeout == 5000
    engine.dispose()
```

- [ ] **Step 2: 运行确认失败**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_database.py -v`
Expected: FAIL（journal 为 delete / busy_timeout 为 0）

- [ ] **Step 3: 实现**

`backend/app/core/database.py` 的 `create_db_engine` 改为：
```python
from sqlalchemy import create_engine, event


def create_db_engine(database_url: str):
    _prepare_sqlite_path(database_url)
    if database_url.startswith("sqlite"):
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            pool_size=1,
            max_overflow=0,
        )

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()

        return engine
    return create_engine(database_url)
```

- [ ] **Step 4: 运行确认通过**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_database.py -v`
Expected: PASS

- [ ] **Step 5: 全量回归 + 提交**

Run: `.\.venv\Scripts\python.exe -m pytest -q` → 全绿
```bash
git -c safe.directory='C:/Users/g/Documents/多门店点单小程序' add backend/app/core/database.py backend/tests/test_database.py
git -c safe.directory='C:/Users/g/Documents/多门店点单小程序' commit -m "feat: SQLite WAL/busy_timeout/单连接池配置"
```

---

### Task 2: 字段重命名 order_status + 取消字段 + 契约更新

**Files:**
- Modify: `backend/app/models/order.py`
- Modify: `backend/app/schemas/order.py`
- Modify: `backend/app/services/order_service.py`
- Modify: `backend/app/api/v1/admin_orders.py`
- Test: `backend/tests/test_orders.py`、`backend/tests/test_stores.py`

- [ ] **Step 1: 更新既有测试到新契约（先红）**

把测试里所有响应字段 `"status"` 改为 `"order_status"`；`PATCH /admin/orders/{id}/status` 请求体键改为 `{"order_status": ...}`。涉及 `test_orders.py`、`test_stores.py` 中相关断言。

- [ ] **Step 2: 运行确认失败**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_orders.py -q`
Expected: FAIL（KeyError: 'order_status'）

- [ ] **Step 3: 模型字段**

`backend/app/models/order.py`：
```python
order_status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
cancel_reason: Mapped[str | None] = mapped_column(String(32), nullable=True)
cancel_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
```
（原 `status` 字段删除；Integer 已导入。）

- [ ] **Step 4: 契约字段**

`backend/app/schemas/order.py`：
- 新增：
```python
class CancelReason(str, Enum):
    CUSTOMER_CANCEL = "customer_cancel"
    MERCHANT_CANCEL_NOT_MADE = "merchant_cancel_not_made"
    MERCHANT_CANCEL_MADE = "merchant_cancel_made"


class CustomerCancelRequest(BaseModel):
    phone: str = Field(pattern=r"^1[3-9]\d{9}$")


class MerchantCancelRequest(BaseModel):
    cancel_reason: CancelReason
```
- `OrderOut`：`status: OrderStatus` 改为 `order_status: OrderStatus`，并新增 `cancel_reason: CancelReason | None`、`cancel_by: int | None`。
- `OrderStatusUpdate`：`status: OrderStatus` 改为 `order_status: OrderStatus`。

- [ ] **Step 5: 服务与路由引用更新**

`backend/app/services/order_service.py`：
- `ALLOWED_TRANSITIONS` 改为（取消不再走 PATCH）：
```python
ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.ACCEPTED},
    OrderStatus.ACCEPTED: {OrderStatus.COMPLETED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}
```
- `update_order_status` 与 `mark_order_paid` 中 `order.status` → `order.order_status`。

`backend/app/api/v1/admin_orders.py`：
- 列表筛选参数 `status` → `order_status`，查询条件 `Order.status == status` → `Order.order_status == order_status`。
- `PATCH /{order_id}/status` 请求体 `OrderStatusUpdate` 自动带新字段。

- [ ] **Step 6: 全量测试**

Run: `.\.venv\Scripts\python.exe -m pytest -q` → 全绿（除取消相关旧断言，见 Task 3）

- [ ] **Step 7: 提交**

```bash
git -c safe.directory='C:/Users/g/Documents/多门店点单小程序' add backend
git -c safe.directory='C:/Users/g/Documents/多门店点单小程序' commit -m "refactor: 订单状态字段更名 order_status，新增取消原因/操作人字段"
```

---

### Task 3: 取消接口（顾客/商家）+ 事务化库存回补 + 幂等

**Files:**
- Modify: `backend/app/services/order_service.py`
- Modify: `backend/app/api/v1/orders.py`
- Modify: `backend/app/api/v1/admin_orders.py`
- Test: `backend/tests/test_cancel.py`

- [ ] **Step 1: 写失败测试**

`backend/tests/test_cancel.py`：
```python
from tests.conftest import login


def _create(client, seed, key, qty=1):
    return client.post(
        "/api/v1/orders",
        json={
            "store_id": seed["store1_id"],
            "customer_name": "测试顾客",
            "customer_phone": "13900000001",
            "idempotency_key": key,
            "items": [{"menu_item_id": seed["item2_id"], "quantity": qty}],
        },
    ).json()["data"]


def test_customer_cancel_pending_restocks(client, seed):
    order = _create(client, seed, "cancel-c-001")
    resp = client.post(
        f"/api/v1/orders/{order['order_no']}/cancel",
        json={"phone": "13900000001"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["order_status"] == "cancelled"
    assert data["cancel_reason"] == "customer_cancel"
    menu = client.get(f"/api/v1/stores/{seed['store1_id']}/menu").json()["data"]
    item = next(i for g in menu for i in g["items"] if i["id"] == seed["item2_id"])
    assert item["stock"] == 1  # 回补


def test_customer_cancel_rejected_after_accepted(client, seed):
    order = _create(client, seed, "cancel-c-002")
    headers = login(client, "admin1")
    client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"order_status": "accepted"},
        headers=headers,
    )
    resp = client.post(
        f"/api/v1/orders/{order['order_no']}/cancel",
        json={"phone": "13900000001"},
    )
    assert resp.status_code == 409


def test_customer_cancel_wrong_phone_not_found(client, seed):
    order = _create(client, seed, "cancel-c-003")
    resp = client.post(
        f"/api/v1/orders/{order['order_no']}/cancel",
        json={"phone": "13900000002"},
    )
    assert resp.status_code == 404


def test_merchant_cancel_not_made_restocks(client, seed):
    order = _create(client, seed, "cancel-m-001")
    headers = login(client, "admin1")
    resp = client.post(
        f"/api/v1/admin/orders/{order['id']}/cancel",
        json={"cancel_reason": "merchant_cancel_not_made"},
        headers=headers,
    )
    assert resp.status_code == 200
    menu = client.get(f"/api/v1/stores/{seed['store1_id']}/menu").json()["data"]
    item = next(i for g in menu for i in g["items"] if i["id"] == seed["item2_id"])
    assert item["stock"] == 1


def test_merchant_cancel_made_does_not_restock(client, seed):
    order = _create(client, seed, "cancel-m-002")
    headers = login(client, "admin1")
    resp = client.post(
        f"/api/v1/admin/orders/{order['id']}/cancel",
        json={"cancel_reason": "merchant_cancel_made"},
        headers=headers,
    )
    assert resp.status_code == 200
    menu = client.get(f"/api/v1/stores/{seed['store1_id']}/menu").json()["data"]
    item = next(i for g in menu for i in g["items"] if i["id"] == seed["item2_id"])
    assert item["stock"] == 0  # 不回补


def test_double_cancel_is_idempotent(client, seed):
    order = _create(client, seed, "cancel-m-003")
    headers = login(client, "admin1")
    first = client.post(
        f"/api/v1/admin/orders/{order['id']}/cancel",
        json={"cancel_reason": "merchant_cancel_not_made"},
        headers=headers,
    )
    second = client.post(
        f"/api/v1/admin/orders/{order['id']}/cancel",
        json={"cancel_reason": "merchant_cancel_not_made"},
        headers=headers,
    )
    assert first.status_code == 200 and second.status_code == 200
    menu = client.get(f"/api/v1/stores/{seed['store1_id']}/menu").json()["data"]
    item = next(i for g in menu for i in g["items"] if i["id"] == seed["item2_id"])
    assert item["stock"] == 1  # 只回补一次


def test_admin_cancel_cross_store_blocked(client, seed):
    order = _create(client, seed, "cancel-m-004")
    headers = login(client, "admin2")
    resp = client.post(
        f"/api/v1/admin/orders/{order['id']}/cancel",
        json={"cancel_reason": "merchant_cancel_not_made"},
        headers=headers,
    )
    assert resp.status_code == 403
```

同时把 `test_orders.py` 中旧的“PATCH 取消”用例改为走取消接口：
- `test_status_machine_allows_valid_and_rejects_invalid`：PATCH 到 accepted 后，用 `POST /admin/orders/{id}/cancel`（merchant_cancel_not_made）取消。
- `test_mark_paid_ok_and_cancelled_rejected`：取消步骤同样改为取消接口。

- [ ] **Step 2: 运行确认失败**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_cancel.py -q`
Expected: FAIL（404 路由不存在）

- [ ] **Step 3: 服务层取消逻辑**

`backend/app/services/order_service.py` 追加：
```python
def cancel_order(db: Session, order: Order, reason: CancelReason, actor_id: int | None) -> Order:
    if order.order_status == OrderStatus.CANCELLED.value:
        return order  # 幂等：已取消直接返回，不重复回补
    current = OrderStatus(order.order_status)
    if current not in (OrderStatus.PENDING, OrderStatus.ACCEPTED):
        raise BusinessError(409, "当前状态不可取消")
    if reason == CancelReason.CUSTOMER_CANCEL:
        if current != OrderStatus.PENDING:
            raise BusinessError(409, "已接单后顾客不能取消")
    elif reason not in (CancelReason.MERCHANT_CANCEL_NOT_MADE, CancelReason.MERCHANT_CANCEL_MADE):
        raise BusinessError(400, "取消原因不合法")
    order.order_status = OrderStatus.CANCELLED.value
    order.cancel_reason = reason.value
    order.cancel_by = actor_id
    if reason != CancelReason.MERCHANT_CANCEL_MADE:
        _restock_items(db, order)
    db.commit()
    db.refresh(order)
    return order


def _restock_items(db: Session, order: Order) -> None:
    for item in order.items:
        if item.menu_item_id is None:
            continue
        db.execute(
            update(MenuItem)
            .where(MenuItem.id == item.menu_item_id, MenuItem.stock.isnot(None))
            .values(stock=MenuItem.stock + item.quantity)
        )
```
（顶部 import 增加 `from app.schemas.order import CancelReason`。）

- [ ] **Step 4: 顾客取消与商家取消路由**

`backend/app/api/v1/orders.py` 追加：
```python
from app.core.errors import BusinessError
from app.schemas.order import CancelReason, CustomerCancelRequest
from app.services.order_service import cancel_order


@router.post("/orders/{order_no}/cancel")
def customer_cancel(order_no: str, payload: CustomerCancelRequest, db: Session = Depends(get_db)):
    order = db.scalar(select(Order).where(Order.order_no == order_no))
    if order is None or order.customer_phone != payload.phone:
        raise BusinessError(404, "订单不存在")
    return ok(OrderOut.model_validate(cancel_order(db, order, CancelReason.CUSTOMER_CANCEL, 0)).model_dump())
```

`backend/app/api/v1/admin_orders.py` 追加：
```python
from app.schemas.order import MerchantCancelRequest
from app.services.order_service import cancel_order


@router.post("/{order_id}/cancel")
def admin_cancel(order_id: int, payload: MerchantCancelRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = get_order(db, order_id)
    if order is None:
        raise BusinessError(404, "订单不存在")
    ensure_store_access(user, order.store_id)
    if payload.cancel_reason.value == "customer_cancel":
        raise BusinessError(400, "商家取消原因不合法")
    return ok(OrderOut.model_validate(cancel_order(db, order, payload.cancel_reason, user.id)).model_dump())
```

- [ ] **Step 5: 全量测试**

Run: `.\.venv\Scripts\python.exe -m pytest -q` → 全绿

- [ ] **Step 6: 提交**

```bash
git -c safe.directory='C:/Users/g/Documents/多门店点单小程序' add backend
git -c safe.directory='C:/Users/g/Documents/多门店点单小程序' commit -m "feat: 顾客/商家取消分类、事务化库存回补、幂等"
```

---

### Task 4: 查单收紧（手机号+订单号）与商家列表脱敏

**Files:**
- Modify: `backend/app/api/v1/orders.py`
- Modify: `backend/app/api/v1/admin_orders.py`
- Test: `backend/tests/test_orders.py`

- [ ] **Step 1: 更新测试（先红）**

`test_orders.py` 中 `test_idempotent_replay_returns_same_order`、`test_my_orders_only_returns_that_phone` 改为：
- 查单必须带 `phone` 和 `order_no` 两个参数；
- 只传 phone → 422；手机号与订单号不匹配 → 404；匹配 → 返回该订单。

- [ ] **Step 2: 实现**

`backend/app/api/v1/orders.py`：
```python
@router.get("/orders")
def get_my_order(
    phone: str = Query(pattern=r"^1[3-9]\d{9}$"),
    order_no: str = Query(min_length=8, max_length=32),
    db: Session = Depends(get_db),
):
    order = db.scalar(select(Order).where(Order.order_no == order_no, Order.customer_phone == phone))
    if order is None:
        raise BusinessError(404, "订单不存在")
    return ok(OrderOut.model_validate(order).model_dump())
```

`backend/app/api/v1/admin_orders.py` 列表返回脱敏：
```python
def mask_phone(phone: str) -> str:
    return f"{phone[:3]}****{phone[-4:]}" if len(phone) == 11 else phone


@router.get("")
def list_admin_orders(
    store_id: int | None = None,
    order_status: str | None = Query(default=None, pattern="^(pending|accepted|completed|cancelled)$"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    store_ids = get_user_store_ids(user)
    query = select(Order).where(Order.store_id.in_(store_ids))
    if store_id is not None:
        ensure_store_access(user, store_id)
        query = query.where(Order.store_id == store_id)
    if order_status is not None:
        query = query.where(Order.order_status == order_status)
    orders = list(db.scalars(query.order_by(Order.created_at.desc(), Order.id.desc())))
    payload = []
    for order in orders:
        data = OrderOut.model_validate(order).model_dump()
        data["customer_phone"] = mask_phone(data["customer_phone"])
        payload.append(data)
    return ok(payload)
```
（详情接口 `GET /{order_id}` 保持完整号码。）

- [ ] **Step 3: 全量测试**

Run: `.\.venv\Scripts\python.exe -m pytest -q` → 全绿

- [ ] **Step 4: 提交**

```bash
git -c safe.directory='C:/Users/g/Documents/多门店点单小程序' add backend
git -c safe.directory='C:/Users/g/Documents/多门店点单小程序' commit -m "feat: 顾客查单收紧为手机号+订单号，商家列表脱敏"
```

---

### Task 5: 分类下架联动商品

**Files:**
- Modify: `backend/app/services/menu_service.py`
- Test: `backend/tests/test_menu.py`

- [ ] **Step 1: 写失败测试**

`backend/tests/test_menu.py` 追加：
```python
def test_delete_category_deactivates_its_items(client, seed):
    headers = login(client, "admin1")
    resp = client.delete(
        f"/api/v1/admin/stores/{seed['store1_id']}/categories/{seed['cat1_id']}",
        headers=headers,
    )
    assert resp.status_code == 200
    menu = client.get(f"/api/v1/stores/{seed['store1_id']}/menu").json()["data"]
    item_ids = {item["id"] for group in menu for item in group["items"]}
    assert seed["item1_id"] not in item_ids
    order = client.post(
        "/api/v1/orders",
        json={
            "store_id": seed["store1_id"],
            "customer_name": "测试顾客",
            "customer_phone": "13900000001",
            "idempotency_key": "cat-inactive-key-001",
            "items": [{"menu_item_id": seed["item1_id"], "quantity": 1}],
        },
    )
    assert order.status_code == 400
```

- [ ] **Step 2: 运行确认失败**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_menu.py::test_delete_category_deactivates_its_items -v`
Expected: FAIL（item1 仍可见/可下单）

- [ ] **Step 3: 实现**

`backend/app/services/menu_service.py` 的 `delete_category` 改为：
```python
def delete_category(db: Session, category: MenuCategory) -> None:
    category.is_active = False
    db.execute(
        update(MenuItem)
        .where(MenuItem.category_id == category.id, MenuItem.is_active.is_(True))
        .values(is_active=False)
    )
    db.commit()
```
（顶部 import 增加 `from sqlalchemy import select, update`。）

- [ ] **Step 4: 全量测试**

Run: `.\.venv\Scripts\python.exe -m pytest -q` → 全绿

- [ ] **Step 5: 提交**

```bash
git -c safe.directory='C:/Users/g/Documents/多门店点单小程序' add backend
git -c safe.directory='C:/Users/g/Documents/多门店点单小程序' commit -m "fix: 删除分类连带下架分类内商品"
```

---

### Task 6: 订单组合索引

**Files:**
- Modify: `backend/app/models/order.py`
- Test: `backend/tests/test_orders.py`

- [ ] **Step 1: 写失败测试**

`backend/tests/test_orders.py` 追加：
```python
from sqlalchemy import inspect


def test_orders_composite_index_exists(client, seed, db_session_factory):
    engine = db_session_factory().get_bind()
    indexes = {ix["name"]: ix for ix in inspect(engine).get_indexes("orders")}
    target = indexes.get("ix_orders_store_status_created")
    assert target is not None
    assert sorted(target["column_names"]) == ["created_at", "order_status", "store_id"]
```

- [ ] **Step 2: 运行确认失败**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_orders.py::test_orders_composite_index_exists -v`
Expected: FAIL（索引不存在）

- [ ] **Step 3: 实现**

`backend/app/models/order.py`：
```python
from sqlalchemy import ForeignKey, Index, Integer, String

order_status: Mapped[str] = mapped_column(String(16), default="pending")

Index("ix_orders_store_status_created", "store_id", "order_status", "created_at")
```
（删除原 `order_status` 上的 `index=True`，由组合索引覆盖。）

- [ ] **Step 4: 全量测试**

Run: `.\.venv\Scripts\python.exe -m pytest -q` → 全绿

- [ ] **Step 5: 提交**

```bash
git -c safe.directory='C:/Users/g/Documents/多门店点单小程序' add backend
git -c safe.directory='C:/Users/g/Documents/多门店点单小程序' commit -m "perf: 订单组合索引 (store_id, order_status, created_at)"
```

---

## 完成验证

1. `.\.venv\Scripts\python.exe -m pytest -q` → 全绿（含新增取消/脱敏/索引/联动用例）
2. 启动服务做冒烟：登录 admin1 → 下一单（限库存商品）→ 顾客取消 → 库存回补 → 商家列表手机号脱敏 → 详情完整
3. 更新 `dev-docs/runtime.md` 与 `dev-docs/stages/stage-1.md` 实施回写，提交 Git 检查点
