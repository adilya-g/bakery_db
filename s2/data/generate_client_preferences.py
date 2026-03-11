import psycopg2
from psycopg2.extras import execute_batch
import random
import json
from tqdm import tqdm

DB_CONFIG = {
    'host': 'localhost',
    'port': 5438,
    'dbname': 'bakery_db_2_semester',
    'user': 'admin',
    'password': 'adminpass',
    'client_encoding': 'UTF8'
}

BATCH_SIZE = 1000

def generate_preferences():
    preferences = {
        'newsletter': random.choice([True, False]),
        'theme': random.choice(['light', 'dark']),
        'notifications': random.choice(['email', 'sms', 'none'])
    }
    return json.dumps(preferences)

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Получаем id строк где preferences NULL
    cur.execute("""
        SELECT client_id
        FROM bakery_db.clients
        WHERE preferences IS NULL
    """)

    ids = [row[0] for row in cur.fetchall()]

    update_sql = """
        UPDATE bakery_db.clients
        SET preferences = %s
        WHERE client_id = %s
    """

    batch = []

    for client_id in tqdm(ids, desc="Updating preferences"):
        batch.append((generate_preferences(), client_id))

        if len(batch) >= BATCH_SIZE:
            execute_batch(cur, update_sql, batch)
            conn.commit()
            batch = []

    if batch:
        execute_batch(cur, update_sql, batch)
        conn.commit()

    cur.close()
    conn.close()

    print("Preferences updated!")

if __name__ == "__main__":
    main()