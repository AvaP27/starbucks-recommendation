import pandas as pd
import sqlite3
import chromadb
from pathlib import Path

DATA_DIR = Path("data")
CSV_PATH = DATA_DIR / "starbucks.csv"
DB_PATH = DATA_DIR / "starbucks.db"

def ingest_data():
    print("Starting ingestion...")

    # Load CSV
    df = pd.read_csv(CSV_PATH)

    # Clean column names
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()

    # Store in SQLite
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("menu", conn, if_exists="replace", index=False)
    conn.close()

    # Store in Chroma (local persistent)
    client = chromadb.Client(
        settings=chromadb.Settings(
            persist_directory=str(DATA_DIR / "chroma")
        )
    )

    collection = client.get_or_create_collection("starbucks")

    for i, row in df.iterrows():
        text = (
            f"{row.get('beverage','')}: "
            f"calories={row.get('calories','N/A')}, "
            f"carbs={row.get('total_carbohydrates','N/A')}, "
            f"fat={row.get('total_fat','N/A')}"
        )
        collection.add(documents=[text], ids=[str(i)])

    print("Ingestion complete!")
