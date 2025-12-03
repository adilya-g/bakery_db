# Транзакции

### Запросы с **COMMIT**
1) Добавляет клиента и оформляет на него заказ
 ``` sql
BEGIN;
INSERT INTO bakery_db.clients(phone_number, last_name, middle_name, first_name, birth_date) VALUES ('89083356464', 'Галимзянова', 'Адиля', 'Айдаровна', '10.01.2007');
UPDATE bakery_db.orders SET client_id = 15 WHERE order_id = 50;
COMMIT;
```
![alt text](img/transaction_1.png)
![alt text](img/transaction_2.png)

2) Перенаправляем работника в новую пекарню
 ``` sql
	BEGIN;
INSERT INTO bakery_db.bakeries(name, address) VALUES ('Жар свежар', 'ул Баумана');
UPDATE bakery_db.workers SET bakery_id = 12 WHERE worker_id = 6;
COMMIT; 
```
![alt text](img/transaction_3.png)
![alt text](img/transaction_4.png)
### Запросы с **ROLLBACK**
3) Добавляет клиента и оформляет на него заказ
``` sql
BEGIN;
INSERT INTO bakery_db.clients(phone_number, last_name, middle_name, first_name, birth_date) VALUES('89083356464', 'Галимзянова', 'Адиля', 'Айдаровна', '10.01.2007');
UPDATE bakery_db.orders SET client_id = 15 WHERE order_id = 50;
ROLLBACK;

```
![alt text](img/transaction_5.png)
![alt text](img/transaction_6.png)

4) Перенаправляем работника в новую пекарню
 ``` sql
BEGIN;
INSERT INTO bakery_db.bakeries(name, address) VALUES('Жар свежар', 'ул Баумана');
UPDATE bakery_db.workers SET bakery_id = 12 WHERE worker_id = 6;
ROLLBACK;
```
![alt text](img/transaction_7.png)
![alt text](img/transaction_8.png)

### Транзакции с ошибкой
5)
 ``` sql
BEGIN;
INSERT INTO bakery_db.clients(phone_number, last_name, middle_name, first_name, birth_date) VALUES ('89083356464', 'Галимзянова', 'Адиля', 'Айдаровна', '10.01.2007');
UPDATE bakery_db.orders SET client_id = 7.5 WHERE order_id = 50;
ROLLBACK;
```
![alt text](img/transaction_9.png)
![alt text](img/transaction_10.png)

6)
 ``` sql
BEGIN;
INSERT INTO bakery_db.bakeries(name, address) values ('Жар свежар', 'ул Баумана');
UPDATE bakery_db.workers SET bakery_id = '10' WHERE worker_id = 6;
ROLLBACK;
```
![alt text](img/transaction_11.png)