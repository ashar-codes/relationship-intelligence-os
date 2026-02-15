iimport streamlit as st

# =============================
# API KEY ACCESS
# =============================
def get_groq_api_key():
    try:
        return st.secrets["groq"]["api_key"]
    except Exception:
        return None


# =============================
# MODEL CONFIGURATION
# =============================

ANALYSIS_MODEL = "llama-3.1-8b-instant"
RESPONSE_MODEL = "llama-3.1-8b-instant"

