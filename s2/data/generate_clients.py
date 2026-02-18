import psycopg2
from psycopg2.extras import execute_batch
from faker import Faker
from tqdm import tqdm
import random


DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'bakery_db_2_semester',
    'user': 'admin',
    'password': 'adminpasss'
}


NUM_CLIENTS = 300_000
BATCH_SIZE = 1000


fake = Faker('ru_RU')


def generate_client():
    phone = '7' + ''.join([str(random.randint(0, 9)) for _ in range(10)])

    last_name = fake.last_name()
    first_name = fake.first_name()
    middle_name = fake.middle_name()  # доступно в ru_RU

    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)

    return (phone, last_name, first_name, middle_name, birth_date)


def main():
    conn = psycopg2.connect("host=localhost port=5438 dbname=bakery_db_2_semester user=admin password=adminpass")
    cur = conn.cursor()

    insert_sql = """
        INSERT INTO bakery_db.clients 
        (phone_number, last_name, first_name, middle_name, birth_date)
        VALUES (%s, %s, %s, %s, %s)
    """

    print(f"Генерация {NUM_CLIENTS} клиентов...")
    data_batch = []

    for i in tqdm(range(1, NUM_CLIENTS + 1), desc="Создание записей"):
        data_batch.append(generate_client())

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