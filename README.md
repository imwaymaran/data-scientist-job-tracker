# data-scientist-job-tracker

---

## What
Automated scraper that collects **Data Scientist** job postings from **Google Jobs** via **SerpApi** once per day.

---

## How
1. GitHub Action triggers daily.
2. `scrape.py` fetches pages from SerpApi, normalizes results, and deduplicates.
3. `make_summary.py` generates short stats.
4. Stats are written to `STATS.md` and a README block.
5. `notify.py` sends a Telegram message.

---

## Data Dictionary

| Field | Type | Description |
|--------|------|-------------|
| `scrape_date` | `string (YYYY-MM-DD)` | Date when the job was collected |
| `job_id` | `string \| None` | Original identifier from Google Jobs / SerpApi (if provided) |
| `job_key` | `string` | Internal deterministic key for deduplication (based on `job_id`, description hash, or title/company/location) |
| `title` | `string \| None` | Job title as displayed in Google Jobs |
| `company` | `string \| None` | Company name |
| `location` | `string \| None` | Job location text (city, state, or “Remote”) |
| `via` | `string \| None` | Source platform shown under the listing (e.g., LinkedIn, Indeed) |
| `google_share_url` | `string \| None` | Canonical Google Jobs share link |
| `thumbnail` | `string \| None` | Logo thumbnail if available |
| `posted_at_raw` | `string \| None` | Raw posting age string (e.g., “3 days ago”) |
| `job_metadata_raw` | `dict` | Parsed structured metadata from Google (schedule type, salary, work mode, etc.). Empty `{}` if unavailable |
| `job_highlights_raw` | `list` | List of highlight sections (each with `title` and `items`). Empty `[]` if none |
| `description_raw` | `string \| None` | Full job description text |
| `apply_options_raw` | `list` | List of application options (each a dict with `title` and `link`). Empty `[]` if none |
| `extras` | `dict` | Any unexpected fields not covered above. Empty `{}` if none |

---
## Why
- Build a reproducible, low-cost pipeline.
- Track job trends over time.
- Keep the repo active with daily commits.
- Prepare long-term dataset for analysis later.