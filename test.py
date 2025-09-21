import os
import psycopg2

# Use the same DATABASE_URL as in Render environment
DB_URI = os.environ.get("DATABASE_URL",
    "postgresql://postgres:HOLYFUCKINGSHIT123@db.nzwplfahwbkefysxglrf.supabase.co:5432/postgres"
)

try:
    # Connect to database
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    result = cur.fetchone()
    print("Database connection successful:", result)
    cur.close()
    conn.close()
except Exception as e:
    print("Database connection failed:", e)
