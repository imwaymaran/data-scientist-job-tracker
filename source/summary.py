from source.logger import get_logger

logger = get_logger()

def build_run_summary(
    today: str | None,
    cap: int,
    remaining_after: int,
    scrape_state: dict,
    seen_stats: dict,
    carryover: int,
) -> dict:
    """Assemble a standardized daily run summary dictionary."""
    used = scrape_state.get("requests_used", 0)
    total_jobs = scrape_state.get("total_jobs", 0)
    inserted = seen_stats.get("inserted", 0)
    touched = seen_stats.get("touched", 0)
    reason = scrape_state.get("reason", "n/a")
    remaining_quota = max(0, remaining_after - used)

    return {
        "date": today,
        "cap": cap,
        "requests_used": used,
        "stop_reason": reason,
        "total_jobs": total_jobs,
        "normalized": touched,
        "uniques": inserted,
        "carryover": carryover,
        "remaining_quota": remaining_quota
    }  
    
def print_run_summary(summary: dict):
    """Log a formatted one-line summary of the daily pipeline run."""
    logger.info(
        "SUMMARY | "
        f"date={summary.get('date')} "
        f"cap={summary.get('cap')} "
        f"used={summary.get('requests_used')} "
        f"reason={summary.get('stop_reason')} "
        f"jobs={summary.get('total_jobs')} "
        f"normalized={summary.get('normalized')} "
        f"uniques={summary.get('uniques')} "
        f"carryover={summary.get('carryover')} "
        f"remaining quota={summary.get('remaining_quota')} "
    )