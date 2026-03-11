#!/bin/bash

DB_CONTAINER="bakery_db_2_semester"
DB_USER="admin"
DB_NAME="bakery_db_2_semester"

echo "Starting load generation on bakery database..."
echo "Press Ctrl+C to stop"

# Функция для выполнения SQL
run_sql() {
    docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "$1" > /dev/null 2>&1
}

# Создаем расширение для статистики, если его нет
run_sql "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"

while true; do
    # 1. SELECT запросы с использованием новых типов данных
    for i in {1..15}; do
        # Поиск клиентов по JSON полям (preferences)
        run_sql "SELECT client_id, last_name, first_name, email, preferences->>'favorite_category' as fav_category
                 FROM bakery_db.clients 
                 WHERE preferences->>'notifications' = 'true'
                 LIMIT 10;"
        
        # Поиск работников по массиву навыков
        run_sql "SELECT worker_id, first_name, second_name, role, skills
                 FROM bakery_db.workers 
                 WHERE 'Baker' = ANY(skills) OR 'Manager' = ANY(skills)
                 LIMIT 10;"
        
        # Отзывы с тегами и метаданными
        run_sql "SELECT cf.feedback_id, c.last_name, c.first_name, cf.rating, cf.tags, cf.metadata->>'device' as device
                 FROM bakery_db.customer_feedback cf
                 JOIN bakery_db.clients c ON cf.client_id = c.client_id
                 WHERE cf.is_verified = true
                 ORDER BY cf.created_at DESC
                 LIMIT 10;"
        
        # Геопоиск клиентов рядом с точкой
        run_sql "SELECT client_id, last_name, first_name, location <-> POINT(55.75, 37.62) as distance
                 FROM bakery_db.clients 
                 WHERE location IS NOT NULL
                 ORDER BY distance
                 LIMIT 10;"
        
        # Статистика по loyalty баллам клиентов
        run_sql "SELECT status, AVG(loyalty_points) as avg_points, COUNT(*) as count
                 FROM bakery_db.clients 
                 GROUP BY status
                 ORDER BY avg_points DESC;"
        
        # Поиск по bio (текстовый поиск)
        run_sql "SELECT worker_id, first_name, second_name, bio
                 FROM bakery_db.workers 
                 WHERE bio ILIKE '%experience%' OR bio ILIKE '%senior%'
                 LIMIT 10;"
        
        # Агрегация по тегам в отзывах
        run_sql "SELECT unnest(tags) as tag, COUNT(*) as count, AVG(rating) as avg_rating
                 FROM bakery_db.customer_feedback
                 WHERE tags IS NOT NULL
                 GROUP BY tag
                 ORDER BY count DESC
                 LIMIT 10;"
        
        # Клиенты с email доменами
        run_sql "SELECT SUBSTRING(email FROM '@(.*)$') as email_domain, COUNT(*) as count
                 FROM bakery_db.clients 
                 WHERE email IS NOT NULL
                 GROUP BY email_domain
                 ORDER BY count DESC;"
        
        # Работники по дате найма
        run_sql "SELECT first_name, second_name, role, hire_date, 
                 EXTRACT(YEAR FROM age(hire_date)) as years_worked
                 FROM bakery_db.workers 
                 WHERE hire_date > '2020-01-01'
                 ORDER BY hire_date;"
        
        # Отзывы с высоким рейтингом и их метаданные
        run_sql "SELECT c.last_name, cf.rating, cf.tags, cf.metadata->>'source' as source
                 FROM bakery_db.customer_feedback cf
                 JOIN bakery_db.clients c ON cf.client_id = c.client_id
                 WHERE cf.rating >= 4 AND cf.metadata->>'verified_purchase' = 'true'
                 LIMIT 15;"
    done
    
    # 2. INSERT запросы с новыми типами данных
    for i in {1..3}; do
        # Добавляем нового клиента со всеми полями
        NAME_SUFFIX=$((RANDOM % 1000))
        LOYALTY_POINTS=$((RANDOM % 1000))
        STATUSES=("active" "inactive" "vip" "regular")
        STATUS=${STATUSES[$((RANDOM % 4))]}
        
        run_sql "
            INSERT INTO bakery_db.clients (
                phone_number, last_name, first_name, middle_name, birth_date,
                email, status, registration_date, preferences, location, bio, loyalty_points
            ) VALUES (
                '79' || LPAD($((RANDOM % 1000000000))::text, 9, '0'),
                'Иванов' || $NAME_SUFFIX,
                'Иван' || $NAME_SUFFIX,
                'Иванович' || $NAME_SUFFIX,
                DATE '1970-01-01' + ($((RANDOM % 15000)) || ' days')::interval,
                'user' || $NAME_SUFFIX || '@example.com',
                '$STATUS',
                CURRENT_DATE - ($((RANDOM % 365)) || ' days')::interval,
                '{\"notifications\": $((RANDOM % 2 == 0)), \"language\": \"ru\", \"favorite_category\": \"pastry\"}'::jsonb,
                POINT(55.75 + random()/10, 37.62 + random()/10),
                'Regular customer with ' || $LOYALTY_POINTS || ' points',
                $LOYALTY_POINTS
            );"
        
        # Добавляем нового работника со всеми полями
        BAKERY_ID=$((RANDOM % 5 + 1))
        ROLES=("Baker" "Manager" "Cashier" "Cleaner" "Technologist")
        ROLE=${ROLES[$((RANDOM % 5))]}
        SALARY=$((50000 + RANDOM % 50000))
        SKILLS_ARRAY=("{Baker,Cleaning}" "{Manager,Planning}" "{Cashier,Communication}" "{Cleaner,Efficient}" "{Technologist,Quality}")
        SKILLS=${SKILLS_ARRAY[$((RANDOM % 5))]}
        
        run_sql "
            INSERT INTO bakery_db.workers (
                role, phone_number, first_name, second_name, date_of_birth, bakery_id,
                email, status, hire_date, skills, location, bio, salary
            ) VALUES (
                '$ROLE',
                '79' || LPAD($((RANDOM % 1000000000))::text, 9, '0'),
                'Петр' || $((RANDOM % 100)),
                'Петров' || $((RANDOM % 100)),
                DATE '1980-01-01' + ($((RANDOM % 12000)) || ' days')::interval,
                $BAKERY_ID,
                'worker' || $((RANDOM % 1000)) || '@bakery.com',
                'active',
                CURRENT_DATE - ($((RANDOM % 1000)) || ' days')::interval,
                '$SKILLS'::text[],
                POINT(55.75 + random()/10, 37.62 + random()/10),
                'Experienced $ROLE with ' || $((RANDOM % 10 + 1)) || ' years of experience',
                $SALARY
            );"
        
        # Добавляем отзыв со всеми полями
        CLIENT_ID=$((RANDOM % 1000 + 1))
        RATING=$((RANDOM % 5 + 1))
        TAGS_ARRAY=("{tasty,service}" "{fast,quality}" "{delicious,friendly}" "{fresh,good}" "{recommend,great}")
        TAGS=${TAGS_ARRAY[$((RANDOM % 5))]}
        
        run_sql "
            INSERT INTO bakery_db.customer_feedback (
                client_id, feedback_text, rating, tags, metadata, location, created_at, is_verified
            ) VALUES (
                $CLIENT_ID,
                'Great experience with order #' || $((RANDOM % 1000)),
                $RATING,
                '$TAGS'::text[],
                ('{\"source\": \"' || 
                 CASE WHEN random() > 0.5 THEN 'web' ELSE 'mobile' END || 
                 '\", \"verified_purchase\": ' || 
                 CASE WHEN random() > 0.3 THEN 'true' ELSE 'false' END || 
                 ', \"device\": \"' ||
                 CASE WHEN random() > 0.5 THEN 'iOS' ELSE 'Android' END ||
                 '\"}')::jsonb,
                POINT(55.75 + random()/10, 37.62 + random()/10),
                NOW() - ($((RANDOM % 30)) || ' days')::interval,
                random() > 0.2
            );"
    done
    
    # 3. UPDATE запросы с новыми полями
    for i in {1..2}; do
        # Обновляем JSON поле клиента
        run_sql "
            UPDATE bakery_db.clients 
            SET preferences = preferences || '{\"last_visit\": \"' || NOW()::text || '\"}',
                loyalty_points = loyalty_points + 10,
                status = CASE 
                    WHEN loyalty_points > 500 THEN 'vip'
                    WHEN loyalty_points > 100 THEN 'regular'
                    ELSE 'new'
                END
            WHERE client_id = (SELECT client_id FROM bakery_db.clients ORDER BY random() LIMIT 1);"
        
        # Обновляем массив навыков работника
        run_sql "
            UPDATE bakery_db.workers 
            SET skills = array_append(skills, 
                CASE WHEN random() > 0.5 THEN 'NewSkill' || $((RANDOM % 10))
                ELSE 'Advanced' || $((RANDOM % 10)) END
            ),
            salary = salary * (1 + 0.1 * random()),
            status = 'experienced'
            WHERE worker_id = (SELECT worker_id FROM bakery_db.workers ORDER BY random() LIMIT 1);"
        
        # Обновляем метаданные отзыва
        run_sql "
            UPDATE bakery_db.customer_feedback 
            SET metadata = metadata || '{\"review_updated\": true, \"updated_at\": \"' || NOW()::text || '\"}',
                is_verified = true
            WHERE feedback_id = (SELECT feedback_id FROM bakery_db.customer_feedback ORDER BY random() LIMIT 1);"
    done
    
    # 4. DELETE запросы - МАКСИМАЛЬНО ПРОСТЫЕ
    if (( RANDOM % 15 == 0 )); then
        # Просто удаляем 1 случайного неактивного клиента
        run_sql "
            DELETE FROM bakery_db.clients 
            WHERE status = 'inactive' 
            LIMIT 1;"
        
        # Просто удаляем 1 случайного работника с зарплатой меньше 40000
        run_sql "
            DELETE FROM bakery_db.workers 
            WHERE salary < 40000 
            LIMIT 1;"
        
        # Просто удаляем 1 старый неподтвержденный отзыв
        run_sql "
            DELETE FROM bakery_db.customer_feedback 
            WHERE is_verified = false
            AND created_at < NOW() - INTERVAL '6 months'
            LIMIT 1;"
    fi
    
    # Показываем статус с новыми метриками
    if (( RANDOM % 20 == 0 )); then
        active=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "
            SELECT count(*) FROM pg_stat_activity 
            WHERE state = 'active' AND datname = '$DB_NAME';" | tr -d ' ')
        
        clients=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "
            SELECT count(*) FROM bakery_db.clients;" | tr -d ' ')
        
        workers=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "
            SELECT count(*) FROM bakery_db.workers;" | tr -d ' ')
        
        feedbacks=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "
            SELECT count(*) FROM bakery_db.customer_feedback;" | tr -d ' ')
        
        vip_clients=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "
            SELECT count(*) FROM bakery_db.clients WHERE status = 'vip';" | tr -d ' ')
        
        echo "[$(date '+%H:%M:%S')] Active: $active | Clients: $clients (VIP: $vip_clients) | Workers: $workers | Feedbacks: $feedbacks"
    fi
    
    sleep 0.3
done