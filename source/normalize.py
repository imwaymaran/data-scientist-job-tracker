import re, hashlib

def clean_text(s):
    """Trim extra whitespace and return None if the string is empty."""
    if not s: return None
    s = " ".join(str(s).split()).strip()
    return s or None

def norm_text(s):
    """Normalize text to lowercase single-spaced form."""
    if not s: return ""
    return " ".join(str(s).lower().split())
    
def desc_fingerprint(text):
    """Return an MD5 fingerprint of description text for deduplication."""
    if not text: return None
    t = text.lower()
    t = re.sub(r"\d+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return hashlib.md5(t.encode("utf-8")).hexdigest()

def make_job_key(job_id, title, company, location, description_raw):
    """Generate a stable job identifier based on job_id or text fingerprint."""
    if job_id:
        return f"id:{job_id}"
    h = desc_fingerprint(description_raw)
    if h:
        return f"desc:{h}"
    comp = f"{norm_text(title)}|{norm_text(company)}|{norm_text(location)}"
    short = (h or "")[:8]
    return f"cmp:{comp}|{short}"

def normalize_job(job: dict, core_keys: list[str], scrape_date: str) -> dict:
    """Convert one raw SerpApi job record into a standardized dictionary."""
    job_id = job.get("job_id")
    title = clean_text(job.get("title"))
    company = clean_text(job.get("company_name"))
    location = clean_text(job.get("location"))
    via = clean_text(job.get("via"))
    thumbnail = job.get("thumbnail")
    google_share_url = job.get("share_link")

    det = job.get("detected_extensions") or {}
    posted_at_raw = clean_text(det.get("posted_at"))
    job_metadata_raw = {
        str(key).lower(): (str(value).lower() if isinstance(value, str) else value)
        for key, value in det.items()
    }

    description_raw = job.get("description")
    job_highlights_raw = job.get("job_highlights") or []
    apply_options_raw = job.get("apply_options") or []

    extras = {key: value for key, value in job.items() if key not in core_keys}
    job_key = make_job_key(job_id, title, company, location, description_raw)

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
            record = normalize_job(job, core_keys, scrape_date)
            if record["title"] and record["company"]:
                records.append(record)
        except Exception as e:
            # log it later instead of print
            print(f"Failed to normalize job: {e}")
    return records