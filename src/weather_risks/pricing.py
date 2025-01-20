from dataclasses import dataclass


@dataclass
class PricingParameters:
    pivot_precipitation_amount: float
    max_daily_turnover: float
    fixed_daily_costs: float
    subscription_date: str
    city: str


def price_insurance_yearly_premium(pricing_parameters: PricingParameters) -> float:
    # TODO
    pass
