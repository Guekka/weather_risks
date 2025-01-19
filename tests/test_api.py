from weather_risks.api import Location, geocode, get_precipitation_amounts

NICE_LATITUDE = 43.70313
NICE_LONGITUDE = 7.26608

def test_geocode():
    nice_france_location = Location(
        latitude=NICE_LATITUDE,
        longitude=NICE_LONGITUDE,
        name="Nice",
        country="France",
        timezone="Europe/Paris",
    )

    assert geocode("Nice")[0] == nice_france_location

def test_get_precipitation_amounts():
    res = get_precipitation_amounts(NICE_LATITUDE, NICE_LONGITUDE, 2021)
    assert len(res.days) == 365

    sum_precipitation = sum(res.values)
    assert sum_precipitation == 624.4
