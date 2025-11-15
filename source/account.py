import requests
from .config_loader import get_serpapi_key
from .logger import get_logger


ACCOUNT_URL = "https://serpapi.com/account"
logger = get_logger()

def fetch_account_info():
    """Fetch SerpApi account info for quota calculation."""
    api_key = get_serpapi_key()

    try:
        r = requests.get(ACCOUNT_URL, params={"api_key": api_key}, timeout=15)
        r.raise_for_status()
        account = r.json()
    except requests.Timeout:
        logger.exception("Timeout while fetching account info from SerpApi.")
        raise
    except requests.RequestException as e:
        logger.exception(f"Failed to fetch account info: {e}")
        raise

    quota = account.get("searches_per_month")
    remaining = account.get("plan_searches_left")
    used = account.get("this_month_usage")

    logger.info(f"Fetched SerpApi account info: quota={quota}, remaining={remaining}, used={used}")
    return quota, remaining, used