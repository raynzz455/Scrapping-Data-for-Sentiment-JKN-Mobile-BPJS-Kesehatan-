"""
JKN Sentiment Dashboard
Neo-brutalism + minimalist header style.
"""
from __future__ import annotations

import os
import time
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

from components.charts import donut_chart, bar_rating, trend_line, horizontal_bar_avg_rating
from components.export import to_csv_bytes, to_xlsx_bytes

load_dotenv()

# ── Detect environment: cek apakah ada Supabase secrets di Streamlit Cloud ──
try:
    IS_HOSTED = "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets
except:
    IS_HOSTED = False

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="JKN Sentiment",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS: Neo-Brutalism ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Space+Mono:wght@400;700&display=swap');

/* ── Root reset ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0A0A0A !important;
    color: #FFFFFF !important;
    font-family: 'Space Grotesk', monospace !important;
}

[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebar"] { background: #111111 !important; border-right: 2px solid #FFFFFF; }
[data-testid="stMainBlockContainer"] { padding: 0 2rem 2rem !important; }

/* ── HEADER ── */
.nb-header {
    border-bottom: 3px solid #FFFFFF;
    padding: 1.2rem 0 1rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: baseline;
    gap: 1rem;
}
.nb-header-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: #FFFFFF;
    text-transform: uppercase;
    margin: 0;
}
.nb-header-sub {
    font-size: 0.75rem;
    color: #666666;
    font-family: 'Space Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.nb-header-badge {
    margin-left: auto;
    background: #00E5A0;
    color: #000000;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 3px 10px;
    border: 2px solid #000000;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── STAT CARDS ── */
.nb-stat {
    background: #111111;
    border: 2px solid #FFFFFF;
    padding: 1.2rem 1.4rem;
    position: relative;
    box-shadow: 4px 4px 0 #FFFFFF;
    transition: box-shadow 0.12s ease, transform 0.12s ease;
}
.nb-stat:hover {
    box-shadow: 6px 6px 0 #FFFFFF;
    transform: translate(-2px, -2px);
}
.nb-stat-label {
    font-size: 0.65rem;
    font-family: 'Space Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #666666;
    margin-bottom: 0.4rem;
}
.nb-stat-value {
    font-family: 'Space Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    line-height: 1;
    color: #FFFFFF;
}
.nb-stat-sub {
    font-size: 0.7rem;
    color: #888888;
    margin-top: 0.3rem;
    font-family: 'Space Mono', monospace;
}
.nb-stat-accent-pos { border-left: 5px solid #00E5A0; }
.nb-stat-accent-neg { border-left: 5px solid #FF3B5C; }
.nb-stat-accent-neu { border-left: 5px solid #FFD600; }
.nb-stat-accent-tot { border-left: 5px solid #FFFFFF; }
.nb-stat-accent-rat { border-left: 5px solid #A78BFA; }

/* ── SECTION LABEL ── */
.nb-section {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #444444;
    border-top: 1px solid #222222;
    padding-top: 0.6rem;
    margin: 1.8rem 0 0.9rem;
}

/* ── CHART CARD ── */
.nb-chart-card {
    background: #111111;
    border: 2px solid #FFFFFF;
    padding: 1.2rem 1.2rem 0.8rem;
    box-shadow: 4px 4px 0 #333333;
    margin-bottom: 0.5rem;
}
.nb-chart-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #AAAAAA;
    margin-bottom: 0.8rem;
    border-bottom: 1px solid #222222;
    padding-bottom: 0.5rem;
}

/* ── REVIEW TABLE ── */
.nb-review-card {
    background: #111111;
    border: 2px solid #222222;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    transition: border-color 0.1s;
}
.nb-review-card:hover { border-color: #FFFFFF; }
.nb-review-card.pos { border-left: 4px solid #00E5A0; }
.nb-review-card.neg { border-left: 4px solid #FF3B5C; }
.nb-review-card.neu { border-left: 4px solid #FFD600; }
.nb-review-user {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #666666;
    margin-bottom: 0.3rem;
}
.nb-review-text { font-size: 0.9rem; color: #DDDDDD; line-height: 1.5; }
.nb-review-meta { font-size: 0.68rem; color: #555555; margin-top: 0.4rem; font-family: 'Space Mono', monospace; }
.nb-sentiment-badge {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 2px 8px;
    border: 1.5px solid;
}
.nb-badge-pos { color: #00E5A0; border-color: #00E5A0; background: rgba(0,229,160,0.08); }
.nb-badge-neg { color: #FF3B5C; border-color: #FF3B5C; background: rgba(255,59,92,0.08); }
.nb-badge-neu { color: #FFD600; border-color: #FFD600; background: rgba(255,214,0,0.08); }

/* ── KEYWORD TAGS ── */
.nb-tag-wrap { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
.nb-tag {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    padding: 4px 10px;
    border: 1.5px solid;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    cursor: default;
}
.nb-tag-pos { color: #00E5A0; border-color: #00E5A0; background: rgba(0,229,160,0.06); }
.nb-tag-neg { color: #FF3B5C; border-color: #FF3B5C; background: rgba(255,59,92,0.06); }

/* ── SCRAPER FORM ── */
div[data-testid="stNumberInput"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stCheckbox"] label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #AAAAAA !important;
}

div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background: #000000 !important;
    border: 2px solid #FFFFFF !important;
    color: #FFFFFF !important;
    border-radius: 0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.9rem !important;
}

div[data-testid="stButton"] button {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 2px solid #FFFFFF !important;
    border-radius: 0 !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-size: 0.75rem !important;
    box-shadow: 4px 4px 0 #444444 !important;
    transition: all 0.1s !important;
    width: 100%;
}
div[data-testid="stButton"] button:hover {
    box-shadow: 2px 2px 0 #444444 !important;
    transform: translate(2px, 2px) !important;
}

/* Select / tabs */
div[data-testid="stSelectbox"] > div > div {
    background: #000000 !important;
    border: 2px solid #FFFFFF !important;
    border-radius: 0 !important;
    color: #FFFFFF !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* Plotly chart bg */
.js-plotly-plot .plotly { background: transparent !important; }
.stPlotlyChart { border: 2px solid #222222 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #111111; }
::-webkit-scrollbar-thumb { background: #333333; }
::-webkit-scrollbar-thumb:hover { background: #555555; }

/* Metric override */
[data-testid="metric-container"] {
    background: #111111 !important;
    border: 2px solid #FFFFFF !important;
    padding: 1rem !important;
    box-shadow: 4px 4px 0 #FFFFFF !important;
}

/* Download button */
div[data-testid="stDownloadButton"] button {
    background: #000000 !important;
    color: #00E5A0 !important;
    border: 2px solid #00E5A0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    border-radius: 0 !important;
    box-shadow: 3px 3px 0 #00E5A0 !important;
    width: 100%;
}

div[data-testid="stAlert"] {
    border-radius: 0 !important;
    border: 2px solid !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────

def api_get(path: str, params: dict | None = None) -> dict | list | None:
    if not IS_HOSTED:
        try:
            r = requests.get(f"{API_BASE}{path}", params=params, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            st.error(f"API error ({path}): {e}")
            return None
    else:
        return fetch_supabase(path, params)

def fetch_supabase(path: str, params: dict | None = None) -> dict | list | None:
    try:
        sb = get_supabase()

        if path == "/reviews/stats":
            res_all = sb.table("reviews").select("*", count="exact").execute()
            total = res_all.count or 0
            if total == 0: return None

            res_pos = sb.table("reviews").select("*", count="exact").eq("sentiment", "positif").execute()
            res_neg = sb.table("reviews").select("*", count="exact").eq("sentiment", "negatif").execute()
            res_neu = sb.table("reviews").select("*", count="exact").eq("sentiment", "netral").execute()

            pos, neg, neu = (res_pos.count or 0), (res_neg.count or 0), (res_neu.count or 0)

            res_rating = sb.table("reviews").select("score").order("review_date", desc=True).limit(1000).execute()
            df_r = pd.DataFrame(res_rating.data)
            df_r = df_r[df_r["score"] > 0]
            avg_rating = df_r["score"].mean() if not df_r.empty else 0.0

            return {
                "total": total, "positif": pos, "negatif": neg, "netral": neu,
                "pct_positif": round((pos/total)*100, 1) if total else 0,
                "pct_negatif": round((neg/total)*100, 1) if total else 0,
                "pct_netral": round((neu/total)*100, 1) if total else 0,
                "avg_rating": round(avg_rating, 2)
            }

        elif path == "/reviews/monthly-trend":
            res = sb.table("reviews").select("review_date, sentiment").execute()
            df = pd.DataFrame(res.data)
            if df.empty: return []

            df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')
            df = df.dropna(subset=['review_date'])
            df['bulan'] = df['review_date'].dt.strftime('%Y-%m')

            trend_df = df.groupby(['bulan', 'sentiment']).size().unstack(fill_value=0).reset_index()
            return trend_df.to_dict(orient="records")

        elif path == "/reviews":
            query = sb.table("reviews").select("*", count="exact")
            if params:
                if params.get("sentiment"):
                    query = query.eq("sentiment", params["sentiment"])
                if params.get("score"):
                    query = query.eq("score", params["score"])

                page = params.get("page", 1)
                per_page = params.get("per_page", 50)
                start = (page - 1) * per_page
                end = start + per_page - 1
                res = query.order("review_date", desc=True).range(start, end).execute()
            else:
                res = query.order("review_date", desc=True).limit(50).execute()

            return {"data": res.data, "count": res.count}

        elif path == "/scrape/status":
            res = sb.table("reviews").select("*", count="exact").execute()
            return {"total_in_db": res.count or 0}

        return None

    except Exception as e:
        st.error(f"Supabase error: {e}")
        return None


def api_post(path: str, body: dict) -> dict | None:
    try:
        r = requests.post(f"{API_BASE}{path}", json=body, timeout=300)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error POST ({path}): {e}")
        return None


def sentiment_badge(s: str | None) -> str:
    if s == "positif":
        return '<span class="nb-sentiment-badge nb-badge-pos">✓ positif</span>'
    if s == "negatif":
        return '<span class="nb-sentiment-badge nb-badge-neg">✗ negatif</span>'
    return '<span class="nb-sentiment-badge nb-badge-neu">~ netral</span>'


def star_str(score: int | None) -> str:
    if not score:
        return "—"
    return "★" * int(score) + "☆" * (5 - int(score))


# ── HEADER ───────────────────────────────────────────────
env_badge = "☁️ STREAMLIT CLOUD" if IS_HOSTED else "💻 LOCAL"
st.markdown(f"""
<div class="nb-header">
    <div>
        <div class="nb-header-title">🏥 JKN Sentiment</div>
        <div class="nb-header-sub">Mobile JKN — BPJS Kesehatan · Analisis Ulasan Google Play</div>
    </div>
    <div style="display: flex; gap: 0.5rem;">
        <div class="nb-header-badge">{env_badge}</div>
        <div class="nb-header-badge">IndoBERT</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────────
tab_dash, tab_scrape, tab_data = st.tabs(["DASHBOARD", "SCRAPER", "DATA & EXPORT"])

# ════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ════════════════════════════════════════════════════════════
with tab_dash:
    stats = api_get("/reviews/stats")
    trend = api_get("/reviews/monthly-trend")

    if stats:
        # ── Stat cards ──
        c1, c2, c3, c4, c5 = st.columns(5)
        cards = [
            (c1, "Total Ulasan",    stats["total"],    f"di database", "nb-stat-accent-tot", ""),
            (c2, "Positif",         stats["positif"],  f"{stats['pct_positif']}% dari total", "nb-stat-accent-pos", ""),
            (c3, "Negatif",         stats["negatif"],  f"{stats['pct_negatif']}% dari total", "nb-stat-accent-neg", ""),
            (c4, "Netral",          stats["netral"],   f"{stats['pct_netral']}% dari total",  "nb-stat-accent-neu", ""),
            (c5, "Avg Rating",      f"{stats['avg_rating']:.1f}",  "dari skala 5.0",          "nb-stat-accent-rat", ""),
        ]
        for col, label, val, sub, cls, _ in cards:
            with col:
                st.markdown(f"""
                <div class="nb-stat {cls}">
                    <div class="nb-stat-label">{label}</div>
                    <div class="nb-stat-value">{val}</div>
                    <div class="nb-stat-sub">{sub}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("")  # spacer

    # ── Charts row 1 ──
    st.markdown('<div class="nb-section">Distribusi Sentimen</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1.8])

    with col_a:
        st.markdown('<div class="nb-chart-card"><div class="nb-chart-title">Proporsi Sentimen</div>', unsafe_allow_html=True)
        if stats:
            st.plotly_chart(
                donut_chart(stats["positif"], stats["netral"], stats["negatif"]),
                use_container_width=True, config={"displayModeBar": False},
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="nb-chart-card"><div class="nb-chart-title">Tren Sentimen Bulanan</div>', unsafe_allow_html=True)
        if trend:
            st.plotly_chart(
                trend_line(trend),
                use_container_width=True, config={"displayModeBar": False},
            )
        elif not trend:
            st.caption("Belum ada data tren. Jalankan scraping terlebih dahulu.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Charts row 2 ──
    st.markdown('<div class="nb-section">Analisis Rating</div>', unsafe_allow_html=True)
    col_c, col_d = st.columns(2)

    # Ambil sampel data untuk charts
    reviews_sample = api_get("/reviews", params={"per_page": 200})
    df_sample = pd.DataFrame(reviews_sample["data"] if reviews_sample else [])

    with col_c:
        st.markdown('<div class="nb-chart-card"><div class="nb-chart-title">Distribusi Rating Bintang</div>', unsafe_allow_html=True)
        if not df_sample.empty and "score" in df_sample.columns:
            st.plotly_chart(bar_rating(df_sample), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_d:
        st.markdown('<div class="nb-chart-card"><div class="nb-chart-title">Rata-rata Rating per Sentimen</div>', unsafe_allow_html=True)
        if not df_sample.empty:
            st.plotly_chart(horizontal_bar_avg_rating(df_sample), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Keyword tags ──
    st.markdown('<div class="nb-section">Topik Ulasan</div>', unsafe_allow_html=True)
    col_kw1, col_kw2 = st.columns(2)

    POS_KEYWORDS = ["antrian online", "membantu", "mudah digunakan", "praktis",
                    "cek tagihan", "ganti faskes", "kartu digital", "ringan",
                    "update bagus", "user friendly", "notifikasi", "responsif"]
    NEG_KEYWORDS = ["error", "tidak bisa login", "OTP gagal", "force close",
                    "server down", "loading lama", "tidak berfungsi", "mengecewakan",
                    "bug", "verifikasi wajah", "tidak dibalas", "data hilang"]

    with col_kw1:
        tags_pos = "".join([f'<span class="nb-tag nb-tag-pos">{k}</span>' for k in POS_KEYWORDS])
        st.markdown(f"""
        <div class="nb-chart-card">
            <div class="nb-chart-title">✓ Kata kunci — Positif</div>
            <div class="nb-tag-wrap">{tags_pos}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_kw2:
        tags_neg = "".join([f'<span class="nb-tag nb-tag-neg">{k}</span>' for k in NEG_KEYWORDS])
        st.markdown(f"""
        <div class="nb-chart-card">
            <div class="nb-chart-title">✗ Kata kunci — Negatif</div>
            <div class="nb-tag-wrap">{tags_neg}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Sample reviews ──
    st.markdown('<div class="nb-section">Ulasan Terpilih</div>', unsafe_allow_html=True)

    filter_sent = st.selectbox(
        "Filter sentimen",
        options=["semua", "positif", "negatif", "netral"],
        label_visibility="collapsed",
    )

    q_params: dict = {"per_page": 10}
    if filter_sent != "semua":
        q_params["sentiment"] = filter_sent

    rev_data = api_get("/reviews", params=q_params)

    if rev_data and rev_data.get("data"):
        for r in rev_data["data"]:
            s = r.get("sentiment", "netral") or "netral"
            cls = "pos" if s == "positif" else ("neg" if s == "negatif" else "neu")
            st.markdown(f"""
            <div class="nb-review-card {cls}">
                <div class="nb-review-user">{r.get('user_name','—')} · {r.get('app_version','')}</div>
                <div class="nb-review-text">{r.get('content','(kosong)')}</div>
                <div class="nb-review-meta">
                    {star_str(r.get('score'))}
                    &nbsp;·&nbsp; {r.get('review_date','—')}
                    &nbsp;·&nbsp; 👍 {r.get('thumbs_up', 0)}
                    &nbsp;&nbsp; {sentiment_badge(r.get('sentiment'))}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Belum ada ulasan. Jalankan scraping di tab SCRAPER.")


# ════════════════════════════════════════════════════════════
# TAB 2 — SCRAPER
# ════════════════════════════════════════════════════════════
with tab_scrape:
    st.markdown('<div class="nb-section">Konfigurasi Scraping</div>', unsafe_allow_html=True)

    col_f1, col_f2 = st.columns([2, 1])

    with col_f1:
        app_id  = st.text_input("App ID Google Play", value="app.bpjs.mobile")
        count   = st.number_input("Jumlah ulasan", min_value=50, max_value=5000, value=500, step=50)
        run_sentiment = st.checkbox("Jalankan analisis sentimen", value=True)

    with col_f2:
        st.markdown("<br>", unsafe_allow_html=True)
        status = api_get("/scrape/status")
        if status:
            st.markdown(f"""
            <div class="nb-stat nb-stat-accent-tot" style="margin-bottom:1rem">
                <div class="nb-stat-label">Data di DB</div>
                <div class="nb-stat-value" style="font-size:1.6rem">{status.get('total_in_db', 0)}</div>
                <div class="nb-stat-sub">ulasan tersimpan</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")
    run_btn = st.button("▶ JALANKAN SCRAPING", use_container_width=True)

    if run_btn:
        with st.spinner("Scraping + sentiment analysis berjalan... (bisa 5–10 menit)"):
            result = api_post("/scrape", {
                "app_id":         app_id,
                "count":          count,
                "lang":           "id",
                "country":        "id",
                "run_sentiment":  run_sentiment,
            })
        if result and result.get("status") == "success":
            st.success(result["message"])
            dist = result.get("sentiment_dist", {})
            c1, c2, c3 = st.columns(3)
            for col, key, color in [(c1, "positif", "00E5A0"), (c2, "negatif", "FF3B5C"), (c3, "netral", "FFD600")]:
                with col:
                    st.markdown(f"""
                    <div class="nb-stat" style="border-left: 5px solid #{color}">
                        <div class="nb-stat-label">{key}</div>
                        <div class="nb-stat-value" style="color:#{color}">{dist.get(key, 0)}</div>
                    </div>
                    """, unsafe_allow_html=True)
        elif result:
            st.error(f"Gagal: {result}")

    st.markdown('<div class="nb-section">Catatan Penggunaan</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family: 'Space Mono', monospace; font-size: 0.75rem; color: #666666; line-height: 1.8; border: 1px solid #222222; padding: 1rem;">
    • Google Play memblokir request dari IP server/cloud (403) — scraping harus dijalankan dari laptop lokal<br>
    • Model IndoBERT (~450MB) didownload otomatis pertama kali dari HuggingFace, lalu dicache<br>
    • Estimasi waktu: ~2 menit per 500 ulasan (termasuk sentiment analysis, CPU)<br>
    • Duplikat difilter otomatis via upsert (user_name + review_date)
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TAB 3 — DATA & EXPORT
# ════════════════════════════════════════════════════════════
with tab_data:
    st.markdown('<div class="nb-section">Tabel Data Ulasan</div>', unsafe_allow_html=True)

    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        flt_sent = st.selectbox("Sentimen", ["semua", "positif", "negatif", "netral"], key="dt_sent")
    with col_e2:
        flt_score = st.selectbox("Rating", ["semua", "1", "2", "3", "4", "5"], key="dt_score")
    with col_e3:
        flt_page = st.number_input("Halaman", min_value=1, value=1, key="dt_page")

    dt_params: dict = {"page": flt_page, "per_page": 50}
    if flt_sent != "semua":
        dt_params["sentiment"] = flt_sent
    if flt_score != "semua":
        dt_params["score"] = int(flt_score)

    dt_data = api_get("/reviews", params=dt_params)

    if dt_data and dt_data.get("data"):
        df_show = pd.DataFrame(dt_data["data"])
        display_cols = [c for c in ["user_name", "content", "score", "sentiment", "review_date", "thumbs_up", "app_version"] if c in df_show.columns]
        st.dataframe(
            df_show[display_cols],
            use_container_width=True,
            height=400,
        )
        st.caption(f"Menampilkan {len(df_show)} dari {dt_data.get('count', '?')} total ulasan")
    else:
        st.info("Belum ada data. Jalankan scraping terlebih dahulu.")

    # ── Export ──
    st.markdown('<div class="nb-section">Export Data</div>', unsafe_allow_html=True)

    exp_sent = st.selectbox("Filter sentimen untuk export", ["semua", "positif", "negatif", "netral"], key="exp_sent")
    exp_sent_val = None if exp_sent == "semua" else exp_sent

    # Fetch full data for export
    if st.button("📥 GENERATE FILE EXPORT", use_container_width=True):
        with st.spinner("Mengambil semua data..."):
            full_data = api_get("/reviews", params={"per_page": 5000, **({"sentiment": exp_sent_val} if exp_sent_val else {})})

        if full_data and full_data.get("data"):
            df_exp = pd.DataFrame(full_data["data"])
            st.session_state["df_export"] = df_exp
            st.success(f"{len(df_exp)} ulasan siap diexport.")

    if "df_export" in st.session_state:
        df_exp = st.session_state["df_export"]
        col_dl1, col_dl2 = st.columns(2)

        with col_dl1:
            st.download_button(
                label="⬇ DOWNLOAD CSV",
                data=to_csv_bytes(df_exp),
                file_name=f"jkn_reviews_{exp_sent}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_dl2:
            st.download_button(
                label="⬇ DOWNLOAD EXCEL (.xlsx)",
                data=to_xlsx_bytes(df_exp),
                file_name=f"jkn_reviews_{exp_sent}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
