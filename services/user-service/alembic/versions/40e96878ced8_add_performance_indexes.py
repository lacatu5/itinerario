"""add performance indexes

Revision ID: 40e96878ced8
Create Date: 2025-12-27 00:41:36.677547

"""

from collections.abc import Sequence

from alembic import op

revision: str = "40e96878ced8"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index("idx_users_name_username", "users", ["name", "username"], unique=False)
    op.create_index(op.f("ix_users_created_at"), "users", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_created_at"), table_name="users")
    op.drop_index("idx_users_name_username", table_name="users")
