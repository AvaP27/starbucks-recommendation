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

if LOGO_PATH.exists():
    logo = Image.open(LOGO_PATH)
    st.sidebar.image(logo, width=140)
else:
    st.error(f"Logo not found at {LOGO_PATH}")

st.markdown(
    """
    <style>
    /* Force full-page background on HF */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #EAF4F1 !important;
    }

    /* Main content container */
    [data-testid="stVerticalBlock"] {
        background-color: transparent;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h1 style='color:#00704A;'>Starbucks Recommendation System ☕</h1>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <style>
    /* Section header text */
    .section-header {
        font-size: 22px;
        font-weight: 600;
        color: #00704A; /* Starbucks green */
        margin-bottom: 6px;
    }

    /* Subtext / helper text */
    .section-subtext {
        font-size: 16px;
        color: #1E3932;
        margin-bottom: 12px;
    }

    /* Increase input font size */
    textarea, input {
        font-size: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Starbucks LLM", layout="wide")


st.markdown(
    """
    <div style="
        background-color:#F2F7F5;
        padding:20px;
        border-radius:12px;
        margin-top:10px;
        margin-bottom:20px;
    ">
        <div class='section-header'>☕ Ask a question about Starbucks menu items</div>
        <div class='section-subtext'>
            Type your question below (e.g., calories, caffeine, recommendations).
        </div>
    </div>
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