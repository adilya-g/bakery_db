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


NUM_WORKERS = 400_000
BATCH_SIZE = 1000

fake = Faker('ru_RU')


ROLES = [
    'пекарь', 'кондитер', 'тестомес', 'упаковщик', 'продавец',
    'кассир', 'менеджер', 'уборщик', 'грузчик', 'технолог',
    'кладовщик', 'водитель', 'администратор', 'стажёр'
]


def get_bakery_ids(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT bakery_id FROM bakery_db.bakeries")
        rows = cur.fetchall()
        return [row[0] for row in rows]


def generate_worker(bakery_ids):
    role = random.choice(ROLES)
    phone = '7' + ''.join(str(random.randint(0, 9)) for _ in range(10))
    first_name = fake.first_name()
    second_name = fake.last_name()
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=65)
    bakery_id = random.choice(bakery_ids)
    return (role, phone, first_name, second_name, birth_date, bakery_id)


def main():
    conn = psycopg2.connect(**DB_CONFIG)

    print("Загружаем список пекарен...")
    bakery_ids = get_bakery_ids(conn)
    if not bakery_ids:
        print("Ошибка: таблица bakeries пуста. Сначала заполните пекарни.")
        return
    print(f"Найдено пекарен: {len(bakery_ids)}")

    cur = conn.cursor()
    insert_sql = """
        INSERT INTO bakery_db.workers 
        (role, phone_number, first_name, second_name, date_of_birth, bakery_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    print(f"Генерация {NUM_WORKERS} работников...")
    data_batch = []

    for i in tqdm(range(1, NUM_WORKERS + 1), desc="Создание записей"):
        data_batch.append(generate_worker(bakery_ids))

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