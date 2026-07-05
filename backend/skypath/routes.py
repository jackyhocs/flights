from datetime import datetime

from flask import Blueprint, current_app, jsonify, request

from skypath.constants import DATE_FORMAT
from skypath.search import search_itineraries
from skypath.serialization import serialize_response
from skypath.validation import validate_search_params

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/search")
def search():
    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    date_param = request.args.get("date", "")

    known_airports = current_app.config["AIRPORTS"]
    error = validate_search_params(origin, destination, date_param, known_airports)
    if error is not None:
        return jsonify({"error": error}), 400

    search_date = datetime.strptime(date_param, DATE_FORMAT).date()
    graph = current_app.config["FLIGHT_GRAPH"]
    itineraries = search_itineraries(graph, origin, destination, search_date)

    return jsonify(serialize_response(origin, destination, date_param, itineraries))
