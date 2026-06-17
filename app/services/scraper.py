"""
Service: scraping ulasan Google Play Store.
Menggunakan google-play-scraper dengan auto-pagination.
"""
import os
import time
import logging
from datetime import datetime
from typing import Optional

from tqdm import tqdm

logger = logging.getLogger(__name__)


def scrape_reviews(
    app_id: str  = None,
    count:  int  = 500,
    lang:   str  = "id",
    country: str = "id",
) -> list[dict]:
    """
    Ambil ulasan dari Google Play Store.

    Returns list of dict dengan keys:
      user_name, content, score, thumbs_up,
      review_date, app_version, reply_content, reply_date
    """
    try:
        from google_play_scraper import reviews, Sort
    except ImportError:
        raise ImportError("Jalankan: uv add google-play-scraper")

    app_id  = app_id or os.getenv("APP_ID", "app.bpjs.mobile")
    results: list[dict] = []
    token: Optional[str] = None
    page_size = 200  # Google Play max per request
    fetched   = 0

    logger.info(f"Mulai scraping {app_id} | target={count} | lang={lang} | country={country}")

    with tqdm(total=count, desc="📥 Scraping reviews", unit="ulasan") as pbar:
        while fetched < count:
            batch = min(page_size, count - fetched)
            try:
                batch_results, token = reviews(
                    app_id,
                    lang=lang,
                    country=country,
                    sort=Sort.NEWEST,
                    count=batch,
                    continuation_token=token,
                )
            except Exception as e:
                logger.error(f"Error saat fetch batch: {e}")
                break

            if not batch_results:
                logger.info("Tidak ada ulasan lagi di Play Store.")
                break

            for r in batch_results:
                results.append({
                    "user_name":     r.get("userName") or "",
                    "content":       r.get("content")  or "",
                    "score":         int(r.get("score", 0)),
                    "thumbs_up":     int(r.get("thumbsUpCount", 0)),
                    "review_date":   _parse_date(r.get("at")),
                    "app_version":   r.get("appVersion") or "",
                    "reply_content": r.get("replyContent") or "",
                    "reply_date":    _parse_date(r.get("repliedAt")),
                })

            fetched += len(batch_results)
            pbar.update(len(batch_results))

            if token is None:
                break

            time.sleep(0.4)  # rate limit prevention

    logger.info(f"Selesai scraping: {len(results)} ulasan")
    return results


def _parse_date(value) -> Optional[str]:
    """Convert datetime obj atau string ke ISO date string."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, str) and value:
        return value[:10]
    return None
