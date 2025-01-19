from dataclasses import dataclass

import requests
import openmeteo_requests
from requests_cache import CachedSession
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
retry_session = retry(CachedSession(".cache", expire_after=-1), retries=5, backoff_factor=0.2)

GEOCODING_ENDPOINT = "https://geocoding-api.open-meteo.com/v1/search"
ARCHIVE_ENDPOINT = "https://archive-api.open-meteo.com/v1/archive"


@dataclass
class Location:
    latitude: float
    longitude: float
    name: str
    country: str
    timezone: str


@dataclass
class DailyPrecipitationAmounts:
    days: list[str]
    values: list[float]
    year: int


def geocode( searched_place: str) -> list[Location]:
    params = {
        "name": searched_place,
    }

    api_res = retry_session.get(GEOCODING_ENDPOINT, params=params).json()
    return [
        Location(
            latitude=location["latitude"],
            longitude=location["longitude"],
            name=location["name"],
            country=location["country"],
            timezone=location["timezone"],
        )
        for location in api_res["results"]
    ]

def get_precipitation_amounts(lat: float, lon: float, year: int
):
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": f"{year}-01-01",
        "end_date": f"{year}-12-31",
        "daily": "precipitation_sum",
    }

    api_res = retry_session.get(ARCHIVE_ENDPOINT, params=params).json()
    print(api_res)
    return DailyPrecipitationAmounts(
        days=api_res["daily"]["time"],
        values=api_res["daily"]["precipitation_sum"],
        year=year,
    )
