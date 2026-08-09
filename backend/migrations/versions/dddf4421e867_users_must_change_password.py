"""users.must_change_password (seed hardening)

Revision ID: dddf4421e867
Revises: 09b7215bc9ed
Create Date: 2026-08-09 12:03:32.062594
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dddf4421e867'
down_revision: Union[str, None] = '09b7215bc9ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    cols = {col["name"] for col in sa.inspect(bind).get_columns("users")}
    if "must_change_password" not in cols:
        op.add_column(
            "users",
            sa.Column("must_change_password", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        )


def downgrade() -> None:
    bind = op.get_bind()
    cols = {col["name"] for col in sa.inspect(bind).get_columns("users")}
    if "must_change_password" in cols:
        op.drop_column("users", "must_change_password")
