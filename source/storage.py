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
    table = pa.Table.from_pylist(records)  # will error on empty; you’ll handle upstream
    pq.write_table(table, path)
    logger.info(f"Saved Parquet to {path}")
    return path