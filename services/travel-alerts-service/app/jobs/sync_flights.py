from datetime import datetime, timedelta, timezone

from google.cloud import firestore
from loguru import logger

from app.jobs.flight_api_client import (
    fetch_flight_info_from_api,
    fetch_flight_status_aviationstack,
)
from app.jobs.flight_data_processor import generate_mock_flight_update
from app.models import TrackedFlight
from core.config import api_settings, config, feature_flags
from core.firestore.client import get_firestore_client


def fetch_flight_status(
    flight_number: str, existing_data: dict[str, object] | None = None
) -> dict[str, object]:
    use_live = (
        config.is_prod and api_settings.AVIATIONSTACK_API_KEY and not feature_flags.ENABLE_MOCK_DATA
    )

    if use_live:
        result = fetch_flight_status_aviationstack(flight_number)
        if result:
            return result
        logger.info(f"Falling back to mock data for {flight_number}")

    if existing_data:
        return generate_mock_flight_update(existing_data)

    return {}


def get_flights_to_update(db: firestore.Client) -> list[dict[str, object]]:
    now = datetime.now(timezone.utc)
    past_24h = now - timedelta(hours=24)
    future_48h = now + timedelta(hours=48)

    flights = []

    try:
        results = TrackedFlight.collection.fetch()

        for flight in results:
            dep = flight.scheduled_departure
            if not dep:
                continue

            if hasattr(dep, "timestamp"):
                dep_dt = dep
            elif isinstance(dep, str):
                try:
                    dep_dt = datetime.fromisoformat(dep.replace("Z", "+00:00"))
                except ValueError:
                    continue
            else:
                continue

            if dep_dt.tzinfo is None:
                dep_dt = dep_dt.replace(tzinfo=timezone.utc)

            if past_24h <= dep_dt <= future_48h:
                status = flight.status if hasattr(flight, "status") else "scheduled"
                if status == "landed":
                    if dep_dt < now - timedelta(hours=2):
                        continue

                flights.append(
                    {
                        "id": flight.id,
                        "flight_number": flight.flight_number,
                        "scheduled_departure": flight.scheduled_departure,
                        "status": flight.status if hasattr(flight, "status") else "scheduled",
                        "delay_minutes": flight.delay_minutes
                        if hasattr(flight, "delay_minutes")
                        else None,
                    }
                )

        logger.info(f"Found {len(flights)} flights to update")
        return flights

    except Exception as e:
        logger.error(f"Error fetching flights to update: {e}")
        return []


def update_flight_alert(
    db: firestore.Client, flight_id: str, update_data: dict[str, object]
) -> bool:
    try:
        flight = TrackedFlight.collection.get(flight_id)
        if not flight:
            logger.error(f"Flight {flight_id} not found")
            return False

        if "status" in update_data and update_data["status"] is not None:
            flight.status = update_data["status"]
        if "delay_minutes" in update_data and update_data["delay_minutes"] is not None:
            flight.delay_minutes = update_data["delay_minutes"]
        if "gate" in update_data and update_data["gate"] is not None:
            flight.gate = update_data["gate"]
        if "terminal" in update_data and update_data["terminal"] is not None:
            flight.terminal = update_data["terminal"]
        if "actual_departure" in update_data and update_data["actual_departure"] is not None:
            flight.actual_departure = update_data["actual_departure"]
        if "actual_arrival" in update_data and update_data["actual_arrival"] is not None:
            flight.actual_arrival = update_data["actual_arrival"]
        if "alert_type" in update_data and update_data["alert_type"] is not None:
            flight.alert_type = update_data["alert_type"]
        if "alert_message" in update_data and update_data["alert_message"] is not None:
            flight.alert_message = update_data["alert_message"]

        flight.updated_at = datetime.now(timezone.utc)
        flight.save()

        return True

    except Exception as e:
        logger.error(f"Error updating flight {flight_id}: {e}")
        return False


def sync_flights():
    logger.info("=" * 60)
    logger.info("Starting flight status sync...")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"API Key configured: {'Yes' if api_settings.AVIATIONSTACK_API_KEY else 'No'}")
    logger.info(f"Mock data: {'Enabled' if feature_flags.ENABLE_MOCK_DATA else 'Disabled'}")
    logger.info("=" * 60)

    try:
        db = get_firestore_client()
    except Exception as e:
        logger.error(f"Failed to initialize Firestore: {e}")
        return {"success": False, "error": str(e)}

    flights = get_flights_to_update(db)

    if not flights:
        logger.info("No flights to update")
        return {"success": True, "updated": 0, "skipped": 0, "errors": 0}

    updated = 0
    skipped = 0
    errors = 0

    for flight in flights:
        flight_number = flight.get("flight_number", "")
        flight_id = flight.get("id", "")

        if not flight_number or not flight_id:
            skipped += 1
            continue

        logger.info(f"Processing flight: {flight_number}")

        update_data = fetch_flight_status(flight_number, flight)

        if not update_data or not update_data.get("status"):
            logger.warning(f"No update data for {flight_number}")
            skipped += 1
            continue

        current_status = flight.get("status")
        new_status = update_data.get("status")
        current_delay = flight.get("delay_minutes")
        new_delay = update_data.get("delay_minutes")

        if current_status == new_status and current_delay == new_delay:
            logger.info(f"No changes for {flight_number}")
            skipped += 1
            continue

        if update_flight_alert(db, flight_id, update_data):
            logger.info(f"Updated {flight_number}: {current_status} -> {new_status}")
            if update_data.get("alert_message"):
                logger.info(f"  Alert: {update_data['alert_message']}")
            updated += 1
        else:
            errors += 1

    result = {
        "success": True,
        "total_processed": len(flights),
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
    }

    logger.info("=" * 60)
    logger.info(f"Sync completed: {result}")
    logger.info("=" * 60)

    return result


if __name__ == "__main__":
    result = sync_flights()
    print(result)


__all__ = [
    "sync_flights",
    "fetch_flight_status",
    "fetch_flight_info_from_api",
]
