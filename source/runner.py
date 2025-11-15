from datetime import date

from source.account import fetch_account_info
from source.config_loader import (
    load_settings,
    get_serpapi_key,
    build_serpapi_params,
    load_core_keys,
)
from source.logger import get_logger
from source.normalize import normalize_batch
from source.policies import calculate_cap, detect_reset
from source.scraper import fetch_jobs
from source.seen_store import (
    open_seen_db, 
    upsert_and_filter_uniques, 
    count_total_seen
)
from source.state_store import (
    open_state_db,
    get_state,
    update_last_reset,
    update_carryover,
)
from source.storage import save_raw_json, save_processed_parquet
from source.telegram_bot import send_telegram_message
from source.summary import (
    build_run_summary,
    print_run_summary,
    format_summary_for_telegram,
)

logger = get_logger()

def main():
    """
    Run the full Data Scientist Job Tracker pipeline.

    Steps:
    1. Load configuration and API key.
    2. Fetch account info and compute request cap.
    3. Scrape job listings from SerpApi.
    4. Normalize and deduplicate results.
    5. Save raw JSON and processed Parquet.
    6. Update persistent state and summarize run.

    Handles logging, errors, and state persistence automatically.
    """
    logger.info("Run started")
    
    today_iso = date.today().isoformat()
    settings = load_settings()
    budget = settings["budget"]
    api_key = get_serpapi_key()
    params = build_serpapi_params(settings, api_key)
    core_keys = load_core_keys()
    
    state_conn = open_state_db(today_iso)
    seen_conn = None
    try:
        # ---- State + account
        state = get_state(state_conn)
        last_reset = state["last_reset"] 
        carryover_requests = state["carryover_requests"]

        quota, remaining, used = fetch_account_info()
        if detect_reset(quota, remaining, used):
            logger.info("Detected monthly reset from SerpApi account endpoint.")
            update_last_reset(state_conn, today_iso)
            update_carryover(state_conn, 0)
            carryover_requests = 0
            
        # ---- Cap
        cap = calculate_cap(
            remaining=remaining,
            last_reset=last_reset,
            today=today_iso,
            budget=budget,
            carryover_requests=carryover_requests,
        )
        if cap <= 0:
            update_carryover(state_conn, 0)
            logger.info("Cap is 0, skipping scrape.")
            summary = build_run_summary(
                today=today_iso, cap=0, remaining_after=remaining,
                scrape_state={"requests_used": 0, "total_jobs": 0, "reason": "cap_zero"},
                seen_stats={"touched": 0, "inserted": 0, "updated": 0},
                carryover=0
            )
            print_run_summary(summary)
            text = format_summary_for_telegram(summary)
            send_telegram_message(text)
            return
        logger.info(f"Cap computed: cap={cap} (remaining={remaining}, carryover={carryover_requests})")
        
        # ---- Scrape
        raw_jobs, scrape_state = fetch_jobs(dict(params), cap)
        logger.info(f"Stop reason: {scrape_state.get('reason')}")
        if raw_jobs:
            save_raw_json(raw_jobs, today_iso)
        else:
            logger.info("No raw jobs returned; skipping normalization/storage.")

        # ---- Normalize + dedup
        normalized = normalize_batch(raw_jobs, core_keys, today_iso) if raw_jobs else []
        seen_conn = open_seen_db()
        if normalized:
            uniques, seen_stats = upsert_and_filter_uniques(seen_conn, normalized, today_iso)
        else:
            uniques, seen_stats = [], {"touched": 0, "inserted": 0, "updated": 0}
                
        # ---- Store processed
        if uniques:  
            save_processed_parquet(uniques, today_iso)
            logger.info(f"Normalized {len(normalized)} rows, stored {len(uniques)} uniques.")
            
        else:
            logger.info("No unique rows to store.")

        # ---- State update (carryover)
        requests_used = scrape_state.get("requests_used", 0)
        unused_today = max(0, cap - requests_used)
        update_carryover(state_conn, unused_today)
        
        remaining_after = max(0, remaining - requests_used)
        
        total_seen = count_total_seen(seen_conn)
        
        summary = build_run_summary(
            today=today_iso,
            cap=cap,
            remaining_after=remaining_after,
            scrape_state=scrape_state,
            seen_stats=seen_stats,
            carryover=unused_today,
            total_seen=total_seen,
        )
        print_run_summary(summary)
        
        text = format_summary_for_telegram(summary)
        send_telegram_message(text)
        
        logger.info("Run finished")
    
    finally:
        try:
            if seen_conn is not None:
                seen_conn.close()
        finally:
            state_conn.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        msg = (
            "Job Tracker — pipeline FAILED\n"
            f"Error type: {type(e).__name__}\n"
            f"Message: {e}"
        )
        send_telegram_message(msg)
        raise