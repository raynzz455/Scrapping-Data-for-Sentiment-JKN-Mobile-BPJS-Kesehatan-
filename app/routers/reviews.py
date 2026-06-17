"""
Router: /reviews
Query, filter, stats, dan export data ulasan dari Supabase.
"""
import io
import logging
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.db.supabase import get_db
from app.models.review import ReviewListResponse, StatsResponse

router = APIRouter(prefix="/reviews", tags=["Reviews"])
logger = logging.getLogger(__name__)


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db = Depends(get_db)):
    """Statistik ringkas: jumlah per sentimen + rata-rata rating."""
    try:
        res = db.table("reviews").select("sentiment, score").execute()
        rows = res.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not rows:
        return StatsResponse(
            total=0, positif=0, negatif=0, netral=0,
            avg_rating=0.0, pct_positif=0.0, pct_negatif=0.0, pct_netral=0.0,
        )

    total    = len(rows)
    positif  = sum(1 for r in rows if r.get("sentiment") == "positif")
    negatif  = sum(1 for r in rows if r.get("sentiment") == "negatif")
    netral   = sum(1 for r in rows if r.get("sentiment") == "netral")
    scores   = [r["score"] for r in rows if r.get("score")]
    avg_rat  = round(sum(scores) / len(scores), 2) if scores else 0.0

    return StatsResponse(
        total=total,
        positif=positif,
        negatif=negatif,
        netral=netral,
        avg_rating=avg_rat,
        pct_positif=round(positif / total * 100, 1) if total else 0.0,
        pct_negatif=round(negatif / total * 100, 1) if total else 0.0,
        pct_netral=round(netral  / total * 100, 1) if total else 0.0,
    )


@router.get("", response_model=ReviewListResponse)
async def list_reviews(
    sentiment:  Optional[str] = Query(None, description="positif | negatif | netral"),
    score:      Optional[int] = Query(None, ge=1, le=5, description="Filter by bintang"),
    page:       int           = Query(1,    ge=1),
    per_page:   int           = Query(50,   ge=1, le=200),
    db = Depends(get_db),
):
    """
    List ulasan dengan filter opsional sentimen dan rating.
    Mendukung pagination.
    """
    offset = (page - 1) * per_page
    try:
        q = db.table("reviews").select("*", count="exact").order(
            "review_date", desc=True
        ).range(offset, offset + per_page - 1)

        if sentiment:
            q = q.eq("sentiment", sentiment)
        if score:
            q = q.eq("score", score)

        res = q.execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ReviewListResponse(
        data=res.data or [],
        count=res.count or 0,
        page=page,
        per_page=per_page,
    )


@router.get("/export/csv")
async def export_csv(
    sentiment: Optional[str] = Query(None),
    db = Depends(get_db),
):
    """Download semua ulasan sebagai CSV (utf-8-sig agar Excel baca huruf Indonesia)."""
    try:
        q = db.table("reviews").select("*").order("review_date", desc=True)
        if sentiment:
            q = q.eq("sentiment", sentiment)
        res = q.execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    df     = pd.DataFrame(res.data or [])
    buf    = io.StringIO()
    df.to_csv(buf, index=False, encoding="utf-8-sig")
    buf.seek(0)

    filename = f"jkn_reviews_{sentiment or 'all'}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/xlsx")
async def export_xlsx(
    sentiment: Optional[str] = Query(None),
    db = Depends(get_db),
):
    """Download ulasan sebagai Excel dengan 3 sheet (data, ringkasan, tren)."""
    try:
        q = db.table("reviews").select("*").order("review_date", desc=True)
        if sentiment:
            q = q.eq("sentiment", sentiment)
        res = q.execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    df = pd.DataFrame(res.data or [])
    buf = io.BytesIO()

    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # Sheet 1: Data lengkap
        df.to_excel(writer, sheet_name="Ulasan Lengkap", index=False)

        # Sheet 2: Ringkasan sentimen
        if not df.empty and "sentiment" in df.columns:
            counts = df["sentiment"].value_counts().reset_index()
            counts.columns = ["Sentimen", "Jumlah"]
            counts["Persen (%)"] = (counts["Jumlah"] / len(df) * 100).round(2)
            counts.to_excel(writer, sheet_name="Ringkasan", index=False)

        # Sheet 3: Tren bulanan
        if not df.empty and "review_date" in df.columns:
            df["bulan"] = pd.to_datetime(df["review_date"], errors="coerce").dt.to_period("M").astype(str)
            tren = df.groupby(["bulan", "sentiment"]).size().unstack(fill_value=0).reset_index()
            tren.to_excel(writer, sheet_name="Tren Bulanan", index=False)

    buf.seek(0)
    filename = f"jkn_reviews_{sentiment or 'all'}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/monthly-trend")
async def monthly_trend(db = Depends(get_db)):
    """Data tren bulanan per sentimen untuk chart."""
    try:
        res = db.table("reviews").select("review_date, sentiment").execute()
        rows = res.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not rows:
        return []

    df = pd.DataFrame(rows)
    df["bulan"] = pd.to_datetime(df["review_date"], errors="coerce").dt.to_period("M").astype(str)
    tren = (
        df.groupby(["bulan", "sentiment"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    return tren.to_dict("records")
