import streamlit as st
import requests
import socket
from pathlib import Path


# =========================================================
# PAGE CONFIG (MUST BE FIRST)
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
    else "http://127.0.0.1:8000/ask"
"
)


# =========================================================
# GLOBAL CSS  (MINIMAL & SAFE)
# =========================================================
st.markdown(
    """
    <style>
    /* Page background */
    html, body, .stApp {
        background-color: #EAF4F1;
    }

    /* Inputs */
    input, textarea {
        background-color: #FFFFFF !important;
        color: #1E3932 !important;
        border-radius: 8px !important;
        border: 1px solid #C7DCD2 !important;
        font-size: 16px !important;
    }

    /* Buttons */
    button {
        background-color: #00704A !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR LOGO  (STREAMLIT-NATIVE ONLY)
# =========================================================
with st.sidebar:
    st.markdown("### ☕ Starbucks")

    logo_path = Path(__file__).resolve().parent.parent / "assets" / "starbucks_logo.png"

    if logo_path.exists():
        st.image(str(logo_path), width=140)
    else:
        st.warning("Logo file not found")


# =========================================================
# MAIN CONTENT (STREAMLIT-NATIVE ONLY)
# =========================================================
st.title("☕ Starbucks Recommendation System")
st.subheader("Ask a question about Starbucks menu items")
st.caption("Examples: calories, caffeine, sugar-free drinks, recommendations")

user_question = st.text_input(
    label="Your question",
    placeholder="Which Starbucks drink has the least sugar?",
    label_visibility="collapsed"
)


# =========================================================
# ASK BUTTON & RESPONSE
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

            # ✅ STREAMLIT-NATIVE ANSWER RENDERING
            st.markdown("### 💬 LLM Answer")
            st.markdown(answer)

    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
