import psycopg2
from psycopg2.extras import execute_batch
from faker import Faker
from tqdm import tqdm
import random
import numpy as np
from datetime import datetime, timedelta
import json  # если понадобится для других форматов

# Конфигурация подключения (порт 5438, как в вашем исходном коде)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5438,
    'dbname': 'bakery_db_2_semester',
    'user': 'admin',
    'password': 'adminpass'
}

# Количество работников и размер пачки
NUM_WORKERS = 400_000
BATCH_SIZE = 1000

fake = Faker('ru_RU')

# Роли (оставляем без изменений)
ROLES = [
    'пекарь', 'кондитер', 'тестомес', 'упаковщик', 'продавец',
    'кассир', 'менеджер', 'уборщик', 'грузчик', 'технолог',
    'кладовщик', 'водитель', 'администратор', 'стажёр'
]

# Статусы с перекосом (70% active, 20% inactive, 10% on_leave)
STATUSES = ['active', 'inactive', 'on_leave']
STATUS_WEIGHTS = [0.7, 0.2, 0.1]

# Набор навыков (для массива)
SKILLS_POOL = [
    'работа с тестом', 'управление печью', 'упаковка', 'обслуживание клиентов',
    'работа с кассой', 'водительские права', 'знание рецептур', 'санитарные нормы',
    'закупка продуктов', 'управление персоналом', 'логистика', 'английский язык'
]

def get_bakery_ids_with_weights(conn):
    """
    Возвращает два списка: bakery_ids и соответствующие веса для Zipf-подобного распределения.
    Веса пропорциональны 1/(rank), что даёт сильный перекос: первые пекарни получают много работников.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT bakery_id FROM bakery_db.bakeries ORDER BY bakery_id")
        rows = cur.fetchall()
        bakery_ids = [row[0] for row in rows]
    
    if not bakery_ids:
        return [], []
    
    # Создаём веса: чем меньше индекс, тем больше вес (популярнее пекарня)
    n = len(bakery_ids)
    # Используем степенной закон с показателем 1 (Zipf)
    ranks = np.arange(1, n + 1)
    weights = 1.0 / ranks
    weights = weights / weights.sum()  # нормализация
    return bakery_ids, weights


def generate_worker(bakery_ids, bakery_weights):
    """
    Генерирует одного работника со всеми новыми полями.
    """
    # --- Поля из старой версии ---
    role = random.choice(ROLES)
    phone = '7' + ''.join(str(random.randint(0, 9)) for _ in range(10))
    first_name = fake.first_name()
    second_name = fake.last_name()
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=65)

    # Неравномерное распределение по пекарням (используем веса)
    # Явное преобразование numpy.int64 -> int
    bakery_id = int(np.random.choice(bakery_ids, p=bakery_weights))

    # --- Новые поля ---
    email = fake.unique.email()
    status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
    days_ago = random.randint(0, 10 * 365)
    hire_date = datetime.now() - timedelta(days=days_ago)

    # Навыки (массив) – 15% NULL, иначе от 1 до 4 навыков
    if random.random() < 0.15:
        skills = None
    else:
        num_skills = random.randint(1, 4)
        skills = random.sample(SKILLS_POOL, num_skills)

    # Геоточка (POINT) – координаты в пределах Москвы
    lat = round(random.uniform(55.5, 56.0), 6)
    lon = round(random.uniform(37.3, 37.9), 6)
    location = f'({lon},{lat})'  # строка вида (37.856334,55.942064)


    # Био (полнотекст) – 10% NULL
    if random.random() < 0.1:
        bio = None
    else:
        bio = fake.paragraph(nb_sentences=3)

    # Зарплата – 20% NULL, иначе случайное число от 30000 до 150000
    if random.random() < 0.2:
        salary = None
    else:
        salary = round(random.uniform(30000, 150000), 2)

    return (role, phone, first_name, second_name, birth_date, bakery_id,
            email, status, hire_date, skills, location, bio, salary)
def main():
    conn = psycopg2.connect(**DB_CONFIG)
    
    # Получаем список пекарен и веса для неравномерного распределения
    print("Загружаем список пекарен и вычисляем веса...")
    bakery_ids, bakery_weights = get_bakery_ids_with_weights(conn)
    if not bakery_ids:
        print("Ошибка: таблица bakeries пуста. Сначала заполните пекарни.")
        return
    print(f"Найдено пекарен: {len(bakery_ids)}")
    print(f"Пример весов (первые 5): {bakery_weights[:5]}")

    cur = conn.cursor()
    insert_sql = """
        INSERT INTO bakery_db.workers 
        (role, phone_number, first_name, second_name, date_of_birth, bakery_id,
         email, status, hire_date, skills, location, bio, salary)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    print(f"Генерация {NUM_WORKERS} работников...")
    data_batch = []

    for i in tqdm(range(1, NUM_WORKERS + 1), desc="Создание записей"):
        data_batch.append(generate_worker(bakery_ids, bakery_weights))

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