"""
Router: /scrape
Trigger scraping + sentiment analysis + simpan ke Supabase.
"""
import time
import logging
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from app.db.supabase import get_db
from app.models.review import ScrapeRequest, ScrapeResponse
from app.services.scraper import scrape_reviews
from app.services.sentiment import predict_sentiment

router = APIRouter(prefix="/scrape", tags=["Scraping"])
logger = logging.getLogger(__name__)


@router.post("", response_model=ScrapeResponse)
async def trigger_scrape(
    req:  ScrapeRequest,
    db    = Depends(get_db),
):
    """
    Jalankan scraping ulasan Google Play Store,
    analisis sentimen, dan simpan ke Supabase.
    """
    start_time = time.time()

    # 1. Scraping
    try:
        raw = scrape_reviews(
            app_id=req.app_id,
            count=req.count,
            lang=req.lang,
            country=req.country,
        )
    except Exception as e:
        logger.error(f"Scraping gagal: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping error: {e}")

    if not raw:
        raise HTTPException(
            status_code=404,
            detail="Tidak ada ulasan ditemukan. Cek app_id atau koneksi internet.",
        )

    # 2. Sentiment Analysis
    if req.run_sentiment:
        try:
            raw = predict_sentiment(raw)
        except Exception as e:
            logger.warning(f"Sentiment analysis gagal, skip: {e}")
            for r in raw:
                r.setdefault("sentiment", None)
                r.setdefault("sentiment_bin", None)

    # 3. Simpan ke Supabase (upsert by user_name + review_date untuk avoid duplikat)
    saved = 0
    CHUNK = 100  # insert per batch
    for i in range(0, len(raw), CHUNK):
        chunk = raw[i:i + CHUNK]
        try:
            db.table("reviews").upsert(
                chunk,
                on_conflict="user_name,review_date",
            ).execute()
            saved += len(chunk)
        except Exception as e:
            logger.error(f"Gagal insert chunk {i}–{i+CHUNK}: {e}")

    # 4. Summary
    dist     = Counter(r.get("sentiment") for r in raw if r.get("sentiment"))
    duration = round(time.time() - start_time, 2)

    return ScrapeResponse(
        status="success",
        total_scraped=len(raw),
        total_saved=saved,
        sentiment_dist=dict(dist),
        duration_seconds=duration,
        message=f"Berhasil scraping {len(raw)} ulasan, disimpan {saved} ke Supabase dalam {duration}s.",
    )


@router.get("/status")
async def scrape_status(db = Depends(get_db)):
    """Cek jumlah total ulasan yang sudah ada di database."""
    try:
        res = db.table("reviews").select("id", count="exact").execute()
        return {
            "total_in_db": res.count,
            "status": "ok",
            "db": "supabase",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
