"""add performance indexes

Revision ID: 9b0387e6f728
Create Date: 2025-12-27 00:43:15.103176

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "9b0387e6f728"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "itineraries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("destination", sa.String(length=200), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("short_description", sa.String(length=80), nullable=False),
        sa.Column("detail_description", sa.String(length=5000), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("latitude", sa.String(length=50), nullable=True),
        sa.Column("longitude", sa.String(length=50), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_itineraries_date_range", "itineraries", ["start_date", "end_date"], unique=False
    )
    op.create_index(
        "idx_itineraries_owner_created", "itineraries", ["owner_id", "created_at"], unique=False
    )
    op.create_index(op.f("ix_itineraries_created_at"), "itineraries", ["created_at"], unique=False)
    op.create_index(
        op.f("ix_itineraries_destination"), "itineraries", ["destination"], unique=False
    )
    op.create_index(op.f("ix_itineraries_end_date"), "itineraries", ["end_date"], unique=False)
    op.create_index(op.f("ix_itineraries_owner_id"), "itineraries", ["owner_id"], unique=False)
    op.create_index(op.f("ix_itineraries_start_date"), "itineraries", ["start_date"], unique=False)
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("short_description", sa.String(length=500), nullable=False),
        sa.Column("from_date", sa.Date(), nullable=False),
        sa.Column("to_date", sa.Date(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("latitude", sa.String(length=50), nullable=True),
        sa.Column("longitude", sa.String(length=50), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("itinerary_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["itinerary_id"],
            ["itineraries.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_locations_itinerary_date", "locations", ["itinerary_id", "from_date"], unique=False
    )
    op.create_index(op.f("ix_locations_from_date"), "locations", ["from_date"], unique=False)
    op.create_index(op.f("ix_locations_itinerary_id"), "locations", ["itinerary_id"], unique=False)
    op.create_index(op.f("ix_locations_to_date"), "locations", ["to_date"], unique=False)
    op.create_table(
        "transports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("departure_location", sa.String(length=200), nullable=False),
        sa.Column("arrival_location", sa.String(length=200), nullable=False),
        sa.Column("departure_time", sa.DateTime(), nullable=False),
        sa.Column("arrival_time", sa.DateTime(), nullable=False),
        sa.Column("carrier", sa.String(length=100), nullable=True),
        sa.Column("transport_number", sa.String(length=50), nullable=True),
        sa.Column("itinerary_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["itinerary_id"],
            ["itineraries.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_transports_itinerary_time",
        "transports",
        ["itinerary_id", "departure_time"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transports_arrival_time"), "transports", ["arrival_time"], unique=False
    )
    op.create_index(
        op.f("ix_transports_departure_time"), "transports", ["departure_time"], unique=False
    )
    op.create_index(
        op.f("ix_transports_itinerary_id"), "transports", ["itinerary_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_transports_itinerary_id"), table_name="transports")
    op.drop_index(op.f("ix_transports_departure_time"), table_name="transports")
    op.drop_index(op.f("ix_transports_arrival_time"), table_name="transports")
    op.drop_index("idx_transports_itinerary_time", table_name="transports")
    op.drop_table("transports")
    op.drop_index(op.f("ix_locations_to_date"), table_name="locations")
    op.drop_index(op.f("ix_locations_itinerary_id"), table_name="locations")
    op.drop_index(op.f("ix_locations_from_date"), table_name="locations")
    op.drop_index("idx_locations_itinerary_date", table_name="locations")
    op.drop_table("locations")
    op.drop_index(op.f("ix_itineraries_start_date"), table_name="itineraries")
    op.drop_index(op.f("ix_itineraries_owner_id"), table_name="itineraries")
    op.drop_index(op.f("ix_itineraries_end_date"), table_name="itineraries")
    op.drop_index(op.f("ix_itineraries_destination"), table_name="itineraries")
    op.drop_index(op.f("ix_itineraries_created_at"), table_name="itineraries")
    op.drop_index("idx_itineraries_owner_created", table_name="itineraries")
    op.drop_index("idx_itineraries_date_range", table_name="itineraries")
    op.drop_table("itineraries")
