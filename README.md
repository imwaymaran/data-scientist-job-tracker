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

## Why
- Build a reproducible, low-cost pipeline.
- Track job trends over time.
- Keep the repo active with daily commits.
- Prepare long-term dataset for analysis later.