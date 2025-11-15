import time
import requests

from source.logger import get_logger

logger = get_logger()

ENDPOINT = "https://serpapi.com/search.json"

def fetch_jobs(params: dict, today_cap: int, delay: float = 0.3) -> tuple[list[dict], dict]:
    """Fetch job postings from SerpApi with pagination and basic rate control.
    
    Returns:
        all_jobs: list of raw job dicts
        stats: dict with debug info (pages, total_jobs, reason)
    """
    used = 0
    token = None
    all_jobs = []
    reason = "limit_reached"

    while used < today_cap:
        if token:
            params["next_page_token"] = token
        elif "next_page_token" in params:
            del params["next_page_token"]

        try:
            r = requests.get(ENDPOINT, params=params, timeout=30)
            r.raise_for_status()
        except requests.exceptions.Timeout:
            reason = f"timeout_page_{used+1}"
            logger.warning(reason)
            break
        except requests.RequestException as e:
            reason = f"error_page_{used+1}:{e}"
            logger.error(reason)
            break

        used += 1
        data = r.json()
        jobs = data.get("jobs_results", [])

        if not jobs:
            reason = f"empty_page_{used}"
            logger.info(f"No jobs on page {used}")
            break

        pagination = data.get("serpapi_pagination") or {}
        token = pagination.get("next_page_token")

        all_jobs.extend(jobs)

        if len(jobs) < 10:
            reason = f"tail_page_{used}"
            logger.info(f"Tail page with {len(jobs)} jobs at page {used}")
            break
        if not token:
            reason = f"no_next_page_{used}"
            logger.info(f"No next_page_token after page {used}")
            break

        time.sleep(delay)

    stats = {"requests_used": used, "total_jobs": len(all_jobs), "reason": reason}
    logger.info(f"Fetched pages={used}, jobs={len(all_jobs)}, reason={reason}")
    return all_jobs, stats