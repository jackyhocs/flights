SECONDS_PER_MINUTE = 60

MAX_STOPS = 2
MAX_SEGMENTS = MAX_STOPS + 1

MIN_DOMESTIC_LAYOVER_MINUTES = 45
MIN_INTERNATIONAL_LAYOVER_MINUTES = 90
MAX_LAYOVER_MINUTES = 6 * 60

REQUIRED_FLIGHT_FIELDS = [
    "flightNumber", "airline", "origin", "destination",
    "departureTime", "arrivalTime", "price", "aircraft",
]
