# Helper functions for serialization

def serialize_response(origin, destination, date_param, itineraries) -> dict:
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
