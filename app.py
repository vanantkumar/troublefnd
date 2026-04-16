import streamlit as st
import google.generativeai as genai
from model import MLModel

# ── CONFIG ─────────────────────────
st.set_page_config(page_title="Fake News Detector", page_icon="📰")

# ── LOAD ML MODEL ─────────────────────────
@st.cache_resource
def load_ml():
    return MLModel()

ml_model = load_ml()

# ── GEMINI SETUP ─────────────────────────
API_KEY = "YOUR_GEMINI_API_KEY"   # 🔴 replace this
genai.configure(api_key=API_KEY)

gemini = genai.GenerativeModel("gemini-1.5-flash")

# ── GEMINI ANALYSIS ─────────────────────────
def api_analysis(text):
    prompt = f"""
    Check if this news is Fake or Real.

    Give:
    Label: Fake or Real
    Reason: short explanation

    News:
    {text}
    """

    try:
        response = gemini.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"API Error: {str(e)}"


# ── HYBRID LOGIC ─────────────────────────
def hybrid_predict(text):
    ml_result = ml_model.predict(text)

    api_result = api_analysis(text)

    return ml_result, api_result


# ── UI ─────────────────────────
st.title("📰 Hybrid Fake News Detection System")

text = st.text_area("Enter News Text")

if st.button("Analyze"):

    if not text.strip():
        st.warning("Enter text first.")
    else:
        with st.spinner("Analyzing..."):
            ml_result, api_result = hybrid_predict(text)

        st.subheader("🤖 ML Prediction")
        st.write(f"Label: {ml_result['label']}")
        st.write(f"Confidence: {ml_result['confidence']}%")

        st.subheader("🧠 AI (Gemini) Analysis")
        st.write(api_result)
