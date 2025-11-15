# Data Scientist Job Tracker

## Overview
Daily pipeline that uses **SerpApi** to fetch **Google Jobs** results for **“data scientist”** roles in a configurable location (currently: **New York, NY**), normalizes and de-duplicates them, and stores daily outputs for analysis.

## Architecture
- **Scraper:** Fetches paginated job results via SerpApi with rate control  
- **Normalizer:** Cleans and standardizes raw fields into a uniform schema  
- **Seen Store:** Tracks and deduplicates jobs using a local SQLite database  
- **Policies:** Calculates daily request caps and detects quota resets  
- **State Store:** Persists last reset date and carryover request counts  
- **Storage:** Saves raw JSON and processed Parquet outputs  
- **Logger:** Centralized structured logging for debugging and monitoring  
- **Config:** YAML-based settings and environment-managed secrets   

## Repository Layout
- `source/` – core modules  
- `config/` – settings and schema  
- `data/` – raw and processed outputs (local or bucket)  

## Configuration & Data
- **settings.yaml:** Defines search parameters and request budget limits  
- **normalize_schema.json:** Lists core fields tracked during normalization  
- **Secrets:** Environment variables (`SERPAPI_KEY`)  
- **Output:** Raw JSON and Parquet datasets of normalized job records   

## State & Automation
- **Seen Jobs:** SQLite database (`seen_jobs.sqlite`) tracks previously scraped jobs to prevent duplicates  
- **State Store:** Persists run metadata such as last reset date and carryover requests  
- **Next Steps:** Add schedule daily runs via GitHub Actions  

## Roadmap
- [x] Core modules  
- [x] State tracking & logging  
- [x] Telegram alerts  
- [x] Cloudflare R2 storage  
- [ ] CI automation  

## License
MIT License.