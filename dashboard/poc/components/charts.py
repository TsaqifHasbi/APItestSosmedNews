"""
Komponen Chart & Visualisasi Reusable
======================================

Modul ini berisi fungsi-fungsi pembangun visualisasi yang digunakan
oleh app.py. Setiap fungsi menerima data (DataFrame/dict/Graph) dan
me-render langsung ke Streamlit via st.plotly_chart, st.pyplot,
st.components.v1.html, dsb.

Prinsip desain:
- Setiap fungsi bersifat self-contained (render sendiri ke UI)
- Warna dan styling konsisten di seluruh dashboard
- Dark-theme friendly (latar gelap)
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
from wordcloud import WordCloud


# ══════════════════════════════════════════════════════════════════════════════
# PALET WARNA
# ══════════════════════════════════════════════════════════════════════════════

SENTIMENT_COLORS: dict[str, str] = {
    "Positif": "#22c55e",   # hijau
    "Negatif": "#ef4444",   # merah
    "Netral": "#64748b",    # abu-abu biru
}

EMOTION_COLORS: dict[str, str] = {
    "Senang": "#facc15",       # kuning
    "Sedih": "#3b82f6",        # biru
    "Marah": "#ef4444",        # merah
    "Takut": "#a855f7",        # ungu
    "Jijik": "#84cc16",        # lime
    "Terkejut": "#f97316",     # oranye
    "Percaya": "#06b6d4",      # cyan
    "Antisipasi": "#ec4899",   # pink
}

PLATFORM_COLORS: dict[str, str] = {
    "Berita Online": "#64748b",
    "X/Twitter": "#1d9bf0",
    "Facebook": "#1877f2",
    "Instagram": "#e1306c",
    "YouTube": "#ff0000",
    "TikTok": "#00f2ea",
    "Threads": "#f8f9fa",
}

_PLOTLY_LAYOUT_DEFAULTS: dict[str, Any] = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, sans-serif"},
    "margin": {"l": 40, "r": 20, "t": 50, "b": 40},
}


# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

def render_metric_cards(metrics: dict) -> None:
    """Render 5 kartu metrik utama dalam satu baris."""
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Mention", f"{metrics['volume']:,}")
    c2.metric("Pengguna Unik", f"{metrics['users']:,}")
    c3.metric("Total Engagement", f"{metrics['engagement']:,}")
    c4.metric("Estimasi Reach", f"{metrics['reach']:,}")


def render_sentiment_pie(metrics: dict) -> None:
    """Render pie chart sentimen keseluruhan."""
    labels = ["Positif", "Negatif", "Netral"]
    values = [
        metrics["sentiment_positive"],
        metrics["sentiment_negative"],
        metrics["sentiment_neutral"],
    ]
    colors = [SENTIMENT_COLORS[l] for l in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker={"colors": colors},
        textinfo="label+percent",
        textfont={"size": 13},
        hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
    )])
    fig.update_layout(
        **_PLOTLY_LAYOUT_DEFAULTS,
        title={"text": "Sentimen Keseluruhan", "x": 0.5, "font": {"size": 16}},
        showlegend=True,
        legend={"orientation": "h", "y": -0.1, "x": 0.5, "xanchor": "center"},
        height=350,
    )
    # Tambah anotasi di tengah donut
    dominant = labels[values.index(max(values))]
    fig.add_annotation(
        text=f"<b>{dominant}</b><br>{max(values):.1f}%",
        x=0.5, y=0.5,
        font={"size": 18, "color": SENTIMENT_COLORS[dominant]},
        showarrow=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_sentiment_gauge(metrics: dict) -> None:
    """Render gauge chart untuk skor sentimen positif."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=metrics["sentiment_positive"],
        number={"suffix": "%", "font": {"size": 36}},
        title={"text": "Skor Sentimen Positif", "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": SENTIMENT_COLORS["Positif"]},
            "bgcolor": "rgba(255,255,255,0.05)",
            "steps": [
                {"range": [0, 33], "color": "rgba(239,68,68,0.2)"},
                {"range": [33, 66], "color": "rgba(100,116,139,0.2)"},
                {"range": [66, 100], "color": "rgba(34,197,94,0.2)"},
            ],
            "threshold": {
                "line": {"color": "#facc15", "width": 3},
                "thickness": 0.8,
                "value": metrics["sentiment_positive"],
            },
        },
    ))
    fig.update_layout(
        **_PLOTLY_LAYOUT_DEFAULTS,
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TREND
# ══════════════════════════════════════════════════════════════════════════════

def render_trend_chart(
    df: pd.DataFrame,
    title: str,
    color_map: dict[str, str] | None = None,
) -> None:
    """Render area chart tren mention."""
    fig = px.area(
        df,
        x="date",
        y="count",
        color="category",
        title=title,
        color_discrete_map=color_map,
        labels={"date": "Tanggal", "count": "Jumlah Mention", "category": "Kategori"},
    )
    fig.update_layout(
        **_PLOTLY_LAYOUT_DEFAULTS,
        height=400,
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.2, "x": 0.5, "xanchor": "center"},
    )
    fig.update_traces(line={"width": 1.5}, opacity=0.7)
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SENTIMEN PER PLATFORM
# ══════════════════════════════════════════════════════════════════════════════

def render_platform_sentiment_card(
    platform: str,
    sentiment_data: dict,
) -> None:
    """Render satu kartu sentimen untuk satu platform."""
    platform_color = PLATFORM_COLORS.get(platform, "#64748b")

    st.markdown(
        f"""
        <div style="
            border: 1px solid {platform_color}44;
            border-radius: 12px;
            padding: 16px;
            background: linear-gradient(135deg, {platform_color}11, {platform_color}05);
            margin-bottom: 8px;
        ">
            <h4 style="margin:0 0 8px 0; color:{platform_color};">{platform}</h4>
            <p style="margin:2px 0; font-size:14px; color:#ccc;">
                <span class='material-symbols-rounded' style='font-size:14px; vertical-align:middle;'>bar_chart</span> Total: <b>{sentiment_data['total_mentions']:,}</b> mention
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Stacked horizontal bar
    fig = go.Figure()
    for sentiment, pct_key in [("Positif", "positive"), ("Negatif", "negative"), ("Netral", "neutral")]:
        fig.add_trace(go.Bar(
            y=[platform],
            x=[sentiment_data[pct_key]],
            name=sentiment,
            orientation="h",
            marker_color=SENTIMENT_COLORS[sentiment],
            text=[f"{sentiment_data[pct_key]:.1f}%"],
            textposition="inside",
            textfont={"size": 11},
            hovertemplate=f"{sentiment}: {sentiment_data[pct_key]:.1f}%<extra></extra>",
        ))

    layout_opts = dict(_PLOTLY_LAYOUT_DEFAULTS)
    layout_opts["margin"] = {"l": 0, "r": 0, "t": 0, "b": 0}
    fig.update_layout(
        **layout_opts,
        barmode="stack",
        showlegend=False,
        height=80,
        xaxis={"visible": False, "range": [0, 100]},
        yaxis={"visible": False},
    )
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# EMOSI & EMOJI
# ══════════════════════════════════════════════════════════════════════════════

def render_emotion_bar(df: pd.DataFrame) -> None:
    """Render horizontal bar chart distribusi emosi Ekman."""
    df_sorted = df.sort_values("count", ascending=True)
    colors = [EMOTION_COLORS.get(e, "#64748b") for e in df_sorted["emotion"]]

    fig = go.Figure(go.Bar(
        y=df_sorted["emotion"],
        x=df_sorted["count"],
        orientation="h",
        marker_color=colors,
        text=[f"{p:.1f}%" for p in df_sorted["percentage"]],
        textposition="outside",
        textfont={"size": 12},
        hovertemplate="%{y}: %{x:,} mention (%{text})<extra></extra>",
    ))
    fig.update_layout(
        **_PLOTLY_LAYOUT_DEFAULTS,
        title={"text": "Distribusi Emosi (Klasifikasi Ekman)", "x": 0.5, "font": {"size": 16}},
        height=450,
        xaxis_title="Jumlah Mention",
        yaxis_title="",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_emoji_table(df: pd.DataFrame) -> None:
    """Render tabel top emoji."""
    st.markdown("#### :material/mood: Top Emoji yang Digunakan")

    # Format dengan bar visual
    max_count = df["count"].max()
    df_display = df.copy()
    df_display["Proporsi"] = df_display["count"].apply(
        lambda x: "█" * int(x / max_count * 20)
    )
    df_display.columns = ["Emoji", "Jumlah", "Proporsi"]
    df_display.index = range(1, len(df_display) + 1)
    df_display.index.name = "Rank"

    st.dataframe(
        df_display,
        use_container_width=True,
        height=min(400, len(df_display) * 38 + 40),
    )


# ══════════════════════════════════════════════════════════════════════════════
# SOCIAL NETWORK ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def render_sna_graph(
    G: nx.Graph,
    title: str,
    color_map: dict[str, str],
) -> None:
    """
    Render graf SNA interaktif menggunakan Pyvis.

    Parameters
    ----------
    G : networkx.Graph
        Graf dengan atribut node: label, group, centrality.
    title : str
        Judul graf.
    color_map : dict[str, str]
        Mapping group → warna hex.
    """
    st.markdown(f"#### {title}")

    # Buat network Pyvis
    net = Network(
        height="550px",
        width="100%",
        bgcolor="#0e1117",
        font_color="#e2e8f0",
        directed=False,
    )

    # Konfigurasi fisika
    net.set_options("""
    {
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -80,
                "centralGravity": 0.01,
                "springLength": 120,
                "springConstant": 0.08,
                "damping": 0.4
            },
            "solver": "forceAtlas2Based",
            "stabilization": {
                "enabled": true,
                "iterations": 150
            }
        },
        "nodes": {
            "borderWidth": 2,
            "borderWidthSelected": 4
        },
        "edges": {
            "color": {
                "color": "#475569",
                "highlight": "#f59e0b",
                "opacity": 0.6
            },
            "smooth": {
                "type": "continuous"
            }
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 100,
            "zoomView": true,
            "dragView": true
        }
    }
    """)

    # Tambah node
    for node_id in G.nodes():
        attrs = G.nodes[node_id]
        group = attrs.get("group", "Unknown")
        centrality = attrs.get("centrality", 0.1)
        label = attrs.get("label", f"Node {node_id}")
        color = color_map.get(group, "#64748b")

        # Ukuran node proporsional terhadap sentralitas
        size = 10 + centrality * 80

        net.add_node(
            node_id,
            label=label,
            title=f"{label}\nGrup: {group}\nSentralitas: {centrality:.3f}",
            color=color,
            size=size,
            font={"size": max(10, int(size * 0.6))},
        )

    # Tambah edge
    for u, v, data in G.edges(data=True):
        weight = data.get("weight", 0.5)
        net.add_edge(u, v, width=weight * 3, title=f"Bobot: {weight:.2f}")

    # Render ke HTML dan embed
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".html", mode="w", encoding="utf-8"
    ) as f:
        net.save_graph(f.name)
        html_path = f.name

    html_content = Path(html_path).read_text(encoding="utf-8")
    components.html(html_content, height=570, scrolling=False)

    # Legenda
    legend_items = [
        f'<span style="color:{c};">●</span> {g}'
        for g, c in color_map.items()
    ]
    st.markdown(
        f"<div style='text-align:center; font-size:13px; color:#94a3b8;'>"
        f"{'&nbsp;&nbsp;|&nbsp;&nbsp;'.join(legend_items)}"
        f"</div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# ISU & DIFUSI
# ══════════════════════════════════════════════════════════════════════════════

def render_top_issues(issues: list[dict]) -> None:
    """Render ranked list isu utama."""
    st.markdown("#### :material/label: Top Isu Teridentifikasi")

    for iss in issues:
        platforms_str = ", ".join(iss["platforms"])
        st.markdown(
            f"""
            <div style="
                border-left: 4px solid #3b82f6;
                padding: 10px 16px;
                margin-bottom: 8px;
                background: rgba(59,130,246,0.06);
                border-radius: 0 8px 8px 0;
            ">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:15px;">
                        <b>#{iss['rank']}</b>&nbsp;&nbsp;{iss['title']}
                    </span>
                    <span style="font-size:13px; color:#94a3b8;">
                        {iss['mentions']:,} mention
                    </span>
                </div>
                <div style="font-size:12px; color:#64748b; margin-top:4px;">
                    Platform: {platforms_str}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_diffusion_chart(df: pd.DataFrame) -> None:
    """Render small multiples — difusi isu lintas platform."""
    if df.empty:
        st.info("Tidak ada data difusi isu.")
        return

    issues = df["issue"].unique()

    for issue in issues:
        df_issue = df[df["issue"] == issue]
        fig = px.line(
            df_issue,
            x="date",
            y="count",
            color="platform",
            title=f"📡 Difusi: {issue[:60]}...",
            color_discrete_map=PLATFORM_COLORS,
            labels={"date": "Tanggal", "count": "Mention", "platform": "Platform"},
        )
        fig.update_layout(
            **_PLOTLY_LAYOUT_DEFAULTS,
            height=300,
            legend={"orientation": "h", "y": -0.3, "x": 0.5, "xanchor": "center"},
        )
        fig.update_traces(line={"width": 2})
        st.plotly_chart(fig, use_container_width=True)


def render_news_sites_table(df: pd.DataFrame) -> None:
    """Render tabel situs berita teratas."""
    st.markdown("#### 📰 Situs Berita Paling Banyak Memberitakan")
    df_display = df.copy()
    df_display.columns = ["Situs", "Jumlah Artikel", "Estimasi Reach"]
    df_display["Estimasi Reach"] = df_display["Estimasi Reach"].apply(lambda x: f"{x:,}")
    df_display.index = range(1, len(df_display) + 1)
    df_display.index.name = "Rank"
    st.dataframe(df_display, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# INFLUENCER & KONTEN VIRAL
# ══════════════════════════════════════════════════════════════════════════════

def render_influencer_list(df: pd.DataFrame, platform: str) -> None:
    """Render ranked list influencer per platform."""
    st.markdown(f"##### :material/star: Top Pemengaruh — {platform}")

    for i, row in df.iterrows():
        eng_color = "#22c55e" if row["engagement_rate"] > 5 else "#f59e0b" if row["engagement_rate"] > 2 else "#64748b"
        st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 10px 14px;
                margin-bottom: 6px;
                background: rgba(255,255,255,0.03);
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.06);
            ">
                <div style="
                    width: 42px; height: 42px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #6366f1, #a855f7);
                    display: flex; align-items: center; justify-content: center;
                    font-size: 18px; font-weight: bold; color: white;
                    flex-shrink: 0;
                ">{row['name'][0]}</div>
                <div style="flex: 1; min-width: 0;">
                    <div style="font-weight: 600; font-size: 14px;">{row['name']}</div>
                    <div style="font-size: 12px; color: #94a3b8;">{row['handle']}</div>
                </div>
                <div style="text-align: right; flex-shrink: 0;">
                    <div style="font-size: 13px;">{row['followers']:,} pengikut</div>
                    <div style="font-size: 12px; color: {eng_color};">
                        ER: {row['engagement_rate']:.1f}% · {row['posts']} post
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_viral_content(df: pd.DataFrame, platform: str) -> None:
    """Render daftar konten viral per platform."""
    st.markdown(f"##### :material/local_fire_department: Konten Paling Viral — {platform}")

    for _, row in df.head(5).iterrows():
        total_eng = row["likes"] + row["shares"] + row["comments"]
        st.markdown(
            f"""
            <div style="
                padding: 12px 16px;
                margin-bottom: 8px;
                background: rgba(255,255,255,0.03);
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.06);
            ">
                <div style="font-size: 14px; margin-bottom: 6px;">
                    {row['content'][:120]}
                </div>
                <div style="display:flex; justify-content:space-between; font-size:12px; color:#94a3b8;">
                    <span style='display:inline-flex; align-items:center; gap:4px;'><span class='material-symbols-rounded' style='font-size:14px;'>person</span> {row['author']}</span>
                    <span>
                        <span style='display:inline-flex; align-items:center; gap:4px;'><span class='material-symbols-rounded' style='font-size:14px;'>favorite</span> {row['likes']:,}</span> · <span style='display:inline-flex; align-items:center; gap:4px;'><span class='material-symbols-rounded' style='font-size:14px;'>share</span> {row['shares']:,}</span> · <span style='display:inline-flex; align-items:center; gap:4px;'><span class='material-symbols-rounded' style='font-size:14px;'>comment</span> {row['comments']:,}</span>
                        &nbsp;(Total: {total_eng:,})
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# WORD CLOUD
# ══════════════════════════════════════════════════════════════════════════════

def render_wordcloud(word_freq: dict[str, int], title: str) -> None:
    """Render awan kata/tagar menggunakan WordCloud + matplotlib."""
    if not word_freq:
        st.info("Tidak ada data untuk ditampilkan.")
        return

    wc = WordCloud(
        width=900,
        height=450,
        background_color="#0e1117",
        colormap="viridis",
        max_words=80,
        min_font_size=10,
        max_font_size=120,
        prefer_horizontal=0.7,
        margin=10,
        contour_width=0,
    ).generate_from_frequencies(word_freq)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(title, color="#e2e8f0", fontsize=16, fontweight="bold", pad=15)
    fig.patch.set_facecolor("#0e1117")
    fig.tight_layout(pad=1)
    st.pyplot(fig)
    plt.close(fig)
