import psycopg2
from psycopg2.extras import execute_batch
from faker import Faker
import numpy as np
import random
import json
from datetime import datetime, timedelta

# Параметры подключения
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'bakery_db_2_semester',
    'user': 'admin',
    'password': 'adminpass'
}

NUM_ROWS = 300_000
BATCH_SIZE = 1000

fake = Faker('ru_RU')

# Список возможных client_id (должны существовать в таблице clients)
def get_client_ids(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT client_id FROM bakery_db.clients")
        return [row[0] for row in cur.fetchall()]

# Распределение рейтингов с перекосом: 70% - 5, 10% - 4, 7% - 3, 7% - 2, 6% - 1
rating_dist = [5]*70 + [4]*10 + [3]*7 + [2]*7 + [1]*6  # всего 100 элементов
random.shuffle(rating_dist)

# Возможные теги
tags_pool = ['вкусно', 'быстро', 'вежливо', 'грязно', 'дорого', 'акция', 'подарок', 'свежий']

def generate_row(client_ids):
    # client_id с равномерным распределением (можно сделать перекос, но пока равномерно)
    client_id = random.choice(client_ids)
    
    # Текст отзыва (иногда пустой для NULL, но лучше делать NULL отдельно)
    if random.random() < 0.1:  # 10% NULL
        feedback_text = None
    else:
        feedback_text = fake.paragraph(nb_sentences=3)
    
    # Рейтинг с перекосом
    rating = random.choice(rating_dist)
    
    # Массив тегов (от 0 до 4 тегов)
    num_tags = random.choices([0,1,2,3,4], weights=[10,30,30,20,10])[0]
    tags = random.sample(tags_pool, num_tags) if num_tags > 0 else None
    
    # JSON метаданных
    metadata = {
        'source': random.choice(['web', 'mobile', 'api']),
        'language': random.choice(['ru', 'en']),
        'device': random.choice(['desktop', 'tablet', 'mobile'])
    }
    metadata_json = json.dumps(metadata)
    
    # Геоточка (широта, долгота) – можно просто строка
    lat = round(random.uniform(55.0, 56.0), 6)
    lon = round(random.uniform(37.0, 38.0), 6)
    location = f'({lat},{lon})'  # формат для PostGIS POINT, но можно и так
    
    # Дата создания за последний год
    days_ago = random.randint(0, 365)
    created_at = datetime.now() - timedelta(days=days_ago)
    
    # is_verified – 15% NULL
    is_verified = None if random.random() < 0.15 else random.choice([True, False])
    
    return (client_id, feedback_text, rating, tags, metadata_json, location, created_at, is_verified)

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    client_ids = get_client_ids(conn)
    if not client_ids:
        print("Нет клиентов! Сначала заполните clients.")
        return
    
    cur = conn.cursor()
    insert_sql = """
        INSERT INTO bakery_db.customer_feedback 
        (client_id, feedback_text, rating, tags, metadata, location, created_at, is_verified)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    data_batch = []
    for i in range(1, NUM_ROWS + 1):
        data_batch.append(generate_row(client_ids))
        if i % BATCH_SIZE == 0:
            execute_batch(cur, insert_sql, data_batch)
            conn.commit()
            data_batch = []
            print(f"Обработано {i} записей")
    
    if data_batch:
        execute_batch(cur, insert_sql, data_batch)
        conn.commit()
    
    cur.close()
    conn.close()
    print("Готово!")

if __name__ == '__main__':
    main()