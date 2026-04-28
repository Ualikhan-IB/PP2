-- procedures.sql
-- This script contains all stored procedures and functions required for TSIS 1.

-- Drop existing objects to avoid conflicts (if any)
DROP FUNCTION IF EXISTS search_contacts(VARCHAR) CASCADE;
DROP PROCEDURE IF EXISTS add_phone(VARCHAR, VARCHAR, VARCHAR) CASCADE;
DROP PROCEDURE IF EXISTS move_to_group(VARCHAR, VARCHAR) CASCADE;

-- =========================================================================
-- 1. PROCEDURE: add_phone
--    Adds a new phone number to an existing contact.
-- =========================================================================
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- Find the contact (searches first_name or full name)
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE first_name ILIKE p_contact_name
       OR (first_name || ' ' || last_name) ILIKE p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact with name "%" not found', p_contact_name;
    END IF;

    -- Validate phone type
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type: "%". Must be home, work, or mobile.', p_type;
    END IF;

    -- Insert the new phone
    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type)
    ON CONFLICT (contact_id, phone) DO NOTHING;

    IF NOT FOUND THEN
        RAISE NOTICE 'Phone % (%) already exists for this contact. Skipped.', p_phone, p_type;
    ELSE
        RAISE NOTICE 'Phone % (%) successfully added to contact ID %.', p_phone, p_type, v_contact_id;
    END IF;
END;
$$;

-- =========================================================================
-- 2. PROCEDURE: move_to_group
--    Moves a contact to a group, creating the group if it doesn't exist.
-- =========================================================================
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id INTEGER;
BEGIN
    -- Find the contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE first_name ILIKE p_contact_name
       OR (first_name || ' ' || last_name) ILIKE p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact with name "%" not found', p_contact_name;
    END IF;

    -- Create the group if it doesn't exist
    INSERT INTO groups (name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    -- Get the group's ID
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    -- Update the contact's group
    UPDATE contacts
    SET group_id = v_group_id
    WHERE id = v_contact_id;

    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;

-- =========================================================================
-- 3. FUNCTION: search_contacts
--    Extends Practice 8's search to cover all fields, including all phones.
-- =========================================================================
CREATE OR REPLACE FUNCTION search_contacts(search_term TEXT)
RETURNS TABLE(
    id INTEGER,
    full_name TEXT,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phones TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        CONCAT(c.first_name, ' ', COALESCE(c.last_name, '')) AS full_name,
        c.email,
        c.birthday,
        g.name AS group_name,
        STRING_AGG(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.type) AS phones
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    WHERE
        c.first_name ILIKE '%' || search_term || '%'
        OR c.last_name ILIKE '%' || search_term || '%'
        OR c.email ILIKE '%' || search_term || '%'
        OR p.phone ILIKE '%' || search_term || '%'
    GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
    ORDER BY c.first_name, c.last_name;
END;
$$;