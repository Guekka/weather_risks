from dataclasses import dataclass
from weather_risks.api import geocode, get_precipitation_amounts

@dataclass
class PricingParameters:
    pivot_precipitation_amount: float
    max_daily_turnover: float
    fixed_daily_costs: float
    subscription_date: str
    city: str


def price_insurance_yearly_premium(pricing_parameters: PricingParameters) -> float:
    locations = geocode(pricing_parameters.city)
    if not locations:
        raise ValueError(f"No geocoding results for city: {pricing_parameters.city}")
    location = locations[0]

    precipitation_data = get_precipitation_amounts(
        lat=location.latitude,
        lon=location.longitude,
        year=int(pricing_parameters.subscription_date[:4]),
    )

    days_exceeding_pivot = sum(
        1 for value in precipitation_data.values if value > pricing_parameters.pivot_precipitation_amount
    )

    variable_costs = days_exceeding_pivot * pricing_parameters.max_daily_turnover
    fixed_costs = pricing_parameters.fixed_daily_costs * len(precipitation_data.days)

    yearly_premium = variable_costs + fixed_costs

    return yearly_premium