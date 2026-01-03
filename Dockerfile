FROM python:3.11-slim

# Disable Chroma telemetry
ENV CHROMA_TELEMETRY=FALSE

WORKDIR /app

# 🔧 Install system dependencies needed for chroma-hnswlib
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install backend deps
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install frontend deps
COPY frontend/requirements.txt frontend/requirements.txt
RUN pip install --no-cache-dir -r frontend/requirements.txt

# Copy application code and data
COPY backend backend
COPY frontend frontend
COPY data data
COPY assets assets

# Expose ports
EXPOSE 8000
EXPOSE 8501

# Start backend + frontend
CMD ["bash", "-c", "\
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 & \
    streamlit run frontend/app.py --server.address=0.0.0.0 --server.port=8501 \
"]
