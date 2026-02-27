## SQL запросы (>, <, =, %like, like%, IN)
``` sql
SELECT * FROM BAKERY_DB.WORKERS 
WHERE DATE_OF_BIRTH > '1999-01-01';

SELECT * FROM BAKERY_DB.WORKERS 
WHERE DATE_OF_BIRTH < '1999-01-01';

UPDATE BAKERY_DB.WORKERS 
SET EMAIL = 'defaultemail@gmail.com'
WHERE worker_id = 1000;

SELECT * FROM BAKERY_DB.CLIENTS 
WHERE FIRST_NAME LIKE 'Ир%';

SELECT * FROM BAKERY_DB.WORKERS 
WHERE SECOND_NAME LIKE '%ва';

SELECT * FROM BAKERY_DB.CUSTOMER_FEEDBACK 
WHERE DATE(CREATED_AT) IN ('2025-01-01', '2025-01-15', '2025-02-01');
```
## ДЛЯ ПОИСКА РАБОТНИКОВ С ДАТОЙ РОЖДЕНИЯ > 1999-01-01
``` sql
EXPLAIN SELECT * FROM BAKERY_DB.WORKERS WHERE DATE_OF_BIRTH > '1999-01-01';

EXPLAIN ANALYZE SELECT * FROM BAKERY_DB.WORKERS WHERE DATE_OF_BIRTH > '1999-01-01';

EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM BAKERY_DB.WORKERS WHERE DATE_OF_BIRTH > '1999-01-01';

CREATE INDEX idx_workers_birth ON bakery_db.workers(date_of_birth);

DROP INDEX IF EXISTS bakery_db.idx_workers_birth;

CREATE INDEX idx_workers_birth_hash ON bakery_db.workers USING HASH (date_of_birth);
```
#### Без индекса:
![alt text](image.png)
![alt text](image-1.png)
![alt text](image-2.png)
#### С индексом b-tree:
![alt text](image-20.png)
#### С индексом hash:
![alt text](image-36.png)


## EXPLAIN ДЛЯ ПОИСКА РАБОТНИКОВ С ДАТОЙ РОЖДЕНИЯ < 1999-01-01
``` sql
EXPLAIN SELECT * FROM BAKERY_DB.WORKERS WHERE DATE_OF_BIRTH < '1999-01-01';

EXPLAIN ANALYZE SELECT * FROM BAKERY_DB.WORKERS WHERE DATE_OF_BIRTH < '1999-01-01';

EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM BAKERY_DB.WORKERS WHERE DATE_OF_BIRTH < '1999-01-01';

CREATE INDEX idx_workers_birth ON bakery_db.workers(date_of_birth);

DROP INDEX IF EXISTS bakery_db.idx_workers_birth;

CREATE INDEX idx_workers_birth_hash ON bakery_db.workers USING HASH (date_of_birth);
```
#### Без индекса
![alt text](image-3.png)
![alt text](image-4.png)
![alt text](image-5.png)
#### С индексом b-tree:
![alt text](image-23.png)
#### С индексом hash:
![alt text](image-37.png)

## ДЛЯ ОБНОВЛЕНИЯ EMAIL
``` sql
EXPLAIN UPDATE BAKERY_DB.WORKERS 
SET EMAIL = 'defaultemail@gmail.com'
WHERE worker_id = 1000;

EXPLAIN ANALYZE UPDATE BAKERY_DB.WORKERS 
SET EMAIL = 'defaultemail@gmail.com'
WHERE worker_id = 1000;

EXPLAIN (ANALYZE, BUFFERS) UPDATE BAKERY_DB.WORKERS 
SET EMAIL = 'defaultemail@gmail.com'
WHERE worker_id = 1000;

CREATE INDEX idx_workers_email ON bakery_db.workers(email);

DROP INDEX IF EXISTS bakery_db.idx_workers_email;

CREATE INDEX idx_workers_email_hash ON bakery_db.workers USING HASH (email);
```
#### Без индекса
![alt text](image-6.png)
![alt text](image-7.png)
![alt text](image-8.png)
#### С индексом b-tree:
![alt text](image-26.png)
#### С индексом hash:
![alt text](image-38.png)

## ДЛЯ ПОИСКА КЛИЕНТОВ ПО ИМЕНИ, НАЧИНАЮЩЕГОСЯ С "ИР"
``` sql
EXPLAIN SELECT * FROM BAKERY_DB.CLIENTS 
WHERE FIRST_NAME LIKE 'Ир%';

EXPLAIN ANALYZE SELECT * FROM BAKERY_DB.CLIENTS 
WHERE FIRST_NAME LIKE 'Ир%';

EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM BAKERY_DB.CLIENTS 
WHERE FIRST_NAME LIKE 'Ир%';

CREATE INDEX idx_clients_first_name ON bakery_db.clients(first_name);

DROP INDEX IF EXISTS bakery_db.idx_clients_first_name;

CREATE INDEX idx_clients_first_name_hash ON bakery_db.clients USING HASH (first_name);
```
#### Без индекса
![alt text](image-9.png)
![alt text](image-10.png)
![alt text](image-11.png)
#### С индексом b-tree:
![alt text](image-29.png)
#### С индексом hash:
![alt text](image-39.png)

## ДЛЯ ПОИСКА РАБОТНИКОВ ПО ФАМИЛИИ, ЗАКАНЧИВАЮЩЕЙСЯ НА "ВА"
``` sql
EXPLAIN SELECT * FROM BAKERY_DB.WORKERS 
WHERE SECOND_NAME LIKE '%ва';

EXPLAIN ANALYZE SELECT * FROM BAKERY_DB.WORKERS 
WHERE SECOND_NAME LIKE '%ва';

EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM BAKERY_DB.WORKERS 
WHERE SECOND_NAME LIKE '%ва';

CREATE INDEX idx_workers_second_name ON bakery_db.workers(second_name);

DROP INDEX IF EXISTS bakery_db.idx_workers_second_name;

CREATE INDEX idx_workers_second_name_hash ON bakery_db.workers USING HASH (second_name);
```
#### Без индекса
![alt text](image-12.png)
![alt text](image-13.png)
![alt text](image-14.png)
#### С индексом b-tree:
![alt text](image-32.png)
#### С индексом hash:
![alt text](image-40.png)

## ДЛЯ ПОИСКА ОТЗЫВОВ ПО ДАТАМ
``` sql
EXPLAIN SELECT * FROM BAKERY_DB.CUSTOMER_FEEDBACK 
WHERE DATE(CREATED_AT) IN ('2025-01-01', '2025-01-15', '2025-02-01');

EXPLAIN ANALYZE SELECT * FROM BAKERY_DB.CUSTOMER_FEEDBACK 
WHERE DATE(CREATED_AT) IN ('2025-01-01', '2025-01-15', '2025-02-01');

EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM BAKERY_DB.CUSTOMER_FEEDBACK 
WHERE DATE(CREATED_AT) IN ('2025-01-01', '2025-01-15', '2025-02-01');

CREATE INDEX idx_customer_feedback_created_at ON bakery_db.customer_feedback(created_at);

DROP INDEX IF EXISTS bakery_db.idx_customer_feedback_created_at;

CREATE INDEX idx_customer_feedback_created_at_hash ON bakery_db.customer_feedback USING HASH (created_at);
```
#### Без индекса
![alt text](image-15.png)
![alt text](image-16.png)
![alt text](image-17.png)
#### С индексом b-tree:
![alt text](image-35.png)
#### С индексом hash:
![alt text](image-41.png)

