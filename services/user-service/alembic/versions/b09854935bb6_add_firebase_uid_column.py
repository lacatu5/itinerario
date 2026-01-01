"""add_firebase_uid_column

Revision ID: b09854935bb6
Revises: 40e96878ced8
Create Date: 2025-12-28 13:57:18.638474

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "b09854935bb6"
down_revision: str | None = "40e96878ced8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("firebase_uid", sa.String(255), nullable=True))
    op.create_unique_constraint("uq_users_firebase_uid", "users", ["firebase_uid"])
    op.create_index("ix_users_firebase_uid", "users", ["firebase_uid"])


def downgrade() -> None:
    op.drop_index("ix_users_firebase_uid", table_name="users")
    op.drop_constraint("uq_users_firebase_uid", "users", type_="unique")
    op.drop_column("users", "firebase_uid")
