import psycopg2
from psycopg2.extras import execute_batch
from faker import Faker
from tqdm import tqdm
import random
import json
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'bakery_db_2_semester',
    'user': 'admin',
    'password': 'adminpass'  
}

NUM_CLIENTS = 300_000
BATCH_SIZE = 1000

fake = Faker('ru_RU')

# Возможные статусы с весами для перекоса (70% active, 20% inactive, 10% vip)
STATUSES = ['active', 'inactive', 'vip']
STATUS_WEIGHTS = [0.7, 0.2, 0.1]

def generate_client():
    phone = '7' + ''.join([str(random.randint(0, 9)) for _ in range(10)])
    last_name = fake.last_name()
    first_name = fake.first_name()
    middle_name = fake.middle_name()
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)

    # Email: почти уникальный (высокая кардинальность)
    email = fake.unique.email()

    # Статус: низкая кардинальность с перекосом
    status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]

    # Дата регистрации: равномерно за последние 5 лет
    days_ago = random.randint(0, 5*365)
    registration_date = datetime.now() - timedelta(days=days_ago)

    # JSONB preferences: случайная структура
    preferences = {
        'newsletter': random.choice([True, False]),
        'theme': random.choice(['light', 'dark']),
        'notifications': random.choice(['email', 'sms', 'none'])
    }
    preferences_json = json.dumps(preferences)

    # Геоточка (широта, долгота) в пределах Москвы
    lat = round(random.uniform(55.5, 56.0), 6)
    lon = round(random.uniform(37.3, 37.9), 6)
    location = f'POINT({lon} {lat})'  # формат для PostGIS

    # Био (полнотекст) – 10% NULL
    if random.random() < 0.1:
        bio = None
    else:
        bio = fake.paragraph(nb_sentences=3)

    # Баллы лояльности – 20% NULL
    if random.random() < 0.2:
        loyalty_points = None
    else:
        loyalty_points = random.randint(0, 1000)

    return (phone, last_name, first_name, middle_name, birth_date,
            email, status, registration_date, preferences_json,
            location, bio, loyalty_points)

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    insert_sql = """
        INSERT INTO bakery_db.clients 
        (phone_number, last_name, first_name, middle_name, birth_date,
         email, status, registration_date, preferences, location, bio, loyalty_points)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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