import sqlite3
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# Paths (ROBUST)
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent   # project root
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "starbucks.db"   # must match ingestion filename

# =========================
# Constants
# =========================
KNOWN_DRINKS = [
    "latte", "cappuccino", "mocha", "espresso",
    "americano", "macchiato", "frappuccino"
]


def sql_query(user_question: str) -> dict:
    print(f"[DB] Question received: {user_question}")

    if not DB_PATH.exists():
        logger.error(f"[DB] Database not found at {DB_PATH}")
        return {"found": False, "type": None, "data": None}

    q = user_question.lower()

    conn = sqlite3.connect(DB_PATH)

    try:
        # --- Extract drink name ---
        drink = None
        for d in KNOWN_DRINKS:
            if d in q:
                drink = d
                break

        print(f"[DB] Detected drink: {drink}")

        # --- FAT query ---
        if drink and any(k in q for k in ["fat", "trans fat"]):
            logger.info("[DB] Running FAT query")

            df = pd.read_sql(
                """
                SELECT beverage, total_fat
                FROM menu
                WHERE LOWER(beverage) LIKE ?
                """,
                conn,
                params=[f"%{drink}%"]
            )

            print(f"[DB] Rows returned: {len(df)}")

            if not df.empty:
                return {
                    "found": True,
                    "type": "fat",
                    "data": df.to_dict(orient="records")
                }

        # --- CALORIES query ---
        if drink and "calorie" in q:
            logger.info("[DB] Running CALORIES query")

            df = pd.read_sql(
                """
                SELECT beverage, calories
                FROM menu
                WHERE LOWER(beverage) LIKE ?
                """,
                conn,
                params=[f"%{drink}%"]
            )

            if not df.empty:
                return {
                    "found": True,
                    "type": "calories",
                    "data": df.to_dict(orient="records")
                }

        logger.info("[DB] No SQL match found")
        return {"found": False, "type": None, "data": None}

    except Exception as e:
        logger.exception("[DB] ERROR during SQL query")
        return {"found": False, "type": None, "data": None}

    finally:
        conn.close()
