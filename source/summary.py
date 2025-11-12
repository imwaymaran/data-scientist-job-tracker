def build_run_summary(
    today: str | None,
    cap: int,
    remaining: int,
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
    remaining_quota = max(0, remaining - used)

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
    """Pretty-print a short debug summary of the daily run."""
    print("\nRUN SUMMARY")
    print(f"Date: {summary.get('date', 'n/a')}")
    print(f"Cap: {summary.get('cap', 0)}")
    print(f"Requests used: {summary.get('requests_used', 0)}")
    print(f"Stop reason: {summary.get('stop_reason', 'n/a')}")
    print(f"Jobs scraped: {summary.get('total_jobs', 0)}")
    print(f"Normalized: {summary.get('normalized', 0)} | Uniques: {summary.get('uniques', 0)}")
    print(f"Carryover: {summary.get('carryover', 0)}")
    print(f"Remaining quota: {summary.get('remaining_quota', 0)}")
    print("-" * 35)    