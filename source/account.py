import requests
from .config_loader import get_serpapi_key

ACCOUNT_URL = "https://serpapi.com/account"

def fetch_account_info():
    """Fetch SerpApi account info for quota calculation."""
    api_key = get_serpapi_key()
    r = requests.get(ACCOUNT_URL, params={"api_key": api_key}, timeout=15)
    r.raise_for_status()
    account = r.json()
    
    quota = account.get("searches_per_month")
    remaining = account.get("plan_searches_left")
    used = account.get("this_month_usage")
    
    return quota, remaining, used