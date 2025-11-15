from pathlib import Path
import json
import pyarrow as pa
import pyarrow.parquet as pq

from source.logger import get_logger

logger = get_logger()

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
RAW_TEMPLATE = "raw_jobs_{date}.json"
PARQUET_TEMPLATE = "jobs_{date}.parquet"
NESTED_KEYS = ["job_metadata_raw", "job_highlights_raw", "apply_options_raw", "extras"]

def _to_parquet_row(rec: dict) -> dict:
    row = dict(rec)
    for k in NESTED_KEYS:
        v = row.get(k)
        if v in (None, {}, []):
            row[k] = None
        else:
            row[k] = json.dumps(v, ensure_ascii=False)
    return row

def save_raw_json(records: list[dict], run_date: str) -> Path:
    """Save raw API results as JSON.""" #  no validation here
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / RAW_TEMPLATE.format(date=run_date)
    with path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved raw JSON to {path}")
    return path

def save_processed_parquet(records: list[dict], run_date: str) -> Path:
    """Save normalized records as Parquet."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / PARQUET_TEMPLATE.format(date=run_date)
    
    rows = [_to_parquet_row(r) for r in records]
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, path)
    logger.info(f"Saved Parquet to {path}")
    return path