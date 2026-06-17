"""
Pydantic models untuk request / response API dan validasi data.
"""
from __future__ import annotations
from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


SentimentLabel = Literal["positif", "netral", "negatif"]
SentimentBinary = Literal["positif", "negatif/netral"]


class ReviewBase(BaseModel):
    user_name:     Optional[str]  = None
    content:       Optional[str]  = None
    score:         Optional[int]  = Field(None, ge=1, le=5)
    thumbs_up:     int            = 0
    review_date:   Optional[date] = None
    app_version:   Optional[str]  = None
    reply_content: Optional[str]  = None
    reply_date:    Optional[date] = None


class ReviewCreate(ReviewBase):
    sentiment:     Optional[SentimentLabel]  = None
    sentiment_bin: Optional[SentimentBinary] = None


class ReviewOut(ReviewCreate):
    id:         int
    scraped_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Request / Response ────────────────────────────────────

class ScrapeRequest(BaseModel):
    count:   int  = Field(500, ge=10, le=5000, description="Jumlah ulasan yang diambil")
    app_id:  str  = Field("app.bpjs.mobile", description="App ID Google Play")
    lang:    str  = "id"
    country: str  = "id"
    run_sentiment: bool = True


class ScrapeResponse(BaseModel):
    status:      str
    total_scraped:     int
    total_saved:       int
    sentiment_dist:    dict[str, int]
    duration_seconds:  float
    message:           str


class StatsResponse(BaseModel):
    total:       int
    positif:     int
    negatif:     int
    netral:      int
    avg_rating:  float
    pct_positif: float
    pct_negatif: float
    pct_netral:  float


class ReviewListResponse(BaseModel):
    data:    list[ReviewOut]
    count:   int
    page:    int
    per_page: int
