import httpx
from loguru import logger

from app.utils.airline_codes import AIRLINE_NAMES
from app.utils.constants import STATUS_MAPPING
from core.config import api_settings


def get_airline_name(flight_number: str) -> str:
    if len(flight_number) >= 2:
        code = flight_number[:2].upper()
        return AIRLINE_NAMES.get(code, code)
    return ""


def fetch_flight_status_aviationstack(flight_number: str) -> dict[str, object] | None:
    if not api_settings.AVIATIONSTACK_API_KEY:
        logger.warning("AviationStack API key not configured")
        return None

    try:
        clean_flight = flight_number.replace(" ", "").upper()

        response = httpx.get(
            f"{api_settings.AVIATIONSTACK_BASE_URL}/flights",
            params={
                "access_key": api_settings.AVIATIONSTACK_API_KEY,
                "flight_iata": clean_flight,
            },
            timeout=api_settings.AVIATIONSTACK_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("error"):
            logger.error(f"AviationStack error: {data['error']}")
            return None

        flights = data.get("data", [])
        if not flights:
            logger.info(f"No flight data found for {flight_number}")
            return None

        flight = flights[0]

        departure = flight.get("departure", {})
        arrival = flight.get("arrival", {})

        delay_minutes = None
        if departure.get("delay"):
            delay_minutes = int(departure["delay"])

        raw_status = flight.get("flight_status", "unknown")
        status = STATUS_MAPPING.get(raw_status, "scheduled")

        if delay_minutes and delay_minutes > 15 and status == "scheduled":
            status = "delayed"

        alert_type = None
        alert_message = None

        if status == "cancelled":
            alert_type = "cancellation"
            alert_message = "Flight has been cancelled"
        elif status == "diverted":
            alert_type = "diversion"
            divert_airport = arrival.get("iata", "unknown")
            alert_message = f"Flight diverted to {divert_airport}"
        elif delay_minutes and delay_minutes > 15:
            alert_type = "delay"
            if delay_minutes >= 120:
                alert_message = f"SIGNIFICANT DELAY: {delay_minutes} minutes"
            else:
                alert_message = f"Flight delayed by {delay_minutes} minutes"
        elif status == "landed":
            alert_type = "arrival"
            alert_message = "Flight has landed"

        return {
            "status": status,
            "delay_minutes": delay_minutes,
            "gate": departure.get("gate"),
            "terminal": departure.get("terminal"),
            "actual_departure": departure.get("actual"),
            "actual_arrival": arrival.get("actual"),
            "alert_type": alert_type,
            "alert_message": alert_message,
            "raw_data": flight,
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching flight {flight_number}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching flight {flight_number}: {e}")
        return None


def fetch_flight_info_from_api(flight_number: str) -> dict[str, object] | None:
    if not api_settings.AVIATIONSTACK_API_KEY:
        logger.warning("AviationStack API key not configured")
        return None

    try:
        clean_flight = flight_number.replace(" ", "").upper()

        response = httpx.get(
            f"{api_settings.AVIATIONSTACK_BASE_URL}/flights",
            params={
                "access_key": api_settings.AVIATIONSTACK_API_KEY,
                "flight_iata": clean_flight,
            },
            timeout=api_settings.AVIATIONSTACK_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("error"):
            logger.error(f"AviationStack error: {data['error']}")
            return None

        flights = data.get("data", [])
        if not flights:
            logger.info(f"No flight data found for {flight_number}")
            return None

        flight = flights[0]

        departure = flight.get("departure", {})
        arrival = flight.get("arrival", {})
        airline_data = flight.get("airline", {})

        airline_iata = airline_data.get("iata", "")
        airline_name = airline_data.get("name") or AIRLINE_NAMES.get(airline_iata, airline_iata)

        raw_status = flight.get("flight_status", "scheduled")
        status = STATUS_MAPPING.get(raw_status, "scheduled")

        delay_minutes = None
        if departure.get("delay"):
            delay_minutes = int(departure["delay"])
            if delay_minutes > 15 and status == "scheduled":
                status = "delayed"

        return {
            "flight_number": clean_flight,
            "airline": airline_name,
            "departure_airport": f"{departure.get('airport', '')} ({departure.get('iata', '')})",
            "departure_airport_iata": departure.get("iata", ""),
            "arrival_airport": f"{arrival.get('airport', '')} ({arrival.get('iata', '')})",
            "arrival_airport_iata": arrival.get("iata", ""),
            "scheduled_departure": departure.get("scheduled"),
            "scheduled_arrival": arrival.get("scheduled"),
            "actual_departure": departure.get("actual"),
            "actual_arrival": arrival.get("actual"),
            "status": status,
            "delay_minutes": delay_minutes,
            "gate": departure.get("gate"),
            "terminal": departure.get("terminal"),
            "flight_date": flight.get("flight_date"),
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching flight {flight_number}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching flight {flight_number}: {e}")
        return None
