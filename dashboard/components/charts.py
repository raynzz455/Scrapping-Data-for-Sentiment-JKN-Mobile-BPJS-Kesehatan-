"""
Chart builders menggunakan Plotly untuk Streamlit dashboard.
Semua chart menggunakan tema neo-brutalism: border tegas, warna bold, no shadow.
"""
from __future__ import annotations
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Warna neo-brutalism palette ───────────────────────────
C_POS   = "#00E5A0"   # neon green — positif
C_NEG   = "#FF3B5C"   # neon red   — negatif
C_NEU   = "#FFD600"   # neon yellow — netral
C_BG    = "#0A0A0A"   # background
C_CARD  = "#111111"   # card bg
C_BORDER = "#FFFFFF"  # white border
C_TEXT  = "#FFFFFF"

LAYOUT_BASE = dict(
    paper_bgcolor=C_CARD,
    plot_bgcolor=C_CARD,
    font=dict(family="Space Grotesk, monospace", color=C_TEXT, size=12),
    margin=dict(l=20, r=20, t=40, b=20),
)


def donut_chart(positif: int, netral: int, negatif: int) -> go.Figure:
    """Donut chart distribusi sentimen."""
    fig = go.Figure(go.Pie(
        labels=["Positif", "Netral", "Negatif"],
        values=[positif, netral, negatif],
        hole=0.65,
        marker=dict(
            colors=[C_POS, C_NEU, C_NEG],
            line=dict(color=C_BG, width=3),
        ),
        textfont=dict(size=13, color=C_TEXT),
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{value} ulasan<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        showlegend=False,
        height=280,
        annotations=[dict(
            text=f"<b>{positif+netral+negatif}</b><br><span style='font-size:10px'>total</span>",
            x=0.5, y=0.5,
            font=dict(size=20, color=C_TEXT),
            showarrow=False,
        )],
    )
    return fig


def bar_rating(df: pd.DataFrame) -> go.Figure:
    """Bar chart distribusi rating bintang 1–5."""
    counts = df["score"].value_counts().sort_index()
    colors = {1: C_NEG, 2: "#FF8C42", 3: C_NEU, 4: "#7EFF4E", 5: C_POS}
    fig = go.Figure(go.Bar(
        x=[f"★ {i}" for i in counts.index],
        y=counts.values,
        marker=dict(
            color=[colors.get(i, C_NEU) for i in counts.index],
            line=dict(color=C_BORDER, width=2),
        ),
        text=counts.values,
        textposition="outside",
        textfont=dict(color=C_TEXT, size=12),
        hovertemplate="<b>%{x}</b>: %{y} ulasan<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        height=260,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color=C_TEXT, size=12),
            linecolor=C_BORDER,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#222222",
            tickfont=dict(color=C_TEXT),
            linecolor=C_BORDER,
        ),
        bargap=0.25,
    )
    return fig


def trend_line(monthly_data: list[dict]) -> go.Figure:
    """Line chart tren sentimen per bulan."""
    if not monthly_data:
        return go.Figure()

    df = pd.DataFrame(monthly_data)
    fig = go.Figure()

    traces = {
        "positif": (C_POS, "solid",  3),
        "negatif": (C_NEG, "solid",  3),
        "netral":  (C_NEU, "dot",    2),
    }

    for col, (color, dash, width) in traces.items():
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["bulan"],
                y=df[col],
                name=col.capitalize(),
                mode="lines+markers",
                line=dict(color=color, width=width, dash=dash),
                marker=dict(size=6, color=color, line=dict(color=C_BORDER, width=1.5)),
                hovertemplate=f"<b>{col.capitalize()}</b><br>%{{x}}: %{{y}} ulasan<extra></extra>",
            ))

    fig.update_layout(
        **LAYOUT_BASE,
        height=300,
        legend=dict(
            orientation="h",
            y=1.1,
            font=dict(size=12, color=C_TEXT),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            showgrid=False,
            tickangle=45,
            tickfont=dict(color=C_TEXT, size=10),
            linecolor=C_BORDER,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#222222",
            tickfont=dict(color=C_TEXT),
            linecolor=C_BORDER,
        ),
        hovermode="x unified",
    )
    return fig


def horizontal_bar_avg_rating(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar: rata-rata rating per sentimen."""
    if df.empty or "sentiment" not in df.columns:
        return go.Figure()

    avg = df.groupby("sentiment")["score"].mean().round(2).reset_index()
    avg.columns = ["Sentimen", "Avg Rating"]
    order   = ["negatif", "netral", "positif"]
    colors  = [C_NEG, C_NEU, C_POS]

    avg["Sentimen"] = pd.Categorical(avg["Sentimen"], categories=order, ordered=True)
    avg = avg.sort_values("Sentimen")

    fig = go.Figure(go.Bar(
        y=avg["Sentimen"].str.capitalize(),
        x=avg["Avg Rating"],
        orientation="h",
        marker=dict(
            color=colors[:len(avg)],
            line=dict(color=C_BORDER, width=2),
        ),
        text=[f"{v:.2f} ★" for v in avg["Avg Rating"]],
        textposition="outside",
        textfont=dict(color=C_TEXT, size=13),
        hovertemplate="<b>%{y}</b><br>Avg: %{x:.2f} bintang<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        height=220,
        xaxis=dict(range=[0, 5.5], showgrid=True, gridcolor="#222222", tickfont=dict(color=C_TEXT), linecolor=C_BORDER),
        yaxis=dict(showgrid=False, tickfont=dict(color=C_TEXT, size=13), linecolor=C_BORDER),
    )
    return fig
