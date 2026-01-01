import httpx
import pycountry
from google.cloud import firestore
from loguru import logger

from app.jobs.fcdo_scraper import parse_fcdo_feed
from core.firestore.client import get_firestore_client

FCDO_FEED_URL = "https://www.gov.uk/foreign-travel-advice.atom"


def get_country_code(country_name: str) -> str:
    clean_name = country_name.strip()

    try:
        country = pycountry.countries.get(name=clean_name)
        if country:
            return country.alpha_2
    except KeyError:
        pass

    for country in pycountry.countries:
        if clean_name.lower() == country.name.lower():
            return country.alpha_2

        if clean_name.lower() in country.name.lower() or country.name.lower() in clean_name.lower():
            return country.alpha_2

    return "XX"


def delete_all_warnings(db) -> int:
    logger.info("Deleting all existing travel warnings...")
    deleted_count = 0

    try:
        docs = db.collection("travel_warnings").stream()

        batch = db.batch()
        batch_count = 0

        for doc in docs:
            batch.delete(doc.reference)
            batch_count += 1
            deleted_count += 1

            if batch_count >= 500:
                batch.commit()
                batch = db.batch()
                batch_count = 0
                logger.info(f"Deleted batch of 500 warnings, total so far: {deleted_count}")

        if batch_count > 0:
            batch.commit()

        logger.info(f"Successfully deleted {deleted_count} existing warnings")
        return deleted_count

    except Exception as e:
        logger.error(f"Error deleting warnings: {e}")
        raise


def sync_warnings():
    logger.info("Starting FCDO travel warnings sync...")

    try:
        response = httpx.get(FCDO_FEED_URL, timeout=30.0)
        response.raise_for_status()
        xml_content = response.text
        logger.info(f"Fetched FCDO feed: {len(xml_content)} bytes")
    except Exception as e:
        logger.error(f"Failed to fetch FCDO feed: {e}")
        return {"success": False, "error": str(e)}

    warnings = parse_fcdo_feed(xml_content, get_country_code)
    logger.info(f"Parsed {len(warnings)} warnings from feed")

    try:
        db = get_firestore_client()
    except Exception as e:
        logger.error(f"Failed to initialize Firestore: {e}")
        return {"success": False, "error": str(e)}

    try:
        deleted_count = delete_all_warnings(db)
    except Exception as e:
        logger.error(f"Failed to delete existing warnings: {e}")
        return {
            "success": False,
            "error": f"Failed to delete existing warnings: {str(e)}",
        }

    created = 0

    for warning in warnings:
        try:
            db.collection("travel_warnings").add(
                {
                    "country_code": warning["country_code"],
                    "country_name": warning["country_name"],
                    "title": warning["title"],
                    "description": warning["description"],
                    "severity": warning["severity"],
                    "category": warning["category"],
                    "source": warning["source"],
                    "source_url": warning["source_url"],
                    "active": True,
                    "created_at": firestore.SERVER_TIMESTAMP,
                    "updated_at": firestore.SERVER_TIMESTAMP,
                }
            )
            created += 1

        except Exception as e:
            logger.error(f"Error processing warning for {warning.get('country_name')}: {e}")
            continue

    result = {
        "success": True,
        "deleted": deleted_count,
        "created": created,
        "total_processed": len(warnings),
    }
    logger.info(f"Sync completed: {result}")
    return result


if __name__ == "__main__":
    result = sync_warnings()
    print(result)
