import re
import hashlib
from source.logger import get_logger
logger = get_logger()

def _clean_text(s):
    """Trim extra whitespace and return None if the string is empty."""
    if not s:
        return None
    s = " ".join(str(s).split()).strip()
    return s or None

def _norm_text(s):
    """Normalize text to lowercase single-spaced form."""
    if not s: 
        return ""
    return " ".join(str(s).lower().split())
    
def _desc_fingerprint(text):
    """Return an MD5 fingerprint of description text for deduplication."""
    if not text: 
        return None
    t = text.lower()
    t = re.sub(r"\d+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return hashlib.md5(t.encode("utf-8")).hexdigest()

def _make_job_key(job_id, title, company, location, description_raw):
    """Generate a stable job identifier based on job_id or text fingerprint."""
    if job_id:
        return f"id:{job_id}"
    h = _desc_fingerprint(description_raw)
    if h:
        return f"desc:{h}"
    comp = f"{_norm_text(title)}|{_norm_text(company)}|{_norm_text(location)}"
    comp_hash = hashlib.md5(comp.encode("utf-8")).hexdigest()
    return f"cmp:{comp_hash}"

def _normalize_job(job: dict, core_keys: list[str], scrape_date: str) -> dict:
    """Convert one raw SerpApi job record into a standardized dictionary."""
    job_id = job.get("job_id")
    title = _clean_text(job.get("title"))
    company = _clean_text(job.get("company_name"))
    location = _clean_text(job.get("location"))
    via = _clean_text(job.get("via"))
    thumbnail = job.get("thumbnail")
    google_share_url = job.get("share_link")

    det = job.get("detected_extensions") or {}
    posted_at_raw = _clean_text(det.get("posted_at"))
    job_metadata_raw = {
        str(key).lower(): (str(value).lower() if isinstance(value, str) else value)
        for key, value in det.items()
    }

    description_raw = job.get("description")
    job_highlights_raw = job.get("job_highlights") or []
    apply_options_raw = job.get("apply_options") or []
    
    extras = {key: value for key, value in job.items() if key not in set(core_keys)}
    job_key = _make_job_key(job_id, title, company, location, description_raw)

    return {
        "scrape_date": scrape_date,
        "job_id": job_id,
        "job_key": job_key,
        "title": title,
        "company": company,
        "location": location,
        "via": via,
        "google_share_url": google_share_url,
        "thumbnail": thumbnail,
        "posted_at_raw": posted_at_raw,
        "job_metadata_raw": job_metadata_raw,   
        "job_highlights_raw": job_highlights_raw,
        "description_raw": description_raw,     
        "apply_options_raw": apply_options_raw, 
        "extras": extras
    }
    
def normalize_batch(raw_jobs: list[dict], core_keys: list[str], scrape_date: str) -> list[dict]:
    """Normalize a batch of raw SerpApi job dicts into standardized records."""
    records = []
    for job in raw_jobs:
        try:
            record = _normalize_job(job, core_keys, scrape_date)
            if record["title"] and record["company"]:
                records.append(record)
            else:
                logger.info("Dropped record without title or company")
        except Exception as e:
            logger.warning(f"Failed to normalize job: {e}")
    logger.info(f"Normalized {len(records)} records from {len(raw_jobs)} raw")   
    return records