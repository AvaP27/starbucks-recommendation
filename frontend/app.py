import streamlit as st
import requests
import pandas as pd
import os
import socket

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

st.set_page_config(page_title="Starbucks LLM", layout="wide")

st.title("☕ Starbucks LLM Assistant")
st.write("Ask a question about Starbucks menu items.")

user_question = st.text_input("Enter your question")

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

                # --- SQL Results ---
                if "sql_results" in data and data["sql_results"]:
                    st.subheader("📊 SQL Results")
                    df = pd.DataFrame(data["sql_results"])
                    st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Error connecting to backend: {e}")