"""
JKN Sentiment — FastAPI Backend
================================
Endpoints:
  POST /scrape          — trigger scraping + sentiment + simpan ke Supabase
  GET  /scrape/status   — cek jumlah data di DB
  GET  /reviews         — list ulasan (dengan filter & pagination)
  GET  /reviews/stats   — ringkasan statistik sentimen
  GET  /reviews/export/csv   — download CSV
  GET  /reviews/export/xlsx  — download Excel
  GET  /reviews/monthly-trend — data chart tren bulanan
"""
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers import scraper, reviews

load_dotenv()

# ── Logging ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────
app = FastAPI(
    title="JKN Sentiment API",
    description=(
        "Scraper & Sentiment Analyzer untuk ulasan aplikasi Mobile JKN "
        "(BPJS Kesehatan) dari Google Play Store. "
        "Model: IndoBERT fine-tuned (taufiqdp/indonesian-sentiment)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (allow Streamlit dashboard di localhost) ─────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────
app.include_router(scraper.router)
app.include_router(reviews.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "app":     "JKN Sentiment API",
        "version": "1.0.0",
        "docs":    "/docs",
        "status":  "running",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG", "true").lower() == "true",
    )
