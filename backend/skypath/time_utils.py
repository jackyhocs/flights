from datetime import datetime, timezone
from zoneinfo import ZoneInfo

SECONDS_PER_MINUTE = 60


def to_utc(local_iso: str, tz_name: str) -> datetime:
    naive = datetime.fromisoformat(local_iso)
    aware = naive.replace(tzinfo=ZoneInfo(tz_name))
    return aware.astimezone(timezone.utc)


def duration_minutes(start_utc: datetime, end_utc: datetime) -> int:
    return int((end_utc - start_utc).total_seconds() // SECONDS_PER_MINUTE)


def is_domestic(airports: list) -> bool:
    countries = {airport.country for airport in airports}
    return len(countries) == 1
