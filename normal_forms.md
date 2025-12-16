## 1 -  Нарушение атомарности (1 НФ) – два разных поля для одного смыслового признака (количества) в таблицах recipes_ingredients,  baking_goods, order_baking_goods:
   
**Решение** – создание таблицы для хранения единиц:

### units

CREATE TABLE bakery_db.units ( <br>
    unit_id SERIAL PRIMARY KEY,<br>
    unit_name VARCHAR(20) NOT NULL UNIQUE, -- например, "g", "ml", "pcs"<br>
    description VARCHAR(100)<br>
);<br>
<br>
INSERT INTO bakery_db.units (unit_name, description) VALUES<br>
('g', 'граммы'),<br>
('ml', 'миллилитры'),<br>
('pcs', 'штуки');<br>

![alt text](img/image_nf.png)

### baking_goods

CREATE TABLE bakery_db.baking_goods (<br>
    baking_id SERIAL PRIMARY KEY,<br>
    name VARCHAR(100) NOT NULL,<br>
    size NUMERIC(10,2) NOT NULL,<br>
    unit_id INT NOT NULL,<br>
    recipe_id INT NOT NULL<br>
);<br>

ALTER TABLE bakery_db.baking_goods<br>
    ADD CONSTRAINT fk_baking_goods_recipe<br>
        FOREIGN KEY (recipe_id)<br>
        REFERENCES bakery_db.recipes(recipe_id)<br>
        ON DELETE CASCADE;<br>

ALTER TABLE bakery_db.baking_goods<br>
    ADD CONSTRAINT fk_baking_goods_unit<br>
        FOREIGN KEY (unit_id)<br>
        REFERENCES bakery_db.units(unit_id)<br>
        ON DELETE RESTRICT;<br>

### recipes_ingredients

CREATE TABLE bakery_db.recipes_ingredients (<br>
    recipe_id INT NOT NULL,<br>
    ingredient_id INT NOT NULL,<br>
    quantity NUMERIC(10,2) NOT NULL,<br>
    unit_id INT NOT NULL,<br>
    PRIMARY KEY (recipe_id, ingredient_id)<br>
);<br>

ALTER TABLE bakery_db.recipes_ingredients<br>
    ADD CONSTRAINT fk_recipes_ingredients_recipe<br>
        FOREIGN KEY (recipe_id)<br>
        REFERENCES bakery_db.recipes(recipe_id)<br>
        ON DELETE CASCADE;<br>

ALTER TABLE bakery_db.recipes_ingredients<br>
    ADD CONSTRAINT fk_recipes_ingredients_ingredient<br>
        FOREIGN KEY (ingredient_id)<br>
        REFERENCES bakery_db.ingredients(ingredient_id)<br>
        ON DELETE CASCADE;<br>

ALTER TABLE bakery_db.recipes_ingredients<br>
    ADD CONSTRAINT fk_recipes_ingredients_unit<br>
        FOREIGN KEY (unit_id)<br>
        REFERENCES bakery_db.units(unit_id)<br>
        ON DELETE RESTRICT;<br>

### order_baking_goods

CREATE TABLE bakery_db.order_baking_goods (<br>
    order_id INT NOT NULL,<br>
    baking_id INT NOT NULL,<br>
    quantity NUMERIC(10,2) NOT NULL,<br>
    unit_id INT NOT NULL,<br>
    PRIMARY KEY (order_id, baking_id)<br>
);

ALTER TABLE bakery_db.order_baking_goods<br>
    ADD CONSTRAINT fk_order_baking_goods_order<br>
        FOREIGN KEY (order_id)<br>
        REFERENCES bakery_db.orders(order_id)<br>
        ON DELETE CASCADE;<br>

ALTER TABLE bakery_db.order_baking_goods<br>
    ADD CONSTRAINT fk_order_baking_goods_baking<br>
        FOREIGN KEY (baking_id)<br>
        REFERENCES bakery_db.baking_goods(baking_id)<br>
        ON DELETE CASCADE;<br>

ALTER TABLE bakery_db.order_baking_goods<br>
    ADD CONSTRAINT fk_order_baking_goods_unit<br>
        FOREIGN KEY (unit_id)<br>
        REFERENCES bakery_db.units(unit_id)<br>
        ON DELETE RESTRICT;<br>

## 2 - Поле full_name в clients и couriers не атомарно (1 НФ). 

###  Решение: Разбиваем на три поля — фамилию, имя, отчество.

ALTER TABLE bakery_db.clients<br>
ADD COLUMN last_name VARCHAR(80),<br>
ADD COLUMN first_name VARCHAR(80),<br>
ADD COLUMN middle_name VARCHAR(80);<br>

UPDATE bakery_db.clients<br>
SET last_name = split_part(full_name, ' ', 1),<br>
first_name = split_part(full_name, ' ', 2),<br>
middle_name = split_part(full_name, ' ', 3);<br>

ALTER TABLE bakery_db.clients DROP COLUMN full_name;<br>

ALTER TABLE bakery_db.couriers<br>
    ADD COLUMN last_name VARCHAR(50),<br>
    ADD COLUMN first_name VARCHAR(50),<br>
    ADD COLUMN middle_name VARCHAR(50);<br>

UPDATE bakery_db.couriers<br>
SET last_name = split_part(full_name, ' ', 1),<br>
    first_name = split_part(full_name, ' ', 2),<br>
    middle_name = NULLIF(split_part(full_name, ' ', 3), '');<br>

ALTER TABLE bakery_db.couriers<br>
    DROP COLUMN full_name;<br>

## 3 - В таблице recipes хранятся поля calories, proteins, fats, carbohydrates, которые представляют собой агрегированные показатели, вычисляемые из состава ингредиентов. Это создаёт транзитивную зависимость (через recipes_ingredients → ingredients), нарушающую 3НФ.
Кроме того, это вызывает риск дублирования и несогласованности данных — если изменить ингредиенты, калорийность рецепта может измениться, но значения в таблице recipes останутся прежними.

### Решение – не хранить нутриенты в recipes, а вычислять их динамически из состава и ингредиентов.

ALTER TABLE bakery_db.recipes<br>
    DROP COLUMN IF EXISTS calories,<br>
    DROP COLUMN IF EXISTS proteins,<br>
    DROP COLUMN IF EXISTS fats,<br>
    DROP COLUMN IF EXISTS carbohydrates;<br>


![alt text](bakery_db_schema_normalised.pgerd.png)
