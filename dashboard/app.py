"""
JKN Sentiment Dashboard — Pure Supabase Version
Neo-brutalism + minimalist header style.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
from supabase import create_client

from components.charts import donut_chart, bar_rating, trend_line, horizontal_bar_avg_rating
from components.export import to_csv_bytes, to_xlsx_bytes

@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="JKN Sentiment",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS: Neo-Brutalism ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Space+Mono:wght@400;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0A0A0A !important;
    color: #FFFFFF !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebar"] { background: #111111 !important; border-right: 2px solid #FFFFFF; }
[data-testid="stMainBlockContainer"] { padding: 0 2rem 2rem !important; }

.nb-header { border-bottom: 3px solid #FFFFFF; padding: 1.2rem 0 1rem; margin-bottom: 2rem; display: flex; align-items: baseline; gap: 1rem; }
.nb-header-title { font-family: 'Space Mono', monospace; font-size: 1.15rem; font-weight: 700; letter-spacing: 0.04em; color: #FFFFFF; text-transform: uppercase; margin: 0; }
.nb-header-sub { font-size: 0.75rem; color: #666666; font-family: 'Space Mono', monospace; text-transform: uppercase; letter-spacing: 0.08em; }
.nb-header-badge { margin-left: auto; background: #00E5A0; color: #000000; font-family: 'Space Mono', monospace; font-size: 0.65rem; font-weight: 700; padding: 3px 10px; border: 2px solid #000000; text-transform: uppercase; letter-spacing: 0.06em; }

.nb-stat { background: #111111; border: 2px solid #FFFFFF; padding: 1.2rem 1.4rem; position: relative; box-shadow: 4px 4px 0 #FFFFFF; transition: box-shadow 0.12s ease, transform 0.12s ease; }
.nb-stat:hover { box-shadow: 6px 6px 0 #FFFFFF; transform: translate(-2px, -2px); }
.nb-stat-label { font-size: 0.65rem; font-family: 'Space Mono', monospace; text-transform: uppercase; letter-spacing: 0.1em; color: #666666; margin-bottom: 0.4rem; }
.nb-stat-value { font-family: 'Space Mono', monospace; font-size: 2.4rem; font-weight: 700; line-height: 1; color: #FFFFFF; }
.nb-stat-sub { font-size: 0.7rem; color: #888888; margin-top: 0.3rem; font-family: 'Space Mono', monospace; }
.nb-stat-accent-pos { border-left: 5px solid #00E5A0; }
.nb-stat-accent-neg { border-left: 5px solid #FF3B5C; }
.nb-stat-accent-neu { border-left: 5px solid #FFD600; }
.nb-stat-accent-tot { border-left: 5px solid #FFFFFF; }
.nb-stat-accent-rat { border-left: 5px solid #A78BFA; }

.nb-section { font-family: 'Space Mono', monospace; font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.15em; color: #444444; border-top: 1px solid #222222; padding-top: 0.6rem; margin: 1.8rem 0 0.9rem; }
.nb-chart-card { background: #111111; border: 2px solid #FFFFFF; padding: 1.2rem 1.2rem 0.8rem; box-shadow: 4px 4px 0 #333333; margin-bottom: 0.5rem; }
.nb-chart-title { font-family: 'Space Mono', monospace; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em; color: #AAAAAA; margin-bottom: 0.8rem; border-bottom: 1px solid #222222; padding-bottom: 0.5rem; }

.nb-review-card { background: #111111; border: 2px solid #222222; padding: 0.9rem 1.1rem; margin-bottom: 0.6rem; transition: border-color 0.1s; }
.nb-review-card:hover { border-color: #FFFFFF; }
.nb-review-card.pos { border-left: 4px solid #00E5A0; }
.nb-review-card.neg { border-left: 4px solid #FF3B5C; }
.nb-review-card.neu { border-left: 4px solid #FFD600; }
.nb-review-user { font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #666666; margin-bottom: 0.3rem; }
.nb-review-text { font-size: 0.9rem; color: #DDDDDD; line-height: 1.5; }
.nb-review-meta { font-size: 0.68rem; color: #555555; margin-top: 0.4rem; font-family: 'Space Mono', monospace; }
.nb-sentiment-badge { display: inline-block; font-family: 'Space Mono', monospace; font-size: 0.6rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 2px 8px; border: 1.5px solid; }
.nb-badge-pos { color: #00E5A0; border-color: #00E5A0; background: rgba(0,229,160,0.08); }
.nb-badge-neg { color: #FF3B5C; border-color: #FF3B5C; background: rgba(255,59,92,0.08); }
.nb-badge-neu { color: #FFD600; border-color: #FFD600; background: rgba(255,214,0,0.08); }

.nb-tag-wrap { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
.nb-tag { font-family: 'Space Mono', monospace; font-size: 0.65rem; padding: 4px 10px; border: 1.5px solid; text-transform: uppercase; letter-spacing: 0.05em; cursor: default; }
.nb-tag-pos { color: #00E5A0; border-color: #00E5A0; background: rgba(0,229,160,0.06); }
.nb-tag-neg { color: #FF3B5C; border-color: #FF3B5C; background: rgba(255,59,92,0.06); }

div[data-testid="stNumberInput"] label, div[data-testid="stTextInput"] label { font-family: 'Space Mono', monospace !important; font-size: 0.7rem !important; text-transform: uppercase !important; }
div[data-testid="stNumberInput"] input, div[data-testid="stTextInput"] input { background: #000000 !important; border: 2px solid #FFFFFF !important; color: #FFFFFF !important; border-radius: 0 !important; }
div[data-testid="stButton"] button { background: #FFFFFF !important; color: #000000 !important; border: 2px solid #FFFFFF !important; font-family: 'Space Mono', monospace !important; font-weight: 700 !important; text-transform: uppercase !important; box-shadow: 4px 4px 0 #444444 !important; }
div[data-testid="stSelectbox"] > div > div { background: #000000 !important; border: 2px solid #FFFFFF !important; color: #FFFFFF !important; }
.stPlotlyChart { border: 2px solid #222222 !important; }
[data-testid="metric-container"] { background: #111111 !important; border: 2px solid #FFFFFF !important; box-shadow: 4px 4px 0 #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# ── DATA FETCHERS ─────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_stats() -> dict | None:
    try:
        sb = get_supabase()
        res_all = sb.table("reviews").select("*", count="exact").execute()
        total = res_all.count or 0
        if total == 0: return None

        res_pos = sb.table("reviews").select("*", count="exact").eq("sentiment", "positif").execute()
        res_neg = sb.table("reviews").select("*", count="exact").eq("sentiment", "negatif").execute()
        res_neu = sb.table("reviews").select("*", count="exact").eq("sentiment", "netral").execute()

        pos, neg, neu = (res_pos.count or 0), (res_neg.count or 0), (res_neu.count or 0)

        res_rating = sb.table("reviews").select("score").execute()
        df_r = pd.DataFrame(res_rating.data)
        avg_rating = df_r["score"].mean() if not df_r.empty else 0.0

        return {
            "total": total, "positif": pos, "negatif": neg, "netral": neu,
            "pct_positif": round((pos/total)*100, 1) if total else 0,
            "pct_negatif": round((neg/total)*100, 1) if total else 0,
            "pct_netral": round((neu/total)*100, 1) if total else 0,
            "avg_rating": round(avg_rating, 2)
        }
    except Exception as e:
        st.error(f"Error loading stats: {e}")
        return None

@st.cache_data(ttl=600, show_spinner=False)
def fetch_trend() -> list | None:
    try:
        sb = get_supabase()
        res = sb.table("reviews").select("review_date, sentiment").execute()
        df = pd.DataFrame(res.data)
        if df.empty: return []

        df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')
        df = df.dropna(subset=['review_date'])
        df['month'] = df['review_date'].dt.strftime('%Y-%m')

        trend_df = df.groupby(['month', 'sentiment']).size().unstack(fill_value=0).reset_index()
        return trend_df.to_dict(orient="records")
    except Exception as e:
        st.error(f"Error loading trend: {e}")
        return None

@st.cache_data(ttl=120, show_spinner=False)
def fetch_reviews(sentiment: str | None = None, score: int | None = None,
                  page: int = 1, per_page: int = 50) -> dict | None:
    try:
        sb = get_supabase()
        query = sb.table("reviews").select("*", count="exact")
        if sentiment:
            query = query.eq("sentiment", sentiment)
        if score:
            query = query.eq("score", score)

        start = (page - 1) * per_page
        end = start + per_page - 1
        res = query.order("review_date", descending=True).range(start, end).execute()

        return {"data": res.data, "count": res.count}
    except Exception as e:
        st.error(f"Error loading reviews: {e}")
        return None

@st.cache_data(ttl=300, show_spinner=False)
def fetch_scrape_status() -> dict | None:
    try:
        sb = get_supabase()
        res = sb.table("reviews").select("*", count="exact").execute()
        return {"total_in_db": res.count or 0}
    except:
        return {"total_in_db": 0}

def sentiment_badge(s: str | None) -> str:
    if s == "positif": return '<span class="nb-sentiment-badge nb-badge-pos">✓ positif</span>'
    if s == "negatif": return '<span class="nb-sentiment-badge nb-badge-neg">✗ negatif</span>'
    return '<span class="nb-sentiment-badge nb-badge-neu">~ netral</span>'

def star_str(score: int | None) -> str:
    if not score: return "—"
    return "★" * int(score) + "☆" * (5 - int(score))

# ── HEADER ────────────────────────────────────────────────
st.markdown("""
<div class="nb-header">
    <div>
        <div class="nb-header-title">🏥 JKN Sentiment</div>
        <div class="nb-header-sub">Mobile JKN — BPJS Kesehatan · Analisis Ulasan Google Play</div>
    </div>
    <div class="nb-header-badge">IndoBERT</div>
</div>
""", unsafe_allow_html=True)

tab_dash, tab_data = st.tabs(["DASHBOARD", "DATA & EXPORT"])

# ════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ════════════════════════════════════════════════════════════
with tab_dash:
    @st.fragment(run_every=300)
    def _stat_cards():
        stats = fetch_stats()
        if not stats:
            st.warning("Belum ada data di database.")
            return
        c1, c2, c3, c4, c5 = st.columns(5)
        cards = [
            (c1, "Total Ulasan", stats["total"], "di database", "nb-stat-accent-tot"),
            (c2, "Positif", stats["positif"], f"{stats['pct_positif']}%", "nb-stat-accent-pos"),
            (c3, "Negatif", stats["negatif"], f"{stats['pct_negatif']}%", "nb-stat-accent-neg"),
            (c4, "Netral", stats["netral"], f"{stats['pct_netral']}%", "nb-stat-accent-neu"),
            (c5, "Avg Rating", f"{stats['avg_rating']:.1f}", "dari 5.0", "nb-stat-accent-rat"),
        ]
        for col, label, val, sub, cls in cards:
            with col:
                st.markdown(f"""
                <div class="nb-stat {cls}">
                    <div class="nb-stat-label">{label}</div>
                    <div class="nb-stat-value">{val}</div>
                    <div class="nb-stat-sub">{sub}</div>
                </div>
                """, unsafe_allow_html=True)

    @st.fragment
    def _chart_donut():
        stats = fetch_stats()
        st.markdown('<div class="nb-chart-card"><div class="nb-chart-title">Proporsi Sentimen</div>', unsafe_allow_html=True)
        if stats:
            st.plotly_chart(donut_chart(stats["positif"], stats["netral"], stats["negatif"]), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    @st.fragment
    def _chart_trend():
        trend = fetch_trend()
        st.markdown('<div class="nb-chart-card"><div class="nb-chart-title">Tren Sentimen Bulanan</div>', unsafe_allow_html=True)
        if trend:
            st.plotly_chart(trend_line(trend), use_container_width=True, config={"displayModeBar": False})
        else:
            st.caption("Belum ada data tren.")
        st.markdown("</div>", unsafe_allow_html=True)

    @st.fragment
    def _chart_ratings():
        reviews_sample = fetch_reviews(per_page=150)
        df_sample = pd.DataFrame(reviews_sample["data"] if reviews_sample else [])
        st.markdown('<div class="nb-section">Analisis Rating</div>', unsafe_allow_html=True)
        col_c, col_d = st.columns(2)
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

    _stat_cards()
    st.markdown('<div class="nb-section">Distribusi Sentimen</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1.8])
    with col_a: _chart_donut()
    with col_b: _chart_trend()
    _chart_ratings()

    st.markdown('<div class="nb-section">Topik Ulasan</div>', unsafe_allow_html=True)
    col_kw1, col_kw2 = st.columns(2)
    POS_KEYWORDS = ["antrian online", "membantu", "mudah digunakan", "praktis", "cek tagihan", "ganti faskes"]
    NEG_KEYWORDS = ["error", "tidak bisa login", "OTP gagal", "force close", "server down", "loading lama"]

    with col_kw1:
        tags_pos = "".join([f'<span class="nb-tag nb-tag-pos">{k}</span>' for k in POS_KEYWORDS])
        st.markdown(f'<div class="nb-chart-card"><div class="nb-chart-title">✓ Positif</div><div class="nb-tag-wrap">{tags_pos}</div></div>', unsafe_allow_html=True)
    with col_kw2:
        tags_neg = "".join([f'<span class="nb-tag nb-tag-neg">{k}</span>' for k in NEG_KEYWORDS])
        st.markdown(f'<div class="nb-chart-card"><div class="nb-chart-title">✗ Negatif</div><div class="nb-tag-wrap">{tags_neg}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="nb-section">Ulasan Terpilih</div>', unsafe_allow_html=True)
    with st.form("review_filter_form"):
        filter_sent = st.selectbox("Filter sentimen", options=["semua", "positif", "negatif", "netral"], label_visibility="collapsed")
        st.form_submit_button("🔍 Tampilkan Ulasan", use_container_width=True)

    active_sent = filter_sent if filter_sent != "semua" else None
    rev_data = fetch_reviews(sentiment=active_sent, per_page=10)

    if rev_data and rev_data.get("data"):
        for r in rev_data["data"]:
            s = r.get("sentiment", "netral") or "netral"
            cls = "pos" if s == "positif" else ("neg" if s == "negatif" else "neu")
            st.markdown(f"""
            <div class="nb-review-card {cls}">
                <div class="nb-review-user">{r.get('user_name','—')} · {r.get('app_version','')}</div>
                <div class="nb-review-text">{r.get('content','(kosong)')}</div>
                <div class="nb-review-meta">
                    {star_str(r.get('score'))} · {r.get('review_date','—')} · 👍 {r.get('thumbs_up', 0)} &nbsp;&nbsp; {sentiment_badge(r.get('sentiment'))}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — DATA & EXPORT
# ════════════════════════════════════════════════════════════
with tab_data:
    st.markdown('<div class="nb-section">Tabel Data Ulasan</div>', unsafe_allow_html=True)

    with st.form("data_filter_form"):
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1: flt_sent = st.selectbox("Sentimen", ["semua", "positif", "negatif", "netral"], key="dt_sent")
        with col_e2: flt_score = st.selectbox("Rating", ["semua", "1", "2", "3", "4", "5"], key="dt_score")
        with col_e3: flt_page = st.number_input("Halaman", min_value=1, value=1, key="dt_page")
        st.form_submit_button("🔍 Tampilkan Data", use_container_width=True)

    _s = flt_sent if flt_sent != "semua" else None
    _sc = int(flt_score) if flt_score != "semua" else None
    dt_data = fetch_reviews(sentiment=_s, score=_sc, page=flt_page, per_page=50)

    if dt_data and dt_data.get("data"):
        df_show = pd.DataFrame(dt_data["data"])
        display_cols = [c for c in ["user_name", "content", "score", "sentiment", "review_date", "thumbs_up", "app_version"] if c in df_show.columns]
        st.dataframe(df_show[display_cols], use_container_width=True, height=400)
    else:
        st.info("Belum ada data ulasan.")

    st.markdown('<div class="nb-section">Export Data</div>', unsafe_allow_html=True)
    exp_sent = st.selectbox("Filter sentimen untuk export", ["semua", "positif", "negatif", "netral"], key="exp_sent")

    if st.button("📥 GENERATE FILE EXPORT", use_container_width=True):
        with st.spinner("Mengunduh data..."):
            full_data = fetch_reviews(sentiment=None if exp_sent == "semua" else exp_sent, per_page=1000)
        if full_data and full_data.get("data"):
            st.session_state["df_export"] = pd.DataFrame(full_data["data"])
            st.success(f"{len(st.session_state['df_export'])} ulasan siap di-download.")

    if "df_export" in st.session_state:
        df_exp = st.session_state["df_export"]
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(label="⬇ DOWNLOAD CSV", data=to_csv_bytes(df_exp), file_name=f"jkn_reviews_{exp_sent}.csv", mime="text/csv", use_container_width=True)
        with col_dl2:
            st.download_button(label="⬇ DOWNLOAD EXCEL", data=to_xlsx_bytes(df_exp), file_name=f"jkn_reviews_{exp_sent}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
