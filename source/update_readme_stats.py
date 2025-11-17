import json
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from source.logger import get_logger

logger = get_logger()

SUMMARY_JSON = Path("data/meta/last_summary.json")
README_PATH = Path("README.md")


def load_summary() -> dict | None:
    """Load the last run summary JSON if it exists, otherwise return None."""
    if not SUMMARY_JSON.exists():
        logger.warning("Summary JSON not found, skipping README stats update.")
        return None
    try:
        with SUMMARY_JSON.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load summary JSON: {e}")
        return None


def _format_last_run_nyc() -> str:
    """Return today's run timestamp formatted in New York local time."""
    ny = ZoneInfo("America/New_York")
    now = datetime.now(ny)

    dt = datetime(now.year, now.month, now.day, now.hour, 0, tzinfo=ny)

    return dt.strftime("%b %d, %Y at %I:%M %p %Z")


def _build_stats_block(summary: dict) -> str:
    """Build the Markdown block for the Daily Stats section."""
    last_run = _format_last_run_nyc()
    total_seen = summary.get("total_seen", "—")
    total_jobs = summary.get("total_jobs", "—")
    uniques = summary.get("uniques", "—")

    return (
        "<!-- STATS_START -->\n"
        f"**Last run:** {last_run}  \n\n"
        "| Metric                 | Value |\n"
        "|------------------------|-------|\n"
        f"| Total jobs tracked     | {total_seen} |\n"
        f"| Jobs collected today   | {total_jobs} |\n"
        f"| New unique roles today | {uniques} |\n"
        "<!-- STATS_END -->"
    )


def update_readme(summary: dict) -> bool:
    """Replace the Daily Stats block in README.md with fresh values."""
    if not README_PATH.exists():
        logger.error("README.md not found, skipping stats update.")
        return False

    text = README_PATH.read_text(encoding="utf-8")
    stats_block = _build_stats_block(summary)

    start_tag = "<!-- STATS_START -->"
    end_tag = "<!-- STATS_END -->"

    if start_tag not in text or end_tag not in text:
        logger.error("Stats markers not found in README.md.")
        return False

    new_text = re.sub(
        r"<!-- STATS_START -->[\s\S]*?<!-- STATS_END -->",
        stats_block,
        text,
    )

    README_PATH.write_text(new_text, encoding="utf-8")
    logger.info("Updated README Daily Stats section.")
    return True


def main():
    """Entry point for updating README stats from the last run summary."""
    summary = load_summary()
    if not summary:
        return
    update_readme(summary)


if __name__ == "__main__":
    main()