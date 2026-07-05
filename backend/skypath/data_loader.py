import json
import logging
from datetime import datetime
from os import PathLike

from skypath.constants import REQUIRED_FLIGHT_FIELDS
from skypath.models import Airport, Flight
from skypath.time_utils import to_utc

logger = logging.getLogger(__name__)


def load_dataset(path: str | PathLike) -> tuple[dict[str, Airport], list[Flight]]:
    with open(path) as f:
        raw = json.load(f)

    airports = {a["code"]: Airport(**a) for a in raw["airports"]}

    flights = []
    seen_flight_numbers = set()
    for index, raw_flight in enumerate(raw["flights"]):
        flight_number = raw_flight.get("flightNumber")
        if flight_number is not None and flight_number in seen_flight_numbers:
            logger.warning("skipping %s: duplicate flight number", flight_number)
            continue

        flight = _parse_flight(raw_flight, airports, index)
        if flight is not None:
            seen_flight_numbers.add(flight.flight_number)
            flights.append(flight)

    return airports, flights


def _parse_flight(raw_flight: dict, airports: dict[str, Airport], index: int) -> Flight | None:
    identifier = raw_flight.get("flightNumber") or f"<flight at index {index}>"

    missing_fields = [field for field in REQUIRED_FLIGHT_FIELDS if field not in raw_flight]
    if missing_fields:
        logger.warning("skipping %s: missing required field(s) %s", identifier, missing_fields)
        return None

    flight_number = raw_flight["flightNumber"]
    origin = airports.get(raw_flight["origin"])
    destination = airports.get(raw_flight["destination"])
    if origin is None or destination is None:
        logger.warning(
            "skipping %s: unknown airport code (origin=%s, destination=%s)",
            flight_number, raw_flight["origin"], raw_flight["destination"],
        )
        return None

    try:
        price = float(raw_flight["price"])
    except (TypeError, ValueError):
        logger.warning("skipping %s: invalid price %r", flight_number, raw_flight["price"])
        return None

    try:
        departure_local = datetime.fromisoformat(raw_flight["departureTime"])
        arrival_local = datetime.fromisoformat(raw_flight["arrivalTime"])
        departure_utc = to_utc(raw_flight["departureTime"], origin.timezone)
        arrival_utc = to_utc(raw_flight["arrivalTime"], destination.timezone)
    except ValueError:
        logger.warning(
            "skipping %s: unparseable date (departure=%r, arrival=%r)",
            flight_number, raw_flight["departureTime"], raw_flight["arrivalTime"],
        )
        return None

    if arrival_utc <= departure_utc:
        logger.warning(
            "skipping %s: arrival (%s) is not after departure (%s)",
            flight_number, arrival_utc, departure_utc,
        )
        return None

    return Flight(
        flight_number=flight_number,
        airline=raw_flight["airline"],
        origin=origin.code,
        destination=destination.code,
        origin_country=origin.country,
        destination_country=destination.country,
        departure_local=departure_local,
        arrival_local=arrival_local,
        departure_utc=departure_utc,
        arrival_utc=arrival_utc,
        price=price,
        aircraft=raw_flight["aircraft"],
    )
