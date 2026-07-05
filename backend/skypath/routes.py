import re
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request

from skypath.search import search_itineraries

AIRPORT_CODE_PATTERN = re.compile(r"^[A-Z]{3}$")
DATE_FORMAT = "%Y-%m-%d"

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/search")
def search():
    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    date_param = request.args.get("date", "")

    error = _validate_search_params(origin, destination, date_param)
    if error is not None:
        return jsonify({"error": error}), 400

    search_date = datetime.strptime(date_param, DATE_FORMAT).date()
    graph = current_app.config["FLIGHT_GRAPH"]
    itineraries = search_itineraries(graph, origin, destination, search_date)

    return jsonify(_serialize_response(origin, destination, date_param, itineraries))


# Helper to validate the input parameters from the endpoint
def _validate_search_params(origin: str, destination: str, date_param: str) -> str | None:
    if not origin or not destination or not date_param:
        return "origin, destination, and date are required"

    if not AIRPORT_CODE_PATTERN.match(origin) or not AIRPORT_CODE_PATTERN.match(destination):
        return "origin and destination must be 3-letter IATA airport codes"

    try:
        datetime.strptime(date_param, DATE_FORMAT)
    except ValueError:
        return "date must be in YYYY-MM-DD format"

    known_airports = current_app.config["AIRPORTS"]
    if origin not in known_airports:
        return f"unknown airport code: {origin}"
    if destination not in known_airports:
        return f"unknown airport code: {destination}"

    if origin == destination:
        return "origin and destination must be different airports"

    return None


def _serialize_response(origin, destination, date_param, itineraries) -> dict:
    return {
        "origin": origin,
        "destination": destination,
        "date": date_param,
        "count": len(itineraries),
        "itineraries": [_serialize_itinerary(itinerary) for itinerary in itineraries],
    }


def _serialize_itinerary(itinerary) -> dict:
    return {
        "id": "-".join(segment.flight_number for segment in itinerary.segments),
        "stops": itinerary.stops,
        "totalDurationMinutes": itinerary.total_duration_minutes,
        "totalPrice": itinerary.total_price,
        "segments": [_serialize_segment(segment) for segment in itinerary.segments],
        "layovers": [_serialize_layover(layover) for layover in itinerary.layovers],
    }


def _serialize_segment(segment) -> dict:
    return {
        "flightNumber": segment.flight_number,
        "airline": segment.airline,
        "origin": segment.origin,
        "destination": segment.destination,
        "departureTimeLocal": segment.departure_local.isoformat(),
        "arrivalTimeLocal": segment.arrival_local.isoformat(),
        "price": segment.price,
        "aircraft": segment.aircraft,
    }


def _serialize_layover(layover) -> dict:
    return {
        "airport": layover.airport,
        "durationMinutes": layover.duration_minutes,
        "type": "domestic" if layover.is_domestic else "international",
    }
