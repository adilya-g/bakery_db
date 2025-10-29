


CREATE SCHEMA IF NOT EXISTS bakery_db;

-- 1. Базовые сущности
CREATE TABLE bakery_db.bakeries (
    bakery_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(100) NOT NULL
);

CREATE TABLE bakery_db.workers (
    worker_id SERIAL PRIMARY KEY,
    role VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15),
    first_name VARCHAR(50),
    second_name VARCHAR(50),
    date_of_birth DATE,
    bakery_id INT,
    CONSTRAINT fk_workers_bakery
        FOREIGN KEY (bakery_id)
        REFERENCES bakery_db.bakeries(bakery_id)
        ON DELETE CASCADE
);

CREATE TABLE bakery_db.appliances (
    appliance_id SERIAL PRIMARY KEY,
    bakery_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    document VARCHAR(50),
    CONSTRAINT fk_appliances_bakery
        FOREIGN KEY (bakery_id)
        REFERENCES bakery_db.bakeries(bakery_id)
        ON DELETE CASCADE
);

-- 2. Таблицы рецептов и ингредиентов
CREATE TABLE bakery_db.recipes (
    recipe_id SERIAL PRIMARY KEY,
    description VARCHAR(200)
);

CREATE TABLE bakery_db.ingredients (
    ingredient_id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    calories NUMERIC(10,2),
    proteins NUMERIC(10,2),
    fats NUMERIC(10,2),
    carbohydrates NUMERIC(10,2)
);

-- 3. Единицы измерения
CREATE TABLE bakery_db.units (
    unit_id SERIAL PRIMARY KEY,
    unit_name VARCHAR(20) NOT NULL UNIQUE,
    description VARCHAR(100)
);

INSERT INTO bakery_db.units (unit_name, description) VALUES
('g', 'граммы'),
('ml', 'миллилитры'),
('pcs', 'штуки');

-- 4. Связь рецептов с ингредиентами
CREATE TABLE bakery_db.recipes_ingredients (
    recipe_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity NUMERIC(10,2) NOT NULL,
    unit_id INT NOT NULL,
    PRIMARY KEY (recipe_id, ingredient_id),
    CONSTRAINT fk_recipes_ingredients_recipe
        FOREIGN KEY (recipe_id)
        REFERENCES bakery_db.recipes(recipe_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_recipes_ingredients_ingredient
        FOREIGN KEY (ingredient_id)
        REFERENCES bakery_db.ingredients(ingredient_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_recipes_ingredients_unit
        FOREIGN KEY (unit_id)
        REFERENCES bakery_db.units(unit_id)
        ON DELETE RESTRICT
);

-- 5. Рецепты и оборудование
CREATE TABLE bakery_db.recipes_appliances (
    recipe_id INT NOT NULL,
    appliance_id INT NOT NULL,
    PRIMARY KEY (recipe_id, appliance_id),
    CONSTRAINT fk_recipes_appliances_recipe
        FOREIGN KEY (recipe_id)
        REFERENCES bakery_db.recipes(recipe_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_recipes_appliances_appliance
        FOREIGN KEY (appliance_id)
        REFERENCES bakery_db.appliances(appliance_id)
        ON DELETE CASCADE
);

-- 6. Клиенты 
CREATE TABLE bakery_db.clients (
    client_id SERIAL PRIMARY KEY,
    phone_number VARCHAR(11),
    last_name VARCHAR(80),
    first_name VARCHAR(80),
    middle_name VARCHAR(80),
    birth_date DATE
);

-- 7. Курьеры 
CREATE TABLE bakery_db.couriers (
    courier_id SERIAL PRIMARY KEY,
    phone_number VARCHAR(11),
    last_name VARCHAR(80),
    first_name VARCHAR(80),
    middle_name VARCHAR(80)
);

-- 8. Заказы
CREATE TABLE bakery_db.orders (
    order_id SERIAL PRIMARY KEY,
    client_id INT NOT NULL,
    bakery_id INT NOT NULL,
    type_of_order VARCHAR(50),
    CONSTRAINT fk_orders_client
        FOREIGN KEY (client_id)
        REFERENCES bakery_db.clients(client_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_orders_bakery
        FOREIGN KEY (bakery_id)
        REFERENCES bakery_db.bakeries(bakery_id)
        ON DELETE CASCADE
);

-- 9. Выпечка
CREATE TABLE bakery_db.baking_goods (
    baking_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    size NUMERIC(10,2) NOT NULL,
    unit_id INT NOT NULL,
    recipe_id INT NOT NULL,
    CONSTRAINT fk_baking_goods_recipe
        FOREIGN KEY (recipe_id)
        REFERENCES bakery_db.recipes(recipe_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_baking_goods_unit
        FOREIGN KEY (unit_id)
        REFERENCES bakery_db.units(unit_id)
        ON DELETE RESTRICT
);

-- 10. Состав заказов
CREATE TABLE bakery_db.order_baking_goods (
    order_id INT NOT NULL,
    baking_id INT NOT NULL,
    quantity NUMERIC(10,2) NOT NULL,
    unit_id INT NOT NULL,
    PRIMARY KEY (order_id, baking_id),
    CONSTRAINT fk_order_baking_goods_order
        FOREIGN KEY (order_id)
        REFERENCES bakery_db.orders(order_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_order_baking_goods_baking
        FOREIGN KEY (baking_id)
        REFERENCES bakery_db.baking_goods(baking_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_order_baking_goods_unit
        FOREIGN KEY (unit_id)
        REFERENCES bakery_db.units(unit_id)
        ON DELETE RESTRICT
);

-- 11. Доставка
CREATE TABLE bakery_db.delivery_orders (
    delivery_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    courier_id INT NOT NULL,
    address VARCHAR(150),
    CONSTRAINT fk_delivery_orders_order
        FOREIGN KEY (order_id)
        REFERENCES bakery_db.orders(order_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_delivery_orders_courier
        FOREIGN KEY (courier_id)
        REFERENCES bakery_db.couriers(courier_id)
        ON DELETE CASCADE
);

ALTER TABLE bakery_db.recipes
    DROP COLUMN IF EXISTS calories,
    DROP COLUMN IF EXISTS proteins,
    DROP COLUMN IF EXISTS fats,
    DROP COLUMN IF EXISTS carbohydrates;

-- Заполняем таблицу единиц измерений
INSERT INTO bakery_db.units (unit_name, description) VALUES
('kg', 'килограммы'),
('l', 'литры');

-- Заполняем таблицу пекарен (10 записей)
INSERT INTO bakery_db.bakeries (name, address) VALUES
('Пекарня "Уют"', 'ул. Ленина, 15'),
('Пекарня "Вкусная"', 'пр. Мира, 42'),
('Пекарня "Сдобная"', 'ул. Центральная, 8'),
('Пекарня "Аромат"', 'ул. Пушкина, 23'),
('Пекарня "Свежая"', 'ул. Садовая, 67'),
('Пекарня "Домашняя"', 'ул. Гагарина, 12'),
('Пекарня "Утренняя"', 'пр. Космонавтов, 34'),
('Пекарня "Золотая"', 'ул. Зеленая, 56'),
('Пекарня "Русская"', 'ул. Московская, 89'),
('Пекарня "Европейская"', 'ул. Парижская, 11');

-- Заполняем таблицу сотрудников (10 записей)
INSERT INTO bakery_db.workers (role, phone_number, first_name, second_name, date_of_birth, bakery_id) VALUES
('Пекарь', '79101234567', 'Иван', 'Петров', '1985-03-15', 1),
('Кондитер', '79209876543', 'Мария', 'Иванова', '1990-07-22', 1),
('Пекарь', '79305556677', 'Сергей', 'Сидоров', '1988-11-10', 2),
('Уборщик', '79401231234', 'Анна', 'Кузнецова', '1992-05-18', 2),
('Менеджер', '79508765432', 'Алексей', 'Смирнов', '1983-09-25', 3),
('Пекарь', '79602345678', 'Ольга', 'Васильева', '1987-12-30', 3),
('Кондитер', '79703456789', 'Дмитрий', 'Павлов', '1991-04-05', 4),
('Кассир', '79804567890', 'Елена', 'Николаева', '1993-08-12', 4),
('Пекарь', '79905678901', 'Артем', 'Федоров', '1986-01-20', 5),
('Упаковщик', '79006789012', 'Наталья', 'Морозова', '1994-06-08', 5);

-- Заполняем таблицу оборудования (10 записей)
INSERT INTO bakery_db.appliances (bakery_id, name, document) VALUES
(1, 'Печь электрическая', 'Паспорт ПЭ-001'),
(1, 'Тестомес', 'Паспорт ТМ-015'),
(2, 'Печь газовая', 'Паспорт ПГ-023'),
(2, 'Холодильник', 'Паспорт ХЛ-045'),
(3, 'Весы электронные', 'Паспорт ВЭ-067'),
(3, 'Миксер', 'Паспорт МК-089'),
(4, 'Печь конвекционная', 'Паспорт ПК-101'),
(4, 'Шкаф расстоечный', 'Паспорт ШР-123'),
(5, 'Тестомес планетарный', 'Паспорт ТП-145'),
(5, 'Хлеборезка', 'Паспорт ХР-167');

-- Заполняем таблицу ингредиентов (10 записей)
INSERT INTO bakery_db.ingredients (name, calories, proteins, fats, carbohydrates) VALUES
('Мука пшеничная', 364.0, 10.3, 1.0, 76.1),
('Сахар', 399.0, 0.0, 0.0, 99.8),
('Яйца куриные', 157.0, 12.7, 11.5, 0.7),
('Молоко', 64.0, 3.2, 3.6, 4.8),
('Масло сливочное', 748.0, 0.5, 82.5, 0.8),
('Дрожжи', 109.0, 12.7, 1.5, 10.0),
('Соль', 0.0, 0.0, 0.0, 0.0),
('Вода', 0.0, 0.0, 0.0, 0.0),
('Какао-порошок', 228.0, 19.6, 13.7, 54.7),
('Изюм', 299.0, 3.1, 0.5, 79.0);

-- Заполняем таблицу рецептов (10 записей)
INSERT INTO bakery_db.recipes (description) VALUES
('Хлеб пшеничный'),
('Булочки сдобные'),
('Торт шоколадный'),
('Пирожки с капустой'),
('Печенье овсяное'),
('Кекс изюмный'),
('Пирог яблочный'),
('Батон нарезной'),
('Рогалики слоеные'),
('Пончики');

-- Заполняем таблицу клиентов (10 записей)
INSERT INTO bakery_db.clients (phone_number, birth_date, last_name, first_name, middle_name) VALUES
('79111234567', '1990-01-15', 'Иванов', 'Петр', 'Сергеевич'),
('79219876543', '1985-05-20', 'Петрова', 'Ольга', 'Владимировна'),
('79315556677', '1992-08-10', 'Сидоров', 'Алексей', 'Игоревич'),
('79411231234', '1988-03-25', 'Кузнецова', 'Елена', 'Дмитриевна'),
('79518765432', '1995-11-30', 'Смирнов', 'Дмитрий', 'Анатольевич'),
('79612345678', '1983-07-12', 'Васильев', 'Андрей', 'Петрович'),
('79713456789', '1991-09-18', 'Павлова', 'Ирина', 'Сергеевна'),
('79814567890', '1987-04-05', 'Николаев', 'Сергей', 'Васильевич'),
('79915678901', '1993-12-22', 'Федорова', 'Мария', 'Алексеевна'),
('79016789012', '1989-06-08', 'Морозов', 'Александр', 'Иванович');

-- Заполняем таблицу курьеров (10 записей)
INSERT INTO bakery_db.couriers (phone_number, last_name, first_name, middle_name) VALUES
('79122345678', 'Козлов', 'Игорь', 'Викторович'),
('79223456789', 'Орлова', 'Светлана', 'Николаевна'),
('79324567890', 'Белов', 'Антон', 'Сергеевич'),
('79425678901', 'Григорьева', 'Татьяна', 'Петровна'),
('79526789012', 'Дмитриев', 'Владимир', 'Александрович'),
('79627890123', 'Семенова', 'Надежда', 'Ивановна'),
('79728901234', 'Филиппов', 'Роман', 'Дмитриевич'),
('79829012345', 'Тихонова', 'Екатерина', 'Владимировна'),
('79920123456', 'Комаров', 'Станислав', 'Олегович'),
('79021234567', 'Зайцева', 'Людмила', 'Андреевна');

-- Заполняем таблицу хлебобулочных изделий (10 записей)
INSERT INTO bakery_db.baking_goods (name, size, unit_id, recipe_id) VALUES
('Хлеб пшеничный', 500, 1, 1),
('Булочка сдобная', 100, 1, 2),
('Торт шоколадный', 1000, 1, 3),
('Пирожок с капустой', 150, 1, 4),
('Печенье овсяное', 50, 1, 5),
('Кекс изюмный', 300, 1, 6),
('Пирог яблочный', 800, 1, 7),
('Батон нарезной', 400, 1, 8),
('Рогалик слоеный', 80, 1, 9),
('Пончик', 70, 1, 10);

-- Заполняем таблицу заказов (10 записей)
INSERT INTO bakery_db.orders (client_id, bakery_id, type_of_order) VALUES
(1, 1, 'Самовывоз'),
(2, 2, 'Доставка'),
(3, 3, 'Самовывоз'),
(4, 4, 'Доставка'),
(5, 5, 'Самовывоз'),
(6, 1, 'Доставка'),
(7, 2, 'Самовывоз'),
(8, 3, 'Доставка'),
(9, 4, 'Самовывоз'),
(10, 5, 'Доставка');

-- Заполняем таблицу доставки (10 записей)
INSERT INTO bakery_db.delivery_orders (order_id, courier_id, address) VALUES
(2, 1, 'ул. Мира, 25, кв. 12'),
(4, 2, 'пр. Ленина, 67, кв. 45'),
(6, 3, 'ул. Центральная, 89, кв. 23'),
(8, 4, 'ул. Садовая, 34, кв. 67'),
(10, 5, 'ул. Пушкина, 56, кв. 89'),
(2, 6, 'ул. Гагарина, 78, кв. 34'),
(4, 7, 'пр. Космонавтов, 12, кв. 56'),
(6, 8, 'ул. Зеленая, 90, кв. 78'),
(8, 9, 'ул. Московская, 23, кв. 90'),
(10, 10, 'ул. Парижская, 45, кв. 12');

-- Заполняем таблицу связи рецептов и ингредиентов (10 записей)
INSERT INTO bakery_db.recipes_ingredients (recipe_id, ingredient_id, quantity, unit_id) VALUES
(1, 1, 500, 1), (1, 6, 10, 1), (1, 7, 5, 1), (1, 8, 300, 2),
(2, 1, 400, 1), (2, 2, 100, 1), (2, 5, 50, 1), (2, 6, 15, 1),
(3, 1, 300, 1), (3, 2, 200, 1), (3, 3, 4, 3), (3, 9, 50, 1);


-- Заполняем таблицу связи заказов и изделий (10 записей)
INSERT INTO bakery_db.order_baking_goods (order_id, baking_id, quantity, unit_id) VALUES
(1, 1, 2, 3), (1, 2, 5, 3),
(2, 3, 1, 3), (2, 5, 10, 3),
(3, 4, 3, 3), (3, 6, 2, 3),
(4, 7, 1, 3), (4, 8, 2, 3),
(5, 9, 6, 3), (5, 10, 8, 3);


-- Заполняем таблицу связи рецептов и оборудования (10 записей)
INSERT INTO bakery_db.recipes_appliances (recipe_id, appliance_id) VALUES
(1, 1), (1, 2),
(2, 1), (2, 2),
(3, 1), (3, 6),
(4, 1), (4, 2),
(5, 1), (5, 6);

-- Добавляем столбец цен в рублях и обновляем предыдущую информацию
ALTER TABLE bakery_db.baking_goods
ADD COLUMN price INT;

UPDATE bakery_db.baking_goods
SET price = CASE
    WHEN name = 'Хлеб пшеничный' THEN 80
    WHEN name = 'Булочка сдобная' THEN 40
    WHEN name = 'Торт шоколадный' THEN 600
    WHEN name = 'Пирожок с капустой' THEN 50
    WHEN name = 'Печенье овсяное' THEN 35
    WHEN name = 'Кекс изюмный' THEN 120
    WHEN name = 'Пирог яблочный' THEN 300
    WHEN name = 'Батон нарезной' THEN 70
    WHEN name = 'Рогалик слоеный' THEN 45
    WHEN name = 'Пончик' THEN 55
END;

ALTER TABLE bakery_db.baking_goods
ALTER COLUMN price SET NOT NULL;
