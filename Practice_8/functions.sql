-- поиск контактов по паттерну (имя или телефон)
CREATE OR REPLACE FUNCTION search_contacts(p_pattern TEXT)
RETURNS TABLE(id INT, first_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT c.id, c.first_name, c.phone
        FROM phonebook c
        WHERE c.first_name ILIKE '%' || p_pattern || '%'
           OR c.phone ILIKE '%' || p_pattern || '%'
        ORDER BY c.first_name;
END;
$$ LANGUAGE plpgsql;


-- получение контактов с пагинацией
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(id INT, first_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT c.id, c.first_name, c.phone
        FROM phonebook c
        ORDER BY c.id
        LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;
