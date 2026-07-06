from app import create_app


# Fixture creating a Flask app backed by the real dataset, so tests exercise
# the endpoint against real data rather than a synthetic fixture.
def _client(real_dataset_path):
    app = create_app(dataset_path=real_dataset_path)
    return app.test_client()


# Missing query parameters should be rejected with a 400 and a clear message,
# not a 500 from a KeyError or an empty-looking 200.
def test_search_missing_params_returns_400(real_dataset_path):
    client = _client(real_dataset_path)

    response = client.get("/api/search?origin=JFK&destination=LAX")

    assert response.status_code == 400
    assert "required" in response.get_json()["error"]


# Airport codes must be exactly 3 letters; anything else is malformed input,
# not a legitimate "airport not found" case.
def test_search_malformed_airport_code_returns_400(real_dataset_path):
    client = _client(real_dataset_path)

    response = client.get("/api/search?origin=JF&destination=LAX&date=2024-03-15")

    assert response.status_code == 400
    assert "3-letter" in response.get_json()["error"]


# Dates must be ISO 8601 (YYYY-MM-DD); other formats should be rejected
# up front rather than causing a downstream parsing failure.
def test_search_malformed_date_returns_400(real_dataset_path):
    client = _client(real_dataset_path)

    response = client.get("/api/search?origin=JFK&destination=LAX&date=03/15/2024")

    assert response.status_code == 400
    assert "YYYY-MM-DD" in response.get_json()["error"]


# Required scenario 5: an airport code that is well-formed but doesn't exist
# in the loaded dataset should fail gracefully with a 400, not a 500 or a
# silently empty result set.
def test_search_unknown_airport_code_returns_400(real_dataset_path):
    client = _client(real_dataset_path)

    response = client.get("/api/search?origin=XXX&destination=LAX&date=2024-03-15")

    assert response.status_code == 400
    assert "unknown airport code" in response.get_json()["error"]


# Required scenario 4: searching an airport against itself is a malformed
# query, not a legitimate empty search, so it's rejected at the validation
# layer with a clear error rather than falling through to the search engine.
def test_search_same_origin_and_destination_returns_400(real_dataset_path):
    client = _client(real_dataset_path)

    response = client.get("/api/search?origin=JFK&destination=JFK&date=2024-03-15")

    assert response.status_code == 400
    assert "different airports" in response.get_json()["error"]


# Airport codes should be accepted case-insensitively, since callers
# shouldn't need to know the dataset stores them upper-case.
def test_search_accepts_lowercase_airport_codes(real_dataset_path):
    client = _client(real_dataset_path)

    response = client.get("/api/search?origin=jfk&destination=lax&date=2024-03-15")

    assert response.status_code == 200
    assert response.get_json()["origin"] == "JFK"


# Required scenario 1: a valid search should return a 200 with itineraries
# in the documented response shape, sorted shortest total duration first.
def test_search_jfk_to_lax_returns_itineraries_in_documented_shape(real_dataset_path):
    client = _client(real_dataset_path)

    response = client.get("/api/search?origin=JFK&destination=LAX&date=2024-03-15")

    assert response.status_code == 200
    body = response.get_json()

    assert body["origin"] == "JFK"
    assert body["destination"] == "LAX"
    assert body["date"] == "2024-03-15"
    assert body["count"] == len(body["itineraries"]) > 0

    durations = [itinerary["totalDurationMinutes"] for itinerary in body["itineraries"]]
    assert durations == sorted(durations)

    first_itinerary = body["itineraries"][0]
    assert set(first_itinerary) == {
        "id", "stops", "totalDurationMinutes", "totalPrice", "tripType", "segments", "layovers",
    }
    first_segment = first_itinerary["segments"][0]
    assert set(first_segment) == {
        "flightNumber", "airline", "origin", "destination",
        "departureTimeLocal", "arrivalTimeLocal", "price", "aircraft",
    }


# Required scenario 3: a route with no direct flight should still return a
# 200 with connecting itineraries, not an error.
def test_search_bos_to_sea_returns_only_connecting_itineraries(real_dataset_path):
    client = _client(real_dataset_path)

    response = client.get("/api/search?origin=BOS&destination=SEA&date=2024-03-15")

    assert response.status_code == 200
    body = response.get_json()
    assert body["count"] > 0
    assert all(itinerary["stops"] >= 1 for itinerary in body["itineraries"])


# A well-formed search that legitimately has no results (no flights on that
# date) should return a 200 with an empty list, not an error.
def test_search_with_no_matching_flights_returns_200_with_empty_list(real_dataset_path):
    client = _client(real_dataset_path)

    response = client.get("/api/search?origin=JFK&destination=LAX&date=2030-01-01")

    assert response.status_code == 200
    assert response.get_json() == {
        "origin": "JFK", "destination": "LAX", "date": "2030-01-01",
        "count": 0, "itineraries": [],
    }
