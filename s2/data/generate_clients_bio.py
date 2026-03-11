import psycopg2
from psycopg2.extras import execute_batch
from faker import Faker
from tqdm import tqdm
import random

DB_CONFIG = {
    'host': 'localhost',
    'port': 5438,
    'dbname': 'bakery_db_2_semester',
    'user': 'admin',
    'password': 'adminpass',
    'client_encoding': 'UTF8'
}

BATCH_SIZE = 1000
fake = Faker('ru_RU')

def generate_bio():
    # 10% остаётся NULL
    if random.random() < 0.1:
        return None
    return fake.paragraph(nb_sentences=3)

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT client_id
        FROM bakery_db.clients
        WHERE bio IS NULL
    """)

    ids = [row[0] for row in cur.fetchall()]

    update_sql = """
        UPDATE bakery_db.clients
        SET bio = %s
        WHERE client_id = %s
    """

    batch = []

    for client_id in tqdm(ids, desc="Updating bio"):
        batch.append((generate_bio(), client_id))

        if len(batch) >= BATCH_SIZE:
            execute_batch(cur, update_sql, batch)
            conn.commit()
            batch = []

    if batch:
        execute_batch(cur, update_sql, batch)
        conn.commit()

    cur.close()
    conn.close()

    print("Bio updated!")

if __name__ == "__main__":
    main()