from pathlib import Path
import json

from source.logger import get_logger

logger = get_logger()

SUMMARY_JSON = Path("data/meta/last_summary.json")

def build_run_summary(
    today: str | None,
    cap: int,
    remaining_after: int,
    scrape_state: dict,
    seen_stats: dict,
    carryover: int,
    total_seen: int = 0,
) -> dict:
    """Assemble a standardized daily run summary dictionary."""
    used = scrape_state.get("requests_used", 0)
    total_jobs = scrape_state.get("total_jobs", 0)
    inserted = seen_stats.get("inserted", 0)
    touched = seen_stats.get("touched", 0)
    reason = scrape_state.get("reason", "n/a")

    return {
        "date": today,
        "cap": cap,
        "requests_used": used,
        "stop_reason": reason,
        "total_jobs": total_jobs,
        "normalized": touched,
        "uniques": inserted,
        "carryover": carryover,
        "remaining_after": remaining_after,
        "total_seen": total_seen,
    }
    
def print_run_summary(summary: dict):
    """Log a formatted one-line summary of the daily pipeline run."""
    logger.info(
        "SUMMARY | "
        f"date={summary.get('date')} "
        f"cap={summary.get('cap')} "
        f"used={summary.get('requests_used')} "
        f"remaining_after={summary.get('remaining_after')} "
        f"reason={summary.get('stop_reason')} "
        f"jobs={summary.get('total_jobs')} "
        f"normalized={summary.get('normalized')} "
        f"uniques={summary.get('uniques')} "
        f"total_seen={summary.get('total_seen')} "
        f"carryover={summary.get('carryover')} "
    )
    
def format_summary_for_telegram(summary: dict) -> str:
    """Return a compact Telegram-friendly summary message."""
    return (
        f"*Job Tracker — Daily Run*\n"
        f"Date: {summary.get('date')}\n"
        f"Cap: {summary.get('cap')}\n"
        f"Requests used: {summary.get('requests_used')}\n"
        f"Remaining after run: {summary.get('remaining_after')}\n"
        f"Reason: {summary.get('stop_reason')}\n"
        f"Jobs scraped: {summary.get('total_jobs')}\n"
        f"Normalized: {summary.get('normalized')}\n"
        f"Uniques stored: {summary.get('uniques')}\n"
        f"Total seen overall: {summary.get('total_seen')}\n"
        f"Carryover to tomorrow: {summary.get('carryover')}\n"
    )
    
def save_summary_json(summary: dict):
    """
    Save the run summary as JSON for the README stats updater.
    """
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY_JSON.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved summary JSON to {SUMMARY_JSON}")