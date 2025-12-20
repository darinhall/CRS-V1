import os
import sys
import psycopg2
from dotenv import load_dotenv

def main():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set")
        return

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    print("--- Verification Queries ---")

    # 1. Count Products
    cur.execute("SELECT COUNT(*) FROM products")
    print(f"Total Products: {cur.fetchone()[0]}")

    # 2. Count Specs
    cur.execute("SELECT COUNT(*) FROM product_specs")
    print(f"Total Spec Data Points: {cur.fetchone()[0]}")

    # 3. Example Filter: Cameras under 500g (assuming we have 'weight' spec mapped)
    # This requires knowing the spec_definition_id for 'weight', or joining
    query = """
    SELECT p.full_name, ps.numeric_value, ps.unit_used
    FROM products p
    JOIN product_specs ps ON p.id = ps.product_id
    JOIN spec_definitions sd ON ps.spec_definition_id = sd.id
    WHERE sd.normalized_key LIKE '%weight%' 
    AND ps.numeric_value < 500
    LIMIT 5;
    """
    try:
        cur.execute(query)
        rows = cur.fetchall()
        print(f"\nLightweight Cameras (<500g):")
        for row in rows:
            print(f"- {row[0]}: {row[1]} {row[2]}")
    except Exception as e:
        print(f"Query failed (might be no data): {e}")

    conn.close()

if __name__ == "__main__":
    main()
