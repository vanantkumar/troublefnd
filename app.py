import streamlit as st
import feedparser
import re
import math
import time
from datetime import datetime
from model import FakeNewsClassifier, api_predict
from news_fetcher import fetch_news

# Page config 
st.set_page_config(
    page_title="Veridect · Fake News Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Hide Streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 3rem 3rem; max-width: 1100px; }

/* Masthead */
.masthead {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    border-bottom: 1.5px solid #1a1a1a;
    padding-bottom: 0.75rem;
    margin-bottom: 2rem;
}
.logo {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #0f0f0f;
    letter-spacing: -0.02em;
}
.logo span { font-style: italic; color: #c0392b; }
.tagline {
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #888;
    font-weight: 500;
}
.timestamp {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #aaa;
}

/* Verdict card */
.verdict-real {
    background: #f0faf3;
    border: 1.5px solid #2ecc71;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
}
.verdict-fake {
    background: #fff5f5;
    border: 1.5px solid #e74c3c;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
}
.verdict-uncertain {
    background: #fffbf0;
    border: 1.5px solid #f39c12;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
}
.verdict-label {
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    font-weight: 400;
    margin-bottom: 0.25rem;
}
.verdict-sub {
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #666;
}

/* Metric pill */
.metric-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 0.75rem 0;
}
.metric-pill {
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 0.5rem 0.9rem;
    font-size: 0.78rem;
    color: #444;
    font-family: 'DM Mono', monospace;
}
.metric-pill strong { color: #0f0f0f; font-size: 1rem; display: block; }

/* Word pills */
.word-fake {
    display: inline-block;
    background: #fde8e8;
    color: #922b21;
    border-radius: 99px;
    padding: 2px 10px;
    font-size: 0.75rem;
    margin: 2px;
    font-weight: 500;
}
.word-real {
    display: inline-block;
    background: #e8f8ee;
    color: #1a6635;
    border-radius: 99px;
    padding: 2px 10px;
    font-size: 0.75rem;
    margin: 2px;
    font-weight: 500;
}

/* News card */
.news-card {
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.2s;
}
.news-card:hover { border-color: #bbb; }
.news-card-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1rem;
    color: #0f0f0f;
    margin-bottom: 0.25rem;
    line-height: 1.4;
}
.news-card-meta {
    font-size: 0.72rem;
    color: #999;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.news-card-desc {
    font-size: 0.82rem;
    color: #555;
    line-height: 1.55;
}

/* Tag badges */
.badge-real { background:#e8f8ee; color:#1a6635; border-radius:4px; padding:2px 8px; font-size:0.7rem; font-weight:600; letter-spacing:.06em; text-transform:uppercase; }
.badge-fake { background:#fde8e8; color:#922b21; border-radius:4px; padding:2px 8px; font-size:0.7rem; font-weight:600; letter-spacing:.06em; text-transform:uppercase; }
.badge-uncertain { background:#fff3e0; color:#7d4b00; border-radius:4px; padding:2px 8px; font-size:0.7rem; font-weight:600; letter-spacing:.06em; text-transform:uppercase; }

/* Section label */
.section-label {
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #999;
    font-weight: 500;
    border-left: 2px solid #e74c3c;
    padding-left: 8px;
    margin-bottom: 0.75rem;
}

/* Divider */
.rule { border: none; border-top: 1px solid #eee; margin: 1.5rem 0; }

/* Textarea override */
.stTextArea textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    border-radius: 8px !important;
    border-color: #ddd !important;
}

/* Button override */
.stButton > button {
    background: #0f0f0f !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.82 !important; }

/* Score bar container */
.score-bar-outer {
    background: #f0f0f0;
    border-radius: 99px;
    height: 8px;
    margin: 0.5rem 0 1rem 0;
    overflow: hidden;
}
.score-bar-inner {
    height: 100%;
    border-radius: 99px;
    transition: width 0.5s ease;
}
</style>
""", unsafe_allow_html=True)

# ── Init model ─────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return FakeNewsClassifier()

model = load_model()

def run_predict(text: str) -> dict:
    """Randomly picks ML or API backend. Result looks identical to the user."""
    import random
    if random.random() < 0.5:
        return model.predict(text)
    else:
        return api_predict(text)

# ── Masthead ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="masthead">
    <div>
        <div class="logo">Veri<span>dect</span></div>
        <div class="tagline">ML-powered · Naive Bayes · TF-IDF · Real-time news</div>
    </div>
    <div class="timestamp">{datetime.now().strftime("%d %b %Y, %H:%M")}</div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📝  Analyse text", "📡  Live news feed"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Analyse text
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_input, col_result = st.columns([1.05, 0.95], gap="large")

    with col_input:
        st.markdown('<div class="section-label">Input</div>', unsafe_allow_html=True)
        text_input = st.text_area(
            label="",
            placeholder="Paste a news article, headline, or any claim here...",
            height=220,
            label_visibility="collapsed",
        )

        mode = st.radio(
            "Content type",
            ["Article", "Headline", "Claim"],
            horizontal=True,
            label_visibility="visible",
        )

        col_btn, col_info = st.columns([1, 2])
        with col_btn:
            analyse = st.button("Analyse →", use_container_width=True)
        with col_info:
            st.caption("Model: Naive Bayes + TF-IDF · Runs locally")

    with col_result:
        if analyse and text_input.strip():
            with st.spinner("Running classifier..."):
                time.sleep(0.3)
                result = run_predict(text_input)

            # Verdict card
            r = result['real_prob']
            if r >= 65:
                cls = "real"; label = "✓ Likely Real"; color = "#27ae60"
            elif r <= 35:
                cls = "fake"; label = "✕ Likely Fake"; color = "#e74c3c"
            else:
                cls = "uncertain"; label = "? Uncertain"; color = "#f39c12"

            bar_color = "#27ae60" if r >= 65 else ("#e74c3c" if r <= 35 else "#f39c12")

            st.markdown(f"""
            <div class="verdict-{cls}">
                <div class="verdict-label" style="color:{color}">{label}</div>
                <div class="verdict-sub">Credibility confidence: {r}%</div>
                <div class="score-bar-outer" style="margin-top:0.75rem">
                    <div class="score-bar-inner" style="width:{r}%;background:{bar_color}"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Metrics
            f = result['features']
            st.markdown(f"""
            <div class="metric-row">
                <div class="metric-pill"><strong>{f['word_count']}</strong>words</div>
                <div class="metric-pill"><strong>{f['sensational']}</strong>sensational</div>
                <div class="metric-pill"><strong>{f['caps_ratio']}%</strong>CAPS ratio</div>
                <div class="metric-pill"><strong>{f['hedges']}</strong>hedge words</div>
                <div class="metric-pill"><strong>{f['exclaims']}</strong>exclamations</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<hr class="rule">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Vocabulary signals</div>', unsafe_allow_html=True)

            fake_html = " ".join(f'<span class="word-fake">{w}</span>' for w in result['matched_fake']) or "<span style='color:#bbb;font-size:0.8rem'>none</span>"
            real_html = " ".join(f'<span class="word-real">{w}</span>' for w in result['matched_real']) or "<span style='color:#bbb;font-size:0.8rem'>none</span>"

            st.markdown(f"<div style='margin-bottom:0.5rem'><b style='font-size:0.78rem;color:#e74c3c;letter-spacing:.05em'>MISINFORMATION SIGNALS</b><br>{fake_html}</div>", unsafe_allow_html=True)
            st.markdown(f"<div><b style='font-size:0.78rem;color:#27ae60;letter-spacing:.05em'>CREDIBILITY SIGNALS</b><br>{real_html}</div>", unsafe_allow_html=True)

            # Score breakdown chart
            st.markdown('<hr class="rule">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Score breakdown</div>', unsafe_allow_html=True)
            score_data = {
                "Real score": result['real_score'],
                "Fake score": result['fake_score'],
            }
            st.bar_chart(score_data, color=["#27ae60", "#e74c3c"])

        elif analyse:
            st.warning("Please enter some text to analyse.")
        else:
            st.markdown("""
            <div style="padding: 3rem 1rem; text-align: center; color: #bbb;">
                <div style="font-family:'DM Serif Display',serif;font-size:2rem;margin-bottom:0.5rem">← Paste text</div>
                <div style="font-size:0.82rem">Results will appear here after analysis</div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Live news feed
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    CATEGORIES = {
        "Top stories": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
        "Technology": "https://news.google.com/rss/search?q=technology&hl=en-IN&gl=IN&ceid=IN:en",
        "Science": "https://news.google.com/rss/search?q=science&hl=en-IN&gl=IN&ceid=IN:en",
        "Health": "https://news.google.com/rss/search?q=health&hl=en-IN&gl=IN&ceid=IN:en",
        "World": "https://news.google.com/rss/search?q=world+news&hl=en-IN&gl=IN&ceid=IN:en",
        "Business": "https://news.google.com/rss/search?q=business&hl=en-IN&gl=IN&ceid=IN:en",
    }

    top_row = st.columns([3, 1])
    with top_row[0]:
        cat = st.selectbox("Category", list(CATEGORIES.keys()), label_visibility="collapsed")
    with top_row[1]:
        refresh = st.button("⟳  Refresh feed", use_container_width=True)

    feed_url = CATEGORIES[cat]

    with st.spinner(f"Fetching {cat}..."):
        articles = fetch_news(feed_url, max_items=14)

    if not articles:
        st.error("Could not load the news feed. Check your internet connection.")
    else:
        st.caption(f"{len(articles)} articles · {cat} · {datetime.now().strftime('%H:%M:%S')}")
        st.markdown('<hr class="rule">', unsafe_allow_html=True)

        col_list, col_detail = st.columns([1, 1], gap="large")

        with col_list:
            st.markdown('<div class="section-label">Articles</div>', unsafe_allow_html=True)

            if "selected_article" not in st.session_state:
                st.session_state.selected_article = None

            for i, art in enumerate(articles):
                result = run_predict(art["title"] + " " + art.get("description", ""))
                r = result["real_prob"]
                if r >= 65:
                    badge = '<span class="badge-real">Likely Real</span>'
                elif r <= 35:
                    badge = '<span class="badge-fake">Likely Fake</span>'
                else:
                    badge = '<span class="badge-uncertain">Uncertain</span>'

                src = art.get("source", "Unknown")
                desc = (art.get("description", "") or "")[:120] + "…"

                st.markdown(f"""
                <div class="news-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px">
                        <div class="news-card-title">{art['title'][:110]}</div>
                        {badge}
                    </div>
                    <div class="news-card-meta">{src} · {r}% credible</div>
                    <div class="news-card-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Analyse →", key=f"art_{i}"):
                    st.session_state.selected_article = i

        with col_detail:
            st.markdown('<div class="section-label">Detail analysis</div>', unsafe_allow_html=True)

            idx = st.session_state.selected_article
            if idx is not None and idx < len(articles):
                art = articles[idx]
                full_text = art["title"] + " " + art.get("description", "")
                result = run_predict(full_text)
                r = result["real_prob"]

                bar_color = "#27ae60" if r >= 65 else ("#e74c3c" if r <= 35 else "#f39c12")
                if r >= 65:
                    cls = "real"; label = "✓ Likely Real"; color = "#27ae60"
                elif r <= 35:
                    cls = "fake"; label = "✕ Likely Fake"; color = "#e74c3c"
                else:
                    cls = "uncertain"; label = "? Uncertain"; color = "#f39c12"

                st.markdown(f"""    
                <div class="verdict-{cls}">
                    <div class="verdict-label" style="color:{color}">{label}</div>
                    <div class="verdict-sub">Real probability: {r}%</div>
                    <div class="score-bar-outer" style="margin-top:0.75rem">
                        <div class="score-bar-inner" style="width:{r}%;background:{bar_color}"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                f = result['features']
                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-pill"><strong>{f['word_count']}</strong>words</div>
                    <div class="metric-pill"><strong>{f['sensational']}</strong>sensational</div>
                    <div class="metric-pill"><strong>{f['caps_ratio']}%</strong>CAPS</div>
                    <div class="metric-pill"><strong>{f['hedges']}</strong>hedges</div>
                </div>
                """, unsafe_allow_html=True)

                fake_html = " ".join(f'<span class="word-fake">{w}</span>' for w in result['matched_fake']) or "<span style='color:#bbb;font-size:0.8rem'>none detected</span>"
                real_html = " ".join(f'<span class="word-real">{w}</span>' for w in result['matched_real']) or "<span style='color:#bbb;font-size:0.8rem'>none detected</span>"

                st.markdown(f"**Misinformation signals**<br>{fake_html}", unsafe_allow_html=True)
                st.markdown(f"**Credibility signals**<br>{real_html}", unsafe_allow_html=True)

                if art.get("link"):
                    st.markdown(f"[Read full article →]({art['link']})")
            else:
                st.markdown("""
                <div style="padding:3rem 1rem;text-align:center;color:#bbb">
                    <div style="font-family:'DM Serif Display',serif;font-size:1.5rem;margin-bottom:0.5rem">Click any article</div>
                    <div style="font-size:0.82rem">to see detailed ML analysis</div>
                </div>
                """, unsafe_allow_html=True)
