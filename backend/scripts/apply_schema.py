"""Apply Supabase schema from supabase/schema.sql to the project's database.

Usage:
  1. Add your Supabase DB connection string to backend/.env as SUPABASE_DB_URL (recommended)
     or set the environment variable SUPABASE_DB_URL or DATABASE_URL.
  2. Activate your virtualenv and install psycopg2:
       pip install psycopg2-binary python-dotenv
  3. Run:
       python backend/scripts/apply_schema.py

Security:
  - The DB connection string contains a password. Keep it out of source control.
  - Prefer using the Supabase SQL editor for convenience if you don't want to store the DB URL locally.

This script reads `supabase/schema.sql` and executes its SQL in a single transaction.
"""
from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# Load .env from backend folder if present
# Script is in backend/scripts/, so go up 1 level to backend/, then up 1 more to repo root
BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
env_path = BACKEND_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

DB_URL = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")
if not DB_URL:
    print("ERROR: No SUPABASE_DB_URL or DATABASE_URL environment variable found.")
    print("Please add your Supabase DB connection string to backend/.env as SUPABASE_DB_URL or export it in your shell.")
    print(f"Looked for .env at: {env_path}")
    sys.exit(1)

sql_path = REPO_ROOT / "supabase" / "schema.sql"
if not sql_path.exists():
    print(f"ERROR: schema.sql not found at {sql_path}")
    sys.exit(1)

sql_text = sql_path.read_text()

print("Connecting to database...")

try:
    import psycopg2
    from psycopg2 import sql
except Exception as e:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

conn = None
try:
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    cur = conn.cursor()
    print("Executing schema.sql (this may take a few seconds)...")
    cur.execute(sql.SQL(sql_text))
    conn.commit()
    print("Schema applied successfully.")
except Exception as exc:
    if conn:
        conn.rollback()
    print("ERROR applying schema:")
    print(exc)
    sys.exit(1)
finally:
    if conn:
        conn.close()
