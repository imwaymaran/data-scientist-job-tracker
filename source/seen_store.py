from pathlib import Path
import sqlite3

from source.logger import get_logger

logger = get_logger()

DEFAULT_SEEN_DB = "data/state/seen_jobs.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS job_seen (
    job_key TEXT PRIMARY KEY,
    first_seen DATE NOT NULL,
    last_seen DATE NOT NULL
);
"""

def open_seen_db(db_path: str | Path = DEFAULT_SEEN_DB) -> sqlite3.Connection:
    """
    Open (and initialize if needed) the SQLite database for seen jobs.
    Ensures schema exists and returns a ready-to-use connection.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    
    conn.execute(SCHEMA)
    conn.commit()
    
    return conn

def select_seen(conn: sqlite3.Connection, job_keys: list[str], chunk: int = 800) -> set[str]:
    """Return the subset of job_keys already present in job_seen."""
    if not job_keys:
        return set()
    seen = set()
    for i in range(0, len(job_keys), chunk):
        part = job_keys[i:i+chunk]
        q = ",".join("?" * len(part))
        rows = conn.execute(
            f"SELECT job_key FROM job_seen WHERE job_key IN ({q})", part
        ).fetchall()
        seen.update(r[0] for r in rows)
    return seen

def insert_new_keys(conn: sqlite3.Connection, new_keys: list[str], today: str) -> int:
    """INSERT new keys with first_seen=last_seen=today."""
    new_keys = [k for k in new_keys if k]
    if not new_keys:
        return 0
    conn.executemany(
        "INSERT INTO job_seen(job_key, first_seen, last_seen) VALUES (?, ?, ?)",
        [(k, today, today) for k in new_keys]
    )
    return len(new_keys)

def update_existing_keys(conn: sqlite3.Connection, existing_keys: list[str], today: str) -> int:
    """UPDATE last_seen for keys we already have."""
    existing_keys = [k for k in existing_keys if k]
    if not existing_keys:
        return 0
    conn.executemany(
        "UPDATE job_seen SET last_seen=? WHERE job_key=?",
        [(today, k) for k in existing_keys]
    )
    return len(existing_keys)


def upsert_and_filter_uniques(
    conn: sqlite3.Connection,
    records: list[dict],
    today: str
) -> tuple[list[dict], dict]:
    """
    Return only records not seen before; also insert new keys and update last_seen
    for previously seen keys. Writes are done in a single transaction.
    """
    keyed = [(record.get("job_key"), record) for record in records if record.get("job_key")]
    keys = [key for key, _ in keyed]
    if not keys:
        return [], {"already_seen": 0, "inserted": 0, "updated": 0} 
    
    seen = select_seen(conn, keys)
    new_keys = [key for key in keys if key not in seen]
    existing_keys = [key for key in keys if key in seen]
    
    uniques = [record for key, record in keyed if key in set(new_keys)]
    already_seen = len(existing_keys)
    
    with conn:
        inserted = insert_new_keys(conn, new_keys, today)
        updated  = update_existing_keys(conn, existing_keys, today)

    stats = {
        "already_seen": already_seen,
        "inserted": inserted,
        "updated": updated,
        "touched": inserted + updated
    }
    logger.info(f"Seen upsert: inserted={inserted}, updated={updated}, uniques={len(uniques)}")
    return uniques, stats