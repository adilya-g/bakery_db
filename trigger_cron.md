# Триггеры и кроны

## Триггеры

### NEW
1) 
 ```

```
![alt text](img/.png)

2) 
 ```

```
![alt text](img/.png)
### OLD

3) 
 ```

```
![alt text](img/.png)

4) 
 ```

```
![alt text](img/.png)

### BEFORE

5) 
 ```

```
![alt text](img/.png)

6) 
 ```

```
![alt text](img/.png)

### AFTER

7) Лгирование изменения адресов пекарен
 ``` sql
 --функция
CREATE OR REPLACE FUNCTION log_address_changes()
RETURNS TRIGGER AS $$
BEGIN
    RAISE NOTICE 'Операция: %', TG_OP;
    
    IF TG_OP = 'INSERT' THEN
        RAISE NOTICE 'Добавлена новая пекарня. ID: %, Адрес: %', 
                     NEW.id, NEW.address;
    ELSIF TG_OP = 'UPDATE' THEN
        RAISE NOTICE 'Изменена пекарня ID: %', NEW.id;
        RAISE NOTICE 'Старый адрес: %', OLD.address;
        RAISE NOTICE 'Новый адрес: %', NEW.address;
    ELSIF TG_OP = 'DELETE' THEN
        RAISE NOTICE 'Удалена пекарня ID: %, Адрес: %', 
                     OLD.id, OLD.address;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

--триггер
CREATE TRIGGER after_bakery_address_change
AFTER INSERT OR UPDATE OR DELETE ON bakery_db.bakeries
FOR EACH ROW EXECUTE FUNCTION log_address_changes();

--запрос
UPDATE bakery_db.bakeries
SET address = 'проспект Беляева, 15'
WHERE bakery_id = 31;
```
![alt text](img/trigger_crons_7.png)

8) Логирование новых заказов
 ```sql
 --функция
CREATE OR REPLACE FUNCTION log_order_changes()
RETURNS TRIGGER AS $$
BEGIN
    RAISE NOTICE 'Операция: %', TG_OP;
    
    IF TG_OP = 'INSERT' THEN
        RAISE NOTICE 'Добавлен новый заказ: ID клиента: %, ID пекарни: %, Тип заказа: %', NEW.client_id, NEW.bakery_id, NEW.type_of_order;
    ELSIF TG_OP = 'UPDATE' THEN
        RAISE NOTICE 'Изменён заказ ID: %', NEW.order_id;
        RAISE NOTICE 'Старый заказ: ID клиента: %, ID пекарни: %, Тип заказа: %', OLD.client_id, OLD.bakery_id, OLD.type_of_order;
        RAISE NOTICE 'Новый заказ: ID клиента: %, ID пекарни: %, Тип заказа: %', NEW.client_id, NEW.bakery_id, NEW.type_of_order;
    ELSIF TG_OP = 'DELETE' THEN
        RAISE NOTICE 'Удален заказ ID: %', 
                     OLD.order_id;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

--триггер
CREATE TRIGGER after_order_change
AFTER INSERT OR UPDATE OR DELETE ON bakery_db.orders
FOR EACH ROW EXECUTE FUNCTION log_order_changes();

--запрос
insert into bakery_db.orders(client_id, bakery_id, type_of_order)
values (1, 31, 'Самовывоз')

```
![alt text](img/trigger_crons_8.png)

### ROW-LEVEL
9) Логирование добавления сторудника
 ```sql
 --функция
CREATE OR REPLACE FUNCTION log_worker_insert()
RETURNS TRIGGER AS $$
BEGIN
    RAISE NOTICE 'Операция: %', TG_OP;
    
    IF TG_OP = 'INSERT' THEN
        RAISE NOTICE 'К нам присоединился новый сотрудник: %', NEW.first_name;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

--триггер
CREATE TRIGGER after_worker_insert
AFTER INSERT  ON bakery_db.workers
FOR EACH ROW EXECUTE FUNCTION log_worker_insert();

--запрос
INSERT INTO bakery_db.workers (
    bakery_id,
    role,
    phone_number,
    first_name,
    second_name,
    date_of_birth
) VALUES (
    31,
    'Помощник пекаря',
    '7(916)5556677',
    'Алексей',
    'Смирнов',
    '1998-02-14'
);
```
![alt text](img/trigger_crons_9.png)

10) Логирование изменения цены
 ```sql
 --функция
CREATE OR REPLACE FUNCTION log_price_update()
RETURNS TRIGGER AS $$
BEGIN
    RAISE NOTICE 'Операция: %', TG_OP;
    
    IF OLD.price IS DISTINCT FROM NEW.price THEN
        RAISE NOTICE 'Изменение в цене продукта "%". Старая цена: %, Новая цена: %, ID: %', NEW.name, OLD.price, NEW.price, NEW.baking_id;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

--триггер
CREATE TRIGGER after_baking_price_changed
AFTER update ON bakery_db.baking_goods
FOR EACH ROW EXECUTE FUNCTION log_price_update();

--запрос
UPDATE bakery_db.baking_goods
SET price = 100
WHERE baking_id = 1;
```
![alt text](img/trigger_crons_10.png)

### Statement level
11) Считает количество сотрудников после изменения 
 ```sql
--функция
CREATE OR REPLACE FUNCTION update_row_counter()
RETURNS TRIGGER AS $$
DECLARE
    new_count INTEGER;
BEGIN
   
    EXECUTE format('SELECT COUNT(*) FROM %I', TG_TABLE_NAME)
    INTO new_count;
    
    RAISE NOTICE 'В таблице % теперь % строк', TG_TABLE_NAME, new_count;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

--триггер
CREATE TRIGGER count_workers
AFTER INSERT OR UPDATE OR DELETE ON bakery_db.workers
FOR EACH STATEMENT EXECUTE FUNCTION update_row_counter();

--запрос
INSERT INTO bakery_db.workers (
    bakery_id,
    role,
    phone_number,
    first_name,
    second_name,
    date_of_birth
) VALUES (
    32,
    'Пекарь',
    '7(916)5556668',
    'Василий',
    'Галимов',
    '1998-10-24'
);
```
![alt text](img/trigger_crons_11.png)

12) Создаём бэкап перед удалением
 ```sql
--функция
CREATE OR REPLACE FUNCTION quick_backup()
RETURNS TRIGGER AS $$
BEGIN
    RAISE NOTICE 'Триггер сработал на DELETE!';
    
    -- Создаем бэкапную таблицу
    CREATE TABLE IF NOT EXISTS workers_deleted_backup AS
    SELECT *, NOW() as deleted_at 
    FROM bakery_db.workers;
    
    RAISE NOTICE 'Бэкап создан: workers_deleted_backup';
    
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

--триггер
CREATE TRIGGER quick_backup_trigger
BEFORE DELETE ON bakery_db.workers
FOR EACH STATEMENT EXECUTE FUNCTION quick_backup();

--запрос
DELETE FROM bakery_db.workers WHERE bakery_id = 31;
```
![alt text](img/trigger_crons_12.png)

### Список триггеров
13)
 ```

```
![alt text](img/.png)


### Кроны
14)
 ```

```
![alt text](img/.png)

15) 
 ```

```
![alt text](img/.png)

16) 
 ```

```
![alt text](img/.png)

### Запрос на просмотр выполнения кронов
17)
 ```

```
![alt text](img/.png)

### Запрос на просмотр кронов
18)
 ```

```
![alt text](img/.png)
