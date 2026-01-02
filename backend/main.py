from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI, RateLimitError, APIError
from dotenv import load_dotenv
import os
from pathlib import Path
from .db import sql_query   # SQL layer
from .rag import retrieve_documents # RAG layer
from .ingest_csv import ingest_data
from .ingest_docs import run_ingestion

import logging

# Silence Chroma telemetry logs
logging.getLogger("chromadb.telemetry").setLevel(logging.CRITICAL)
logging.getLogger("chromadb.telemetry.posthog").setLevel(logging.CRITICAL)

load_dotenv()

app = FastAPI()

DB_PATH = Path("data/starbucks.db")
CHROMA_PATH = Path("data/chroma")

@app.on_event("startup")
def startup_event():
    if not DB_PATH.exists():
        ingest_data()

    if not CHROMA_PATH.exists() or not any(CHROMA_PATH.iterdir()):
        run_ingestion()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Question(BaseModel):
    question: str


# --- OpenAI call ---
def call_model(prompt, model_name="gpt-4o"):
    return client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )


@app.post("/ask")
def ask_question(payload: Question):
    user_question = payload.question

    # 1️⃣ Try SQL first
    sql_result = sql_query(user_question)
    print("SQL RESULT:", sql_result)


    if sql_result["found"]:
        context_data = sql_result["data"]
        source = "SQL"

    else:
        docs = retrieve_documents(user_question)

        if docs:
            context_data = "\n".join(docs)
            source = "RAG"

        else:
            context_data = ""
            source = "STARBUCKS_LLM"


    # 2️⃣ Build guarded prompt

    prompt = f"""
    You are a Starbucks assistant.

    SOURCE TYPE: {source}

    CONTEXT DATA:
    {context_data if context_data else "No retrieved documents or SQL data."}

    QUESTION:
    {user_question}

    STRICT RULES (MUST FOLLOW):
    - Assume all beverages mentioned refer to Starbucks menu items unless clearly stated otherwise.
    - If a drink name exists on the Starbucks menu, treat the question as Starbucks-related.
    - Answer ONLY using Starbucks-related information.
    - If the question is completely unrelated to Starbucks beverages, menu items, or ingredients,
    respond with:
    "I can only answer questions related to Starbucks."
    - If CONTEXT DATA is provided, use ONLY that information.
    - If SOURCE TYPE is STARBUCKS_LLM, you may use general Starbucks knowledge,
    but do NOT make up specific numbers, prices, or nutrition facts.
    - Do NOT hallucinate.
    - Be concise and factual.
    """


    try:
        # 3️⃣ Primary model
        response = call_model(prompt, "gpt-4o")
        answer = response.choices[0].message.content

        return {
            "answer": answer,
            "source": source,
            "sql_results": sql_result["data"] if source == "SQL" else []
        }


    except RateLimitError:
        # 4️⃣ Fallback model
        try:
            response = call_model(prompt, "gpt-4o-mini")
            answer = response.choices[0].message.content
            return {
                "answer": answer,
                "sql_results": sql_result["data"] if sql_result["found"] else [],
                "warning": "Rate limited — used fallback model."
            }
        except Exception as e:
            return {"error": f"Fallback model failed: {e}"}

    except APIError as e:
        return {"error": f"OpenAI API error: {e}"}

    except Exception as e:
        return {"error": f"Unexpected backend error: {e}"}