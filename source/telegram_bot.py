import os
import requests

from source.logger import get_logger

logger = get_logger()

TELEGRAM_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram_message(text: str):
    """
    Send a plain-text Telegram message using the bot API.
    Silently no-ops if no token or chat_id is configured.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.info(
            "Telegram disabled (missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID)."
        )
        return

    url = TELEGRAM_URL.format(token=token)
    payload = {"chat_id": chat_id, "text": text}

    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        logger.info("Telegram message sent.")
    except Exception as e:
        logger.warning(f"Failed to send Telegram message: {e}")