# Data Scientist Job Tracker

## Overview
Daily pipeline that collects **Google Jobs** results for **“data scientist”** in the **United States** via **SerpApi**, normalizes fields, de-duplicates across runs with a SQLite state file, and saves daily outputs for later analysis.

## Architecture
- **Scraper:** fetches paginated results via SerpApi  
- **Normalizer:** standardizes structure and fields  
- **Seen Store:** deduplicates jobs via SQLite  
- **Policies:** controls request budget and reset logic  
- **Config:** YAML-based settings + environment secrets  

## Repository Layout
- `source/` – core modules  
- `config/` – settings and schema  
- `data/` – raw and processed outputs (local or bucket)  

## Configuration & Data
- **settings.yaml:** search params and budget caps  
- **normalize_schema.json:** tracked core keys  
- **Secrets:** `SERPAPI_KEY`, optional Telegram tokens  
- **Output:** normalized Parquet-ready job records  

## State & Automation
Tracks seen jobs (`seen_jobs.sqlite`) to avoid duplicates.  
Next: add state tracking, logging, and daily GitHub Action runs.

## Roadmap
- [x] Core modules  
- [ ] State tracking & logging  
- [ ] Telegram alerts  
- [ ] Cloudflare R2 storage  
- [ ] CI automation  

## License
MIT License.