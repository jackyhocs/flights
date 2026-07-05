from skypath.models import Flight


def is_domestic(*countries: str) -> bool:
    return len(set(countries)) == 1


def is_domestic_connection(inbound: Flight, outbound: Flight) -> bool:
    return is_domestic(
        inbound.origin_country, inbound.destination_country, outbound.destination_country,
    )
