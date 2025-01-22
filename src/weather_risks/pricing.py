from dataclasses import dataclass
from weather_risks.api import Location, get_precipitation_amounts

@dataclass
class PricingParameters:
    pivot_precipitation_amount: float
    max_daily_turnover: float
    fixed_daily_costs: float
    subscription_date: str
    location: Location

@dataclass
class PricingDetails:
    daily_ca: list[float]
    daily_results: list[float]
    total_losses: float
    yearly_premium: float

def calculate_daily_ca(plt: float, pivot: float, max_daily_turnover: float) -> float:
    if plt >= pivot:
        return 0
    elif 0 < plt < pivot:
        return ((pivot - plt) / pivot) * max_daily_turnover
    else:
        return max_daily_turnover

def price_insurance_yearly_premium(pricing_parameters: PricingParameters) -> PricingDetails:
    # Extract parameters
    location = pricing_parameters.location
    year = int(pricing_parameters.subscription_date[:4])

    # Fetch precipitation data for the specified year
    precipitation_data = get_precipitation_amounts(
        lat=location.latitude,
        lon=location.longitude,
        year=year,
    )

    # Calculate daily values
    daily_ca_list = []
    daily_results_list = []
    total_losses = 0

    for plt in precipitation_data.values:
        daily_ca = calculate_daily_ca(
            plt,
            pricing_parameters.pivot_precipitation_amount,
            pricing_parameters.max_daily_turnover
        )
        daily_result = daily_ca - pricing_parameters.fixed_daily_costs
        daily_ca_list.append(daily_ca)
        daily_results_list.append(daily_result)

        if daily_result < 0:
            total_losses += abs(daily_result)

    # Add a margin to the total losses to calculate the yearly premium
    margin = 0.2  # Example: 20% margin
    yearly_premium = total_losses * (1 + margin)

    return PricingDetails(
        daily_ca=daily_ca_list,
        daily_results=daily_results_list,
        total_losses=total_losses,
        yearly_premium=yearly_premium
    )
