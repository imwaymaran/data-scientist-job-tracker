# Data Scientist Job Tracker

Daily automated pipeline that tracks **Data Scientist job postings** and keeps a clean, **structured dataset** for long-term analysis.

## Daily Stats
*(Updated automatically every day)*  

<!-- STATS_START -->
**Last run:** Dec 26, 2025 at 08:00 AM EST  

| Metric                 | Value |
|------------------------|-------|
| Total jobs tracked     | 1686 |
| Jobs collected today   | 115 |
| New unique roles today | 96 |
<!-- STATS_END -->

## Overview

This project creates a reliable daily record of Data Scientist job openings to support long-term trend analysis.  
An automated pipeline collects public job postings from Google Jobs each morning, cleans and structures the data, deduplicates it across days, and stores the results in long-term object storage.

The current configuration collects postings from **New York City and nearby areas**, but the location can be changed at any time through the settings file.

**Part 1** focuses on building a clean, continuously growing dataset.  
**Part 2** will use that dataset to reveal patterns in hiring demand, geography, seniority, and how the job market evolves over time.

The pipeline is set up to run on its own for **months** with **no ongoing expenses**.  
Using only **free tier services** such as **SerpApi**, **GitHub Actions**, **Cloudflare R2**, and **Telegram**, it keeps collecting and storing data quietly in the background until it is time to begin the analysis phase.

## Features

### Automated Daily Collection
- Fetches Google Jobs listings through SerpApi with configurable query and location.
- Uses a quota-aware request cap to avoid over-spending API budget.
- Fully automated through GitHub Actions.

### Normalization & Deduplication
- Transforms raw SerpApi JSON into a consistent, analysis-ready schema.
- Generates a stable `job_key` to track identical postings across days.
- Maintains a SQLite database of all seen jobs to avoid duplicates and measure job “lifetimes.”

### Reliable Storage & Versioning
- Saves raw JSON and processed Parquet snapshots locally.
- Syncs state and outputs to Cloudflare R2 for durable, long-term storage.
- Structure mirrors local folders for easy downstream analysis.

### Monitoring & Observability
- Structured logging at each pipeline stage.
- Automatic Telegram notifications with daily summaries.
- Error alerts sent directly to the Telegram bot for visibility.

### Modular & Extensible Design
- Clear separation of scraping, normalization, state handling, and storage.
- YAML-based config allows easy changes to search parameters, locations, and request budgets.
- Designed so future jobs (e.g., multiple search terms or cities) can be added without rewriting the pipeline.

## Architecture

### 1. Scraper  
Fetches raw Google Jobs data from SerpApi, handles pagination, stop conditions, and rate-control logic.  
Writes raw JSON snapshots for full reproducibility.  
Code: [`source/scraper.py`](source/scraper.py)

### 2. Normalizer  
Transforms raw SerpApi responses into a consistent schema defined in  
[`config/normalize_schema.json`](config/normalize_schema.json).  
Generates stable `job_key` identifiers for cross-day tracking.  
Code: [`source/normalize.py`](source/normalize.py)

### 3. Seen Store (Deduplication)  
Tracks which jobs have ever appeared using a SQLite table with  
`job_key`, `first_seen`, and `last_seen`.  
Enables identifying **new**, **returning**, and **persistent** postings.  
Code: [`source/seen_store.py`](source/seen_store.py)

### 4. State Store  
Maintains SerpApi request usage between runs, including last monthly reset  
and unused carryover capacity.  
Code: [`source/state_store.py`](source/state_store.py)

### 5. Storage Layer  
Saves daily outputs (raw JSON + processed Parquet) locally and syncs them to  
Cloudflare R2 via S3-compatible operations.  
Code: [`source/storage.py`](source/storage.py)

### 6. Automation & Alerts  
Daily GitHub Actions workflow runs the pipeline at **13:00 UTC**, with  
Telegram notifications reporting success or failure and run statistics.  
Code: [`source/telegram_bot.py`](source/telegram_bot.py), [`source/runner.py`](source/runner.py)

## Repository Layout

```text
.
├── config/
│   ├── settings.yaml              # Search parameters, budget rules
│   └── normalize_schema.json      # Schema for normalized job fields
│
├── data/                          # Auto-created locally (or synced from R2)
│   ├── raw/                       # Daily raw JSON snapshots
│   ├── processed/                 # Daily Parquet outputs
│   └── state/                     # SQLite: run_state.sqlite + seen_jobs.sqlite
│
├── source/
│   ├── account.py                 # Fetch SerpApi quota + usage
│   ├── config_loader.py           # YAML + env variable loader
│   ├── logger.py                  # Centralized logging
│   ├── normalize.py               # Schema extraction + job_key generation
│   ├── policies.py                # Request cap logic (daily + rollover)
│   ├── scraper.py                 # SerpApi fetcher with pagination
│   ├── seen_store.py              # SQLite store for deduplication
│   ├── state_store.py             # Track resets + carryover state
│   ├── storage.py                 # Save JSON/Parquet
│   ├── summary.py                 # Summary builder + Telegram formatter 
│   ├── telegram_bot.py            # Telegram notifications
│   ├── update_readme_stats.py     # Update README "Daily Stats" section after each run
│   └── runner.py                  # Pipeline orchestrator
│
├── .github/
│   └── workflows/
│       └── daily.yml              # GitHub Actions workflow
│
├── .env.example                   # Template for required env variables
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone and install

```bash
git clone https://github.com/imwaymaran/data-scientist-job-tracker.git
cd data-scientist-job-tracker

conda create -n jobtracker python=3.10
conda activate jobtracker

python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then open `.env` and fill your credentials:

- **SerpApi** key  
- **Telegram** bot token + chat ID (optional)  
- **Cloudflare R2** credentials (for GitHub Actions long-term storage) 
- **Access Key ID / Secret Access Key** (S3-style credentials for R2)

## Configuration

All configuration lives in the [`config/`](config/) directory:

- **[`settings.yaml`](config/settings.yaml)**  
  Defines search parameters (query, location, filters), SerpApi settings, and daily request-budget rules.

- **[`normalize_schema.json`](config/normalize_schema.json)**  
  Specifies the normalized field schema used when converting raw SerpApi data into clean, structured rows.

Secrets and credentials are provided through environment variables (see [`.env.example`](.env.example)):

- `SERPAPI_KEY` — SerpApi API key  
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — Telegram notifications (optional)  
- `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_R2_BUCKET` — R2 storage configuration  
- `CLOUDFLARE_R2_ACCESS_KEY_ID`, `CLOUDFLARE_R2_SECRET_ACCESS_KEY` — S3-compatible credentials for syncing state and outputs

## Running Locally

This project does **not** automatically read `.env` files.  
If you want to run the pipeline locally, you must load environment variables into your shell.

### 1. Export environment variables

Option A — Export directly in your shell:

```bash
export SERPAPI_KEY="your_key"
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

Option B — If you prefer using a `.env` file, install `python-dotenv`:

```bash
pip install python-dotenv
```

And add this at the top of `source/config_loader.py` and `source/telegram_bot.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

### 2. Run the pipeline

```bash
python -m source.runner
```

### 3. Outputs

- Raw JSON: `data/raw/`
- Normalized Parquet: `data/processed/`
- State databases: `data/state/`

## Scheduled Runs (GitHub Actions + R2)

A scheduled GitHub Actions workflow runs the pipeline in the cloud and keeps its state synchronized with Cloudflare R2:

1. Syncs state databases from R2 → `data/state/`
2. Runs `python -m source.runner` on a GitHub-hosted runner
3. Uploads updated state and daily outputs (`data/raw/`, `data/processed/`) back to R2
4. Sends a Telegram summary (and failure alerts, if enabled)

By default, the workflow is scheduled for **13:00 UTC every day**, which is **8:00 or 9:00 AM in New York** depending on daylight saving time.  
The workflow can also be triggered manually through GitHub Actions.

Workflow file: [`.github/workflows/daily.yml`](.github/workflows/daily.yml)

## Example Daily Run Summary

Below is a typical daily summary sent to Telegram after a successful run:

```
Job Tracker — Daily Run
Date: 2025-11-15
Cap: 12
Requests used: 12
Remaining after run: 203
Reason: limit_reached
Jobs scraped: 97
Normalized: 96
Uniques stored: 96
Total seen overall: 412
Carryover to tomorrow: 0
```

## Roadmap

- [x] Daily scraping pipeline  
- [x] Normalization & deduplication  
- [x] Persistent state tracking  
- [x] Cloudflare R2 integration  
- [x] GitHub Actions automation  
- [x] Telegram notifications  

**Next:**
- [ ] Maintain pipeline and grow dataset  
- [ ] Publish dataset on Kaggle  
- [ ] Begin analysis (Part 2)  

## License

This project is licensed under the MIT License.  
Feel free to use, modify, and distribute the code in accordance with the license terms.