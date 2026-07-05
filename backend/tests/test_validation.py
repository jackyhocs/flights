from skypath.validation import validate_search_params

KNOWN_AIRPORTS = {"JFK": object(), "LAX": object()}


# A well-formed, complete search against known airports should pass
# validation with no error.
def test_validate_search_params_returns_none_for_valid_input():
    error = validate_search_params("JFK", "LAX", "2024-03-15", KNOWN_AIRPORTS)

    assert error is None


# Any missing parameter should be caught before more specific checks run.
def test_validate_search_params_rejects_missing_fields():
    assert validate_search_params("", "LAX", "2024-03-15", KNOWN_AIRPORTS) is not None
    assert validate_search_params("JFK", "", "2024-03-15", KNOWN_AIRPORTS) is not None
    assert validate_search_params("JFK", "LAX", "", KNOWN_AIRPORTS) is not None


# Airport codes must be exactly 3 letters, so anything else is malformed
# input rather than a legitimate "airport not found" case.
def test_validate_search_params_rejects_malformed_airport_codes():
    error = validate_search_params("JF", "LAX", "2024-03-15", KNOWN_AIRPORTS)

    assert "3-letter" in error


# Dates must be ISO 8601 (YYYY-MM-DD); anything else should be rejected
# up front rather than failing later during parsing.
def test_validate_search_params_rejects_malformed_dates():
    error = validate_search_params("JFK", "LAX", "03/15/2024", KNOWN_AIRPORTS)

    assert "YYYY-MM-DD" in error


# An airport code that is well-formed but not present in the known airports
# should be rejected with a message identifying which code was unknown.
def test_validate_search_params_rejects_unknown_airport_code():
    error = validate_search_params("XXX", "LAX", "2024-03-15", KNOWN_AIRPORTS)

    assert "unknown airport code: XXX" in error


# Searching an airport against itself is a malformed query, not a
# legitimate empty search.
def test_validate_search_params_rejects_same_origin_and_destination():
    error = validate_search_params("JFK", "JFK", "2024-03-15", KNOWN_AIRPORTS)

    assert "different airports" in error
