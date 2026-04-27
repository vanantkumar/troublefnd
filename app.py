import streamlit as st
from model import FakeNewsClassifier
from news_fetcher import fetch_news

# ── Page Config ─────────────────────────────
st.set_page_config(page_title="Fake News Detector", page_icon="🔍")

# ── Load Model ──────────────────────────────
@st.cache_resource
def load_model():
    return FakeNewsClassifier()

model = load_model()

# ── Title ───────────────────────────────────
st.title(" Fake News Detection System")

# ── Tabs ────────────────────────────────────
tab1, tab2 = st.tabs(["Analyse Text", "Live News"])

# ════════════════════════════════════════════
# TAB 1 — TEXT ANALYSIS
# ════════════════════════════════════════════
with tab1:
    st.subheader("Enter News Content")

    text_input = st.text_area("Paste your news here:")

    if st.button("Analyse"):
        if text_input.strip() == "":
            st.warning("Please enter some text")
        else:
            result = model.predict(text_input)

            real_prob = result["real_prob"]

            # ── Verdict ─────────────────────
            if real_prob >= 65:
                st.success(f"✅ Likely Real ({real_prob}%)")
            elif real_prob <= 35:
                st.error(f"❌ Likely Fake ({real_prob}%)")
            else:
                st.warning(f"⚠️ Uncertain ({real_prob}%)")

            # ── Features ────────────────────
            st.subheader("Text Analysis")

            f = result["features"]

            st.write("Word Count:", f["word_count"])
            st.write("Sensational Words:", f["sensational"])
            st.write("CAPS Ratio:", f["caps_ratio"])
            st.write("Hedge Words:", f["hedges"])
            st.write("Exclamations:", f["exclaims"])

            # ── Score Chart ────────────────
            st.subheader("Score Breakdown")

            st.bar_chart({
                "Real": result["real_score"],
                "Fake": result["fake_score"]
            })

# ════════════════════════════════════════════
# TAB 2 — LIVE NEWS
# ════════════════════════════════════════════
with tab2:
    st.subheader("Live News Feed")

    categories = {
        "Top": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
        "Technology": "https://news.google.com/rss/search?q=technology",
        "Business": "https://news.google.com/rss/search?q=business",
    }

    category = st.selectbox("Select Category", list(categories.keys()))

    if st.button("Load News"):
        articles = fetch_news(categories[category], max_items=10)

        if not articles:
            st.error("Failed to load news")
        else:
            for i, art in enumerate(articles):
                st.markdown("---")

                st.subheader(art["title"])
                st.write(art.get("description", ""))

                result = model.predict(art["title"] + " " + art.get("description", ""))
                r = result["real_prob"]

                if r >= 65:
                    st.success(f"Real ({r}%)")
                elif r <= 35:
                    st.error(f"Fake ({r}%)")
                else:
                    st.warning(f"Uncertain ({r}%)")

                if st.button("Analyse Article", key=i):
                    st.write("Detailed Analysis:")

                    f = result["features"]
                    st.write(f)
