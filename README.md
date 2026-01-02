---
title: Starbucks GenAI Assistant
emoji: ☕
colorFrom: yellow
colorTo: red
sdk: docker
app_port: 8501
pinned: false
---

# ☕ Starbucks GenAI Assistant

A full-stack GenAI application using:
- Streamlit (UI)
- FastAPI (backend)
- SQLite + ChromaDB
- Docker

## Run locally
```bash
docker build -t starbucks-genai .
docker run -p 8000:8000 -p 8501:8501 \
  -e OPENAI_API_KEY=your_key \
  starbucks-genai
