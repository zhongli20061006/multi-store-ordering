"""baseline: initial schema (idempotent for existing DBs)

Revision ID: 09b7215bc9ed
Revises:
Create Date: 2026-08-09 12:02:28.752129

本基线迁移兼容两种库：
1. 全新空库：按当前模型建全表与索引；
2. 存量演示库（create_all + ensure_additive_columns 时代遗留）：
   已有表跳过建表，仅补历史缺失列（stores 营业时间/经纬度/封面/主题、
   menu_items.spec_groups、order_items.specs/category_name），随后写入 alembic_version。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "09b7215bc9ed"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _bind():
    return op.get_bind()


def _table_exists(table: str) -> bool:
    return sa.inspect(_bind()).has_table(table)


def _columns(table: str) -> set[str]:
    return {col["name"] for col in sa.inspect(_bind()).get_columns(table)}


def _index_exists(table: str, index_name: str) -> bool:
    return any(ix["name"] == index_name for ix in sa.inspect(_bind()).get_indexes(table))


def _create_index(table: str, index_name: str, columns: list[str], unique: bool = False) -> None:
    if not _index_exists(table, index_name):
        op.create_index(index_name, table, columns, unique=unique)


def upgrade() -> None:
    # stores
    if not _table_exists("stores"):
        op.create_table(
            "stores",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=80), nullable=False),
            sa.Column("address", sa.String(length=200), nullable=False),
            sa.Column("phone", sa.String(length=20), nullable=False),
            sa.Column("latitude", sa.Float(), nullable=True),
            sa.Column("longitude", sa.Float(), nullable=True),
            sa.Column("image_url", sa.Text(), nullable=True),
            sa.Column("theme", sa.String(length=16), nullable=False),
            sa.Column("status", sa.String(length=16), nullable=False),
            sa.Column("open_time", sa.String(length=5), nullable=True),
            sa.Column("close_time", sa.String(length=5), nullable=True),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        _create_index("stores", "ix_stores_status", ["status"])
    else:
        store_cols = _columns("stores")
        if "open_time" not in store_cols:
            op.add_column("stores", sa.Column("open_time", sa.String(length=5), nullable=True))
        if "close_time" not in store_cols:
            op.add_column("stores", sa.Column("close_time", sa.String(length=5), nullable=True))
        if "latitude" not in store_cols:
            op.add_column("stores", sa.Column("latitude", sa.Float(), nullable=True))
        if "longitude" not in store_cols:
            op.add_column("stores", sa.Column("longitude", sa.Float(), nullable=True))
        if "image_url" not in store_cols:
            op.add_column("stores", sa.Column("image_url", sa.Text(), nullable=True))
        if "theme" not in store_cols:
            op.add_column("stores", sa.Column("theme", sa.String(length=16), server_default="warm", nullable=False))
        if "status" not in store_cols:
            op.add_column("stores", sa.Column("status", sa.String(length=16), server_default="open", nullable=False))
        _create_index("stores", "ix_stores_status", ["status"])

    # users
    if not _table_exists("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("username", sa.String(length=64), nullable=False),
            sa.Column("password_hash", sa.String(length=128), nullable=False),
            sa.Column("display_name", sa.String(length=64), nullable=False),
            sa.Column("openid", sa.String(length=128), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        _create_index("users", "ix_users_username", ["username"], unique=True)

    # menu_categories
    if not _table_exists("menu_categories"):
        op.create_table(
            "menu_categories",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("store_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=40), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        _create_index("menu_categories", "ix_menu_categories_store_id", ["store_id"])

    # orders
    if not _table_exists("orders"):
        op.create_table(
            "orders",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("order_no", sa.String(length=32), nullable=False),
            sa.Column("store_id", sa.Integer(), nullable=False),
            sa.Column("customer_name", sa.String(length=30), nullable=False),
            sa.Column("customer_phone", sa.String(length=20), nullable=False),
            sa.Column("remark", sa.String(length=200), nullable=True),
            sa.Column("entry_type", sa.String(length=16), nullable=False),
            sa.Column("item_count", sa.Integer(), nullable=False),
            sa.Column("total_cents", sa.Integer(), nullable=False),
            sa.Column("order_status", sa.String(length=16), nullable=False),
            sa.Column("payment_status", sa.String(length=16), nullable=False),
            sa.Column("cancel_reason", sa.String(length=32), nullable=True),
            sa.Column("cancel_by", sa.Integer(), nullable=True),
            sa.Column("idempotency_key", sa.String(length=64), nullable=True),
            sa.Column("source", sa.String(length=32), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("idempotency_key"),
        )
        _create_index("orders", "ix_orders_customer_phone", ["customer_phone"])
        _create_index("orders", "ix_orders_order_no", ["order_no"])
        _create_index("orders", "ix_orders_store_id", ["store_id"])
        _create_index("orders", "ix_orders_store_status_created", ["store_id", "order_status", "created_at"])

    # store_admins
    if not _table_exists("store_admins"):
        op.create_table(
            "store_admins",
            sa.Column("store_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("store_id", "user_id"),
        )

    # store_banners
    if not _table_exists("store_banners"):
        op.create_table(
            "store_banners",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("store_id", sa.Integer(), nullable=False),
            sa.Column("image_url", sa.String(length=500), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        _create_index("store_banners", "ix_store_banners_store_id", ["store_id"])

    # audit_logs
    if not _table_exists("audit_logs"):
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("order_id", sa.Integer(), nullable=False),
            sa.Column("store_id", sa.Integer(), nullable=False),
            sa.Column("actor_type", sa.String(length=16), nullable=False),
            sa.Column("actor_id", sa.Integer(), nullable=True),
            sa.Column("action", sa.String(length=32), nullable=False),
            sa.Column("detail", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
            sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        _create_index("audit_logs", "ix_audit_logs_order_id", ["order_id"])
        _create_index("audit_logs", "ix_audit_logs_store_created", ["store_id", "created_at"])

    # menu_items
    if not _table_exists("menu_items"):
        op.create_table(
            "menu_items",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("store_id", sa.Integer(), nullable=False),
            sa.Column("category_id", sa.Integer(), nullable=True),
            sa.Column("name", sa.String(length=60), nullable=False),
            sa.Column("description", sa.String(length=200), nullable=True),
            sa.Column("price_cents", sa.Integer(), nullable=False),
            sa.Column("spec_groups", sa.Text(), nullable=True),
            sa.Column("stock", sa.Integer(), nullable=True),
            sa.Column("image_url", sa.String(length=500), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["category_id"], ["menu_categories.id"]),
            sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        _create_index("menu_items", "ix_menu_items_is_active", ["is_active"])
        _create_index("menu_items", "ix_menu_items_store_id", ["store_id"])
    else:
        menu_cols = _columns("menu_items")
        if "spec_groups" not in menu_cols:
            op.add_column("menu_items", sa.Column("spec_groups", sa.Text(), nullable=True))
        _create_index("menu_items", "ix_menu_items_is_active", ["is_active"])
        _create_index("menu_items", "ix_menu_items_store_id", ["store_id"])

    # order_items
    if not _table_exists("order_items"):
        op.create_table(
            "order_items",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("order_id", sa.Integer(), nullable=False),
            sa.Column("menu_item_id", sa.Integer(), nullable=True),
            sa.Column("item_name", sa.String(length=60), nullable=False),
            sa.Column("category_name", sa.String(length=40), nullable=True),
            sa.Column("unit_price_cents", sa.Integer(), nullable=False),
            sa.Column("specs", sa.Text(), nullable=True),
            sa.Column("quantity", sa.Integer(), nullable=False),
            sa.Column("subtotal_cents", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["menu_item_id"], ["menu_items.id"]),
            sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        _create_index("order_items", "ix_order_items_order_id", ["order_id"])
    else:
        item_cols = _columns("order_items")
        if "specs" not in item_cols:
            op.add_column("order_items", sa.Column("specs", sa.Text(), nullable=True))
        if "category_name" not in item_cols:
            op.add_column("order_items", sa.Column("category_name", sa.String(length=40), nullable=True))
        _create_index("order_items", "ix_order_items_order_id", ["order_id"])


def downgrade() -> None:
    # 回滚仅对「全新库迁移」有意义；存量库回滚不适用，全部带存在性守卫。
    for table, index_name, columns in [
        ("order_items", "ix_order_items_order_id", ["order_id"]),
        ("menu_items", "ix_menu_items_store_id", ["store_id"]),
        ("menu_items", "ix_menu_items_is_active", ["is_active"]),
        ("audit_logs", "ix_audit_logs_store_created", ["store_id", "created_at"]),
        ("audit_logs", "ix_audit_logs_order_id", ["order_id"]),
        ("store_banners", "ix_store_banners_store_id", ["store_id"]),
        ("orders", "ix_orders_store_status_created", ["store_id", "order_status", "created_at"]),
        ("orders", "ix_orders_store_id", ["store_id"]),
        ("orders", "ix_orders_order_no", ["order_no"]),
        ("orders", "ix_orders_customer_phone", ["customer_phone"]),
        ("menu_categories", "ix_menu_categories_store_id", ["store_id"]),
        ("users", "ix_users_username", ["username"]),
        ("stores", "ix_stores_status", ["status"]),
    ]:
        if _index_exists(table, index_name):
            op.drop_index(index_name, table_name=table)

    for table in [
        "order_items",
        "menu_items",
        "audit_logs",
        "store_banners",
        "store_admins",
        "orders",
        "menu_categories",
        "users",
        "stores",
    ]:
        if _table_exists(table):
            op.drop_table(table)
