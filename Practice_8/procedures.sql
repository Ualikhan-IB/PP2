-- Процедура 1: upsert — вставить или обновить телефон если имя уже есть
CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_name) THEN
        UPDATE phonebook SET phone = p_phone WHERE first_name = p_name;
    ELSE
        INSERT INTO phonebook(first_name, phone) VALUES(p_name, p_phone);
    END IF;
END;
$$;


-- Процедура 2: массовая вставка из списка с валидацией телефона
-- Возвращает некорректные записи через временную таблицу
CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_names VARCHAR[],
    p_phones VARCHAR[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
    v_name VARCHAR;
    v_phone VARCHAR;
BEGIN
    -- Создаём временную таблицу для некорректных данных (если ещё нет)
    CREATE TEMP TABLE IF NOT EXISTS invalid_contacts (
        first_name VARCHAR,
        phone VARCHAR,
        reason TEXT
    ) ON COMMIT PRESERVE ROWS;

    -- Очищаем от предыдущего вызова
    DELETE FROM invalid_contacts;

    FOR i IN 1 .. array_length(p_names, 1) LOOP
        v_name := p_names[i];
        v_phone := p_phones[i];

        -- Валидация телефона: только цифры, +, пробелы, длина 10-15
        IF v_phone !~ '^\+?[0-9\s\-]{10,15}$' THEN
            INSERT INTO invalid_contacts(first_name, phone, reason)
            VALUES(v_name, v_phone, 'Некорректный формат телефона');
        ELSE
            -- Upsert: если имя уже есть — обновляем, иначе вставляем
            IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = v_name) THEN
                UPDATE phonebook SET phone = v_phone WHERE first_name = v_name;
            ELSE
                INSERT INTO phonebook(first_name, phone) VALUES(v_name, v_phone);
            END IF;
        END IF;
    END LOOP;
END;
$$;


-- Процедура 3: удаление по имени или телефону
CREATE OR REPLACE PROCEDURE delete_contact(p_name VARCHAR DEFAULT NULL, p_phone VARCHAR DEFAULT NULL)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_name IS NOT NULL THEN
        DELETE FROM phonebook WHERE first_name = p_name;
    ELSIF p_phone IS NOT NULL THEN
        DELETE FROM phonebook WHERE phone = p_phone;
    ELSE
        RAISE EXCEPTION 'Нужно указать имя или телефон для удаления';
    END IF;
END;
$$;
