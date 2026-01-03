import streamlit as st
import requests
import socket
from pathlib import Path


# =========================================================
# PAGE CONFIG (MUST BE FIRST STREAMLIT CALL)
# =========================================================
st.set_page_config(
    page_title="Starbucks LLM",
    layout="wide"
)


# =========================================================
# BACKEND URL (Docker vs Local)
# =========================================================
def in_docker():
    try:
        socket.gethostbyname("backend")
        return True
    except socket.gaierror:
        return False


BACKEND_URL = (
    "http://backend:8000/ask"
    if in_docker()
    else "http://localhost:8000/ask"
)


# =========================================================
# SIDEBAR LOGO (HF + LOCAL SAFE)
# =========================================================
LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "starbucks_logo.png"

if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), width=140)
else:
    st.sidebar.markdown("## ☕ Starbucks")


# =========================================================
# GLOBAL CSS (STARBUCKS THEME – HF SAFE)
# =========================================================
st.markdown(
    """
    <style>
    /* ===============================
       PAGE BACKGROUND
       =============================== */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #EAF4F1 !important;
    }

    [data-testid="stVerticalBlock"] {
        background-color: transparent !important;
    }

    /* ===============================
       INPUTS & TEXT AREAS
       =============================== */
    input, textarea {
        background-color: #FFFFFF !important;
        color: #1E3932 !important;
        border-radius: 10px !important;
        border: 1px solid #C7DCD2 !important;
        font-size: 16px !important;
    }

    input::placeholder, textarea::placeholder {
        color: #6F8F85 !important;
    }

    /* ===============================
       BUTTONS
       =============================== */
    button {
        background-color: #00704A !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.5em 1.2em !important;
    }

    button:hover {
        background-color: #005F3D !important;
    }

    /* ===============================
       HEADERS & TEXT
       =============================== */
    h1, h2, h3 {
        color: #00704A !important;
    }

    /* ===============================
       CARD STYLE
       =============================== */
    .card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* ===============================
       LLM ANSWER OUTPUT
       =============================== */
    [data-testid="stMarkdownContainer"] {
        color: #1E3932 !important;
        font-size: 16px;
        line-height: 1.6;
    }

    [data-testid="stMarkdownContainer"] img {
        background-color: white;
        padding: 6px;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# MAIN TITLE (STREAMLIT NATIVE — HF SAFE)
# =========================================================
st.title("☕ Starbucks Recommendation System")
st.markdown("---")


# =========================================================
# QUESTION HEADER (STREAMLIT NATIVE — HF SAFE)
# =========================================================
st.subheader("Ask a question about Starbucks menu items")
st.caption("Type your question below (e.g., calories, caffeine, recommendations).")


user_question = st.text_input(
    label="Ask a question about Starbucks menu items",
    placeholder="Example: Which Starbucks drink has the least sugar?",
    label_visibility="collapsed"
)


# =========================================================
# ASK BUTTON & BACKEND CALL
# =========================================================
if st.button("Ask", disabled=not user_question.strip()):
    try:
        with st.spinner("Contacting backend..."):
            response = requests.post(
                BACKEND_URL,
                json={"question": user_question},
                timeout=20
            )

        if response.status_code != 200:
            st.error(f"Backend error: {response.text}")
        else:
            data = response.json()
            answer = data.get("answer", "No answer returned.")

            st.markdown(
                f"""
                <div class="card">
                    <h3>💬 LLM Answer</h3>
                    <div>{answer}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
