import streamlit as st
import requests
import pandas as pd
import os
import socket
from PIL import Image
from pathlib import Path


# --- Auto-detect Docker network ---
def in_docker():
    try:
        # Docker containers usually have hostname 'backend' reachable
        socket.gethostbyname("backend")
        return True
    except socket.gaierror:
        return False

# --- Set backend URL based on environment ---
if in_docker():
    BACKEND_URL = "http://backend:8000/ask"  # when frontend is in Docker
else:
    BACKEND_URL = "http://localhost:8000/ask"  # when running on host


# Resolve absolute path (HF-safe)
ROOT_DIR = Path(__file__).resolve().parents[1]
LOGO_PATH = ROOT_DIR / "assets" / "starbucks_logo.png"

st.write("DEBUG LOGO PATH:", LOGO_PATH)  # TEMP: for HF debugging

LOGO_PATH = Path("assets/starbucks_logo.png")

st.write("DEBUG CWD:", Path.cwd())
st.write("DEBUG LOGO PATH:", LOGO_PATH.resolve())

if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), width=140)
else:
    st.error(f"Logo not found at {LOGO_PATH.resolve()}")

st.set_page_config(
    page_title="Starbucks LLM",
    layout="wide"
)

st.markdown(
    """
    <style>
    /* ===============================
       PAGE BACKGROUND (HF + LOCAL)
       =============================== */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #EAF4F1 !important;  /* Starbucks light green */
    }

    /* Remove default block backgrounds */
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
        color: #FFFFFF !important;
    }

    /* ===============================
       HEADERS & TEXT
       =============================== */
    .section-header {
        font-size: 22px;
        font-weight: 600;
        color: #00704A;
        margin-bottom: 6px;
    }

    .section-subtext {
        font-size: 16px;
        color: #1E3932;
        margin-bottom: 12px;
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
    </style>
    """,
    unsafe_allow_html=True
)




user_question = st.text_input(
    label="Ask a question about Starbucks menu items",
    placeholder="Example: Which Starbucks drink has the least sugar?",
    label_visibility="collapsed"
)


if st.button("Ask"):
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Contacting backend..."):
                response = requests.post(BACKEND_URL, json={"question": user_question})

            if response.status_code != 200:
                st.error(f"Backend error: {response.text}")
            else:
                data = response.json()

                # --- LLM Answer ---
                st.subheader("💬 LLM Answer")
                st.write(data.get("answer", "No answer returned."))

        except Exception as e:
            st.error(f"Error connecting to backend: {e}")