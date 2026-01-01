import time
import xml.etree.ElementTree as ET

import httpx
from bs4 import BeautifulSoup
from loguru import logger


def fetch_page_content(url: str) -> str:
    try:
        response = httpx.get(url, timeout=15.0, follow_redirects=True)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.warning(f"Failed to fetch page content from {url}: {e}")
        return ""


def determine_severity_from_html(html_content: str) -> str:
    if not html_content:
        return "low"

    content_lower = html_content.lower()

    if (
        "advises against all travel" in content_lower
        or "advise against all travel" in content_lower
        or "do not travel" in content_lower
        or "evacuate" in content_lower
    ):
        return "critical"

    if (
        "advises against all but essential travel" in content_lower
        or "advise against all but essential travel" in content_lower
        or "essential travel only" in content_lower
    ):
        return "high"

    if (
        "exercise caution" in content_lower
        or "be vigilant" in content_lower
        or "increased risk" in content_lower
        or "high risk" in content_lower
    ):
        return "medium"

    return "low"


def determine_severity(summary: str, html_content: str = "") -> str:
    if html_content:
        return determine_severity_from_html(html_content)

    summary_lower = summary.lower()
    if any(
        word in summary_lower for word in ["advise against all travel", "do not travel", "evacuate"]
    ):
        return "critical"
    if any(
        word in summary_lower
        for word in ["advise against all but essential", "high risk", "serious"]
    ):
        return "high"
    if any(word in summary_lower for word in ["exercise caution", "be vigilant", "increased risk"]):
        return "medium"
    return "low"


def determine_category(summary: str, html_content: str = "") -> str:
    content_to_check = f"{summary} {html_content}".lower()

    if any(word in content_to_check for word in ["terrorism", "terrorist", "attack"]):
        return "terrorism"
    if any(word in content_to_check for word in ["political", "protest", "unrest", "civil"]):
        return "political_unrest"
    if any(
        word in content_to_check
        for word in [
            "natural disaster",
            "earthquake",
            "hurricane",
            "flood",
            "volcano",
            "cyclone",
        ]
    ):
        return "natural_disaster"
    if any(
        word in content_to_check
        for word in ["health", "disease", "outbreak", "epidemic", "pandemic"]
    ):
        return "health"
    if any(word in content_to_check for word in ["crime", "robbery", "theft", "kidnapping"]):
        return "crime"
    if any(word in content_to_check for word in ["war", "conflict", "military"]):
        return "conflict"
    return "general"


def parse_fcdo_feed(xml_content: str, get_country_code_func) -> list:
    warnings = []

    root = ET.fromstring(xml_content)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    entries = root.findall("atom:entry", ns)

    for entry in entries:
        try:
            title_elem = entry.find("atom:title", ns)
            title = title_elem.text if title_elem is not None else "Unknown"

            summary_elem = entry.find("atom:summary", ns)
            summary = summary_elem.text if summary_elem is not None else ""

            link_elem = entry.find("atom:link", ns)
            link = link_elem.get("href", "") if link_elem is not None else ""

            updated_elem = entry.find("atom:updated", ns)
            updated = updated_elem.text if updated_elem is not None else None

            country_name = title.replace(" travel advice", "").replace(" - ", " ").strip()
            country_code = get_country_code_func(country_name)

            html_content = ""
            if link:
                logger.info(f"Fetching detailed advice for {country_name} from {link}")
                html_content = fetch_page_content(link)
                if html_content:
                    logger.info(f"Successfully fetched HTML for {country_name}")
                else:
                    logger.warning(f"Failed to fetch HTML for {country_name}, using summary only")
                time.sleep(0.5)

            severity = determine_severity(summary or title, html_content)
            category = determine_category(summary or title, html_content)
            logger.info(f"{country_name}: severity={severity}, category={category}")

            description = (
                summary[:500]
                if summary
                else f"Travel advisory for {country_name}. Check official FCDO page for details."
            )
            if html_content:
                soup = BeautifulSoup(html_content, "html.parser")

                warning_section = soup.find("h2", id="areas-where-fcdo-advises-against-travel-")
                if warning_section:
                    content = []
                    next_elem = warning_section.next_sibling
                    while next_elem and not (next_elem.name and next_elem.name.startswith("h")):
                        if hasattr(next_elem, "get_text"):
                            text = next_elem.get_text(strip=True)
                            if text:
                                content.append(text)
                        next_elem = next_elem.next_sibling

                    if content:
                        description = " ".join(content)[:500]

            warnings.append(
                {
                    "country_code": country_code,
                    "country_name": country_name,
                    "title": f"UK FCDO Advisory: {country_name}",
                    "description": description,
                    "severity": severity,
                    "category": category,
                    "source": "UK Foreign, Commonwealth & Development Office",
                    "source_url": link,
                    "updated_at_source": updated,
                }
            )
        except Exception as e:
            logger.error(
                f"Error parsing entry for {title if 'title' in locals() else 'unknown'}: {e}"
            )
            continue

    return warnings
