from datetime import date, datetime

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base


class Itinerary(Base):
    __tablename__ = "itineraries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    destination: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    start_date: Mapped[date] = mapped_column(index=True, nullable=False)
    end_date: Mapped[date | None] = mapped_column(nullable=True, index=True)
    short_description: Mapped[str] = mapped_column(String(80), nullable=False)
    detail_description: Mapped[str] = mapped_column(String(5000), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    latitude: Mapped[str | None] = mapped_column(String(50), nullable=True)
    longitude: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    locations: Mapped[list["Location"]] = relationship(back_populates="itinerary")
    transports: Mapped[list["Transport"]] = relationship(back_populates="itinerary")

    __table_args__ = (
        Index("idx_itineraries_owner_created", "owner_id", "created_at"),
        Index("idx_itineraries_date_range", "start_date", "end_date"),
    )


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_description: Mapped[str] = mapped_column(String(500), nullable=False)
    from_date: Mapped[date] = mapped_column(index=True, nullable=False)
    to_date: Mapped[date] = mapped_column(index=True, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    latitude: Mapped[str | None] = mapped_column(String(50), nullable=True)
    longitude: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    itinerary_id: Mapped[int] = mapped_column(
        ForeignKey("itineraries.id"), index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    itinerary: Mapped["Itinerary"] = relationship(back_populates="locations")

    __table_args__ = (Index("idx_locations_itinerary_date", "itinerary_id", "from_date"),)


class Transport(Base):
    __tablename__ = "transports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    departure_location: Mapped[str] = mapped_column(String(200), nullable=False)
    arrival_location: Mapped[str] = mapped_column(String(200), nullable=False)
    departure_time: Mapped[datetime] = mapped_column(index=True, nullable=False)
    arrival_time: Mapped[datetime] = mapped_column(index=True, nullable=False)
    carrier: Mapped[str | None] = mapped_column(String(100), nullable=True)
    transport_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    itinerary_id: Mapped[int] = mapped_column(
        ForeignKey("itineraries.id"), index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    itinerary: Mapped["Itinerary"] = relationship(back_populates="transports")

    __table_args__ = (Index("idx_transports_itinerary_time", "itinerary_id", "departure_time"),)
