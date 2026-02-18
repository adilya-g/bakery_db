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
    'password': 'adminpass'
}


NUM_BAKERIES = 250000
BATCH_SIZE = 100

fake = Faker('ru_RU')


def generate_bakery():
    name = fake.company() + " (пекарня)"

    address = fake.street_address() + ", " + fake.city()

    return (name, address)


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    insert_sql = """
        INSERT INTO bakery_db.bakeries (name, address)
        VALUES (%s, %s)
    """

    print(f"Генерация {NUM_BAKERIES} пекарен...")
    data_batch = []

    for i in tqdm(range(1, NUM_BAKERIES + 1), desc="Создание записей"):
        data_batch.append(generate_bakery())

        if i % BATCH_SIZE == 0:
            execute_batch(cur, insert_sql, data_batch)
            conn.commit()
            data_batch = []

    if data_batch:
        execute_batch(cur, insert_sql, data_batch)
        conn.commit()

    cur.close()
    conn.close()
    print("Готово!")


if __name__ == '__main__':
    main()