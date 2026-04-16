# app.py

import streamlit as st
from model import FakeNewsClassifier

# ── Page Config ─────────────────────────
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="📰",
    layout="centered"
)

# ── Load Model Safely ─────────────────────────
@st.cache_resource
def load_model():
    return FakeNewsClassifier()

model = load_model()

# ── Prediction Wrapper (SAFE) ─────────────────────────
def hybrid_predict(text_input):
    try:
        if not hasattr(model, "predict"):
            return {"label": "Error", "reason": "Model missing predict() method"}

        result = model.predict(text_input)

        if not isinstance(result, dict):
            return {"label": "Error", "reason": "Invalid model output"}

        return result

    except Exception as e:
        return {"label": "Error", "reason": str(e)}


# ── UI ─────────────────────────
st.title("📰 Fake News Detection System")
st.markdown("Analyze whether a news headline or article is **Real or Fake**.")

# Input box
text_input = st.text_area("Enter News Text", height=180)

# Button
if st.button("Analyze News"):

    if not text_input.strip():
        st.warning("⚠ Please enter some text to analyze.")
    else:
        with st.spinner("Analyzing..."):
            result = hybrid_predict(text_input)

        # ── Display Result ─────────────────────────
        if result["label"] == "Error":
            st.error(f"❌ {result['reason']}")

        elif result["label"] == "Invalid":
            st.warning(f"⚠ {result['reason']}")

        else:
            label = result["label"]
            confidence = result["confidence"]

            if label == "Fake News":
                st.error(f"🛑 {label}")
            else:
                st.success(f"✅ {label}")

            st.write(f"**Confidence:** {confidence}%")

            # Expand for details
            with st.expander("🔍 Detailed Scores"):
                st.write(f"Fake Score: {result['fake_score']}")
                st.write(f"Real Score: {result['real_score']}")


# ── Footer ─────────────────────────
st.markdown("---")
st.caption("Built with Streamlit • Hybrid Fake News Detection System")
