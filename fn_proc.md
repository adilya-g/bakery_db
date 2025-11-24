# Процедуры и функции
### Процедуры
1) Создание нового заказа на доставку клиента в определенной пекарне
 ```
CREATE OR REPLACE PROCEDURE create_delivery_order(
	p_client_id INT,
    p_bakery_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
	INSERT INTO bakery_db.orders (client_id, bakery_id, type_of_order) 
	VALUES (p_client_id, p_bakery_id, 'Доставка');
END;
$$;

-- Вызываем процедуру
CALL create_delivery_order(1, 5);

-- Проверяем результат
SELECT * FROM bakery_db.orders WHERE client_id = 1;
```
![alt text](img/proc1.png)
    
2) Процедура добавления изделия в заказ
  ```
CREATE OR REPLACE PROCEDURE add_good_in_order(
	p_order_id INT,
    p_baking_id INT,
    p_quantity INT,
    p_unit_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
	INSERT INTO bakery_db.order_baking_goods (order_id, baking_id, quantity, unit_id) 
	VALUES (p_order_id, p_baking_id, p_quantity, p_unit_id);
END;
$$;

-- Вызываем процедуру
CALL add_good_in_order(1, 3, 10, 1);

- - Проверяем результат
SELECT * FROM bakery_db.order_baking_goods WHERE order_id = 1;
 ```

![alt text](img/proc2.png)
3) Процедура добавления нового изделия

  ```

CREATE OR REPLACE PROCEDURE add_new_baking_good(
 	p_description VARCHAR,
    p_name VARCHAR,
    p_size NUMERIC,
    p_unit_id INT,
    p_price INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_recipe_id INT;
BEGIN
	INSERT INTO bakery_db.recipes (description)
    VALUES (p_description)
    RETURNING recipe_id INTO v_recipe_id;
	
	INSERT INTO bakery_db.baking_goods (name, size, unit_id, recipe_id, price)
    VALUES (p_name, p_size, p_unit_id, v_recipe_id, p_price);
END;
$$;

-- Вызываем процедуру
call add_new_baking_good('Классический рецепт сырников', 'Сырники', 200, 1, 280);

-- Проверяем результат
SELECT * FROM bakery_db.baking_goods where name = 'Сырники';

 ```
![alt text](img/proc3.png)

Просмотр всех процедур
```
SELECT routine_name, routine_type FROM information_schema.routines
WHERE routine_type = 'PROCEDURE' AND routine_schema = 'public';
```
![alt text](img/allproc.png)

### Функции
1) Определение, калорийный ли ингредиент
 ```
CREATE OR REPLACE FUNCTION is_high_calorie_ingredient(p_ingredient_id INT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN (
        SELECT calories > 300
        FROM bakery_db.ingredients
        WHERE ingredient_id = p_ingredient_id
    );
END;
$$;

SELECT is_high_calorie_ingredient(1);
 ```
![alt text](img/func11.png)
2) Количество заказов у клиента
  ```
CREATE OR REPLACE FUNCTION quantity_of_orders(p_client_id INT)
RETURNS INT
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)
        FROM bakery_db.orders
        WHERE client_id = p_client_id
    );
END;
$$;
 ```
![alt text](img/func12.png)
3) Вывол полного имени клиента
 ```
CREATE OR REPLACE FUNCTION get_client_full_name(p_client_id INT)
RETURNS VARCHAR
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN (
		SELECT CONCAT(last_name,' ', first_name,' ', middle_name)
		FROM bakery_db.clients
		WHERE client_id = p_client_id
	);
END;
$$;

select get_client_full_name(3);
 ```
![alt text](img/func13.png)

### Функции с переменными

1) Вывод полной суммы заказа
 ```
CREATE OR REPLACE FUNCTION get_order_total(
    p_order_id INT
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_total INT;
BEGIN
    SELECT SUM(og.quantity * bg.price)
    INTO v_total
    FROM bakery_db.order_baking_goods og
    JOIN bakery_db.baking_goods bg
        ON og.baking_id = bg.baking_id
    WHERE og.order_id = p_order_id;

    RETURN v_total;
END;
$$;

select get_order_total(5);
 ```
![alt text](img/func1.png)
2) Проверка - у клиента день рождения в этом месяце
  ```
CREATE OR REPLACE FUNCTION is_birthday_this_month(
    p_client_id INT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_birth_date DATE;
BEGIN
    SELECT birth_date
    INTO v_birth_date
    FROM bakery_db.clients
    WHERE client_id = p_client_id;

    IF v_birth_date IS NULL THEN
        RETURN FALSE;
    END IF;

    RETURN EXTRACT(MONTH FROM v_birth_date) = EXTRACT(MONTH FROM CURRENT_DATE);
END;
$$;
-- Пример
SELECT *
FROM bakery_db.clients
WHERE EXTRACT(MONTH FROM birth_date) = EXTRACT(MONTH FROM CURRENT_DATE);
 ```
![alt text](img/func2.png)
3) Получение самого популярного изделия по пекарне
 ```
CREATE OR REPLACE FUNCTION get_bakery_top_good(p_bakery_id INT)
RETURNS VARCHAR
LANGUAGE plpgsql
AS $$
DECLARE
    v_top_good VARCHAR;
BEGIN
    SELECT bg.name
    INTO v_top_good
    FROM bakery_db.baking_goods bg
    JOIN bakery_db.order_baking_goods obg
        ON bg.baking_id = obg.baking_id
    JOIN bakery_db.orders o
        ON obg.order_id = o.order_id
    WHERE o.bakery_id = p_bakery_id
    GROUP BY bg.baking_id, bg.name
    ORDER BY SUM(obg.quantity) DESC
    LIMIT 1;

    RETURN v_top_good;
END;
$$;

SELECT get_bakery_top_good(2);
 ```
![alt text](img/func3.png)

Просмотр всех функций
```
SELECT routine_name, routine_type FROM information_schema.routines
WHERE routine_type = 'FUNCTION' AND routine_schema = 'public';
```
 ![alt text](img/allfunc1.png)
  ![alt text](img/allfunc2.png)
    
### Блок DO 

1) 
 ```
--
 ```
![alt text](img/sub_queries-1.png)
2)
  ```
--
 ```
![alt text](img/sub_queries-1.png)
3)
 ```
--
 ```
![alt text](img/sub_queries-1.png)
### IF

1) 
 ```
--
 ```
![alt text](img/sub_queries-1.png)
### CASE

1) 
 ```
--
 ```
![alt text](img/sub_queries-1.png)

### WHILE

1) 
 ```
--
 ```
![alt text](img/sub_queries-1.png)
2)
  ```
--
 ```
![alt text](img/sub_queries-1.png)

### EXCEPTION

1) 
 ```
--
 ```
![alt text](img/sub_queries-1.png)
2)
  ```
--
 ```
![alt text](img/sub_queries-1.png)

### RAISE

1) 
 ```
--
 ```
![alt text](img/sub_queries-1.png)
2)
  ```
--
 ```
![alt text](img/sub_queries-1.png)

