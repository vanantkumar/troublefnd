import streamlit as st
import time
from datetime import datetime
from model import FakeNewsClassifier
from news_fetcher import fetch_news
import google.generativeai as genai

# ── CONFIG ─────────────────────────────────────────────
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="🔍",
    layout="wide"
)

# ── GEMINI SETUP ───────────────────────────────────────
GEMINI_API_KEY = "YOUR_API_KEY"
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# ── LOAD MODEL ─────────────────────────────────────────
@st.cache_resource
def load_model():
    return FakeNewsClassifier()

model = load_model()

# ── GEMINI FUNCTION (CACHED) ───────────────────────────
@st.cache_data(show_spinner=False)
def gemini_fact_check(text):
    try:
        prompt = f"""
        Classify this news as REAL, FAKE, or UNCERTAIN.
        Give only one word answer.

        News:
        {text}
        """
        response = gemini_model.generate_content(prompt)
        answer = response.text.lower()

        if "fake" in answer:
            return "fake"
        elif "real" in answer or "true" in answer:
            return "real"
        else:
            return "uncertain"

    except:
        return "error"

# ── HYBRID PREDICTION ──────────────────────────────────
def hybrid_predict(text):
    result = model.predict(text)

    ai_result = gemini_fact_check(text)

    if ai_result == "fake":
        result['real_prob'] -= 25
    elif ai_result == "real":
        result['real_prob'] += 25

    result['real_prob'] = max(0, min(100, result['real_prob']))
    result['ai_verdict'] = ai_result

    return result

# ── HEADER ─────────────────────────────────────────────
st.title("🔍 Veridect — Fake News Detector")
st.caption("Hybrid AI: Naive Bayes + Gemini API")

# ── TABS ───────────────────────────────────────────────
tab1, tab2 = st.tabs(["📝 Analyse Text", "📡 Live News"])

# ═══════════════════════════════════════════════════════
# TAB 1 — TEXT ANALYSIS
# ═══════════════════════════════════════════════════════
with tab1:
    text_input = st.text_area(
        "Enter news text:",
        height=200,
        placeholder="Paste news article, headline, or claim..."
    )

    if st.button("Analyse"):
        if text_input.strip():
            with st.spinner("Analyzing with AI + ML..."):
                result = hybrid_predict(text_input)

            r = result['real_prob']

            # Verdict
            if r >= 65:
                st.success(f"✓ Likely Real ({r}%)")
            elif r <= 35:
                st.error(f"✕ Likely Fake ({r}%)")
            else:
                st.warning(f"? Uncertain ({r}%)")

            # Gemini Output
            st.info(f"🤖 Gemini says: {result['ai_verdict'].upper()}")

            # Metrics
            f = result['features']
            st.write("### 📊 Analysis")
            st.write(f"Words: {f['word_count']}")
            st.write(f"Sensational words: {f['sensational']}")
            st.write(f"Caps ratio: {f['caps_ratio']}%")

            # Chart
            st.write("### 📈 Score Breakdown")
            st.bar_chart({
                "Real": result['real_score'],
                "Fake": result['fake_score']
            })

        else:
            st.warning("Please enter text.")

# ═══════════════════════════════════════════════════════
# TAB 2 — LIVE NEWS
# ═══════════════════════════════════════════════════════
with tab2:
    CATEGORIES = {
        "Top": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
        "Tech": "https://news.google.com/rss/search?q=technology",
        "Business": "https://news.google.com/rss/search?q=business"
    }

    category = st.selectbox("Category", list(CATEGORIES.keys()))
    feed_url = CATEGORIES[category]

    with st.spinner("Fetching news..."):
        articles = fetch_news(feed_url, max_items=10)

    if not articles:
        st.error("Failed to load news.")
    else:
        for i, art in enumerate(articles):
            text = art["title"] + " " + art.get("description", "")
            result = hybrid_predict(text)

            r = result['real_prob']

            if r >= 65:
                badge = "🟢 Real"
            elif r <= 35:
                badge = "🔴 Fake"
            else:
                badge = "🟡 Uncertain"

            st.markdown(f"""
            ### {art['title']}
            {badge} — {r}% credible  
            {art.get("description", "")[:150]}...
            """)

            if st.button("Analyse", key=i):
                st.write("### Detailed Result")

                st.write(f"Gemini: {result['ai_verdict']}")
                st.write(f"Real Score: {result['real_score']}")
                st.write(f"Fake Score: {result['fake_score']}")

            st.divider()
