from datetime import date
from math import ceil

def calculate_cap(
    remaining: int,
    last_reset: date,
    today: date,
    budget: dict,
    window_days: int = 30,
    carryover_requests: int = 0,
) -> int:
    """Calculate today's request cap based on remaining quota and weekday multiplier."""
    min_requests = budget["min_requests"]
    max_requests = budget["max_requests"]
    weekday_mult = budget["weekday_mult"]

    days_since = (today - last_reset).days
    days_left = max(1, window_days - max(0, days_since))

    base_per_day = ceil(remaining / days_left)
    mult = weekday_mult.get(today.strftime("%a"), 1.0)

    today_cap = round(base_per_day * mult + carryover_requests)
    return max(min_requests, min(today_cap, max_requests, remaining))

def detect_reset(quota: int, remaining: int, used: int) -> bool:
    """Return True if the SerpApi quota appears to have reset."""
    return quota > 0 and used == 0 and remaining == quota