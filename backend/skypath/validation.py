import re
from datetime import datetime

from skypath.constants import DATE_FORMAT

# Currently a regex but can be a list that is alive in some
# configuration file or repo depending on computation/lookup costs
AIRPORT_CODE_PATTERN = re.compile(r"^[A-Z]{3}$")


# Helper to validate incoming request payload
def validate_search_params(
    origin: str,
    destination: str,
    date_param: str,
    known_airports: dict,
) -> str | None:
    if not origin or not destination or not date_param:
        return "origin, destination, and date are required"

    if not AIRPORT_CODE_PATTERN.match(origin) or not AIRPORT_CODE_PATTERN.match(destination):
        return "origin and destination must be 3-letter IATA airport codes"

    try:
        datetime.strptime(date_param, DATE_FORMAT)
    except ValueError:
        return "date must be in YYYY-MM-DD format"

    if origin not in known_airports:
        return f"unknown airport code: {origin}"
    if destination not in known_airports:
        return f"unknown airport code: {destination}"

    if origin == destination:
        return "origin and destination must be different airports"

    return None
