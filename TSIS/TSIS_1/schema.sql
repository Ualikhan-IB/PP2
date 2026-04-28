-- schema.sql
-- This script creates the entire database schema for TSIS 1.

-- Enable the 'uuid-ossp' extension for generating UUIDs if needed (optional but good practice)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Groups table
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Contacts table (extended from Practice 7)
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    email VARCHAR(255),
    birthday DATE,
    group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Add UNIQUE constraint for first_name and last_name combination
    UNIQUE(first_name, last_name)
);

-- 3. Phones table (1-to-many relationship with contacts)
CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    phone VARCHAR(20) NOT NULL,
    type VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(contact_id, phone) -- Prevents duplicate phones for the same contact
);

-- Indexes for faster searching
CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(first_name, last_name);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_birthday ON contacts(birthday);
CREATE INDEX IF NOT EXISTS idx_phones_number ON phones(phone);

-- Function and Trigger for auto-updating 'updated_at' field
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_contacts_updated_at ON contacts;
CREATE TRIGGER trigger_update_contacts_updated_at
    BEFORE UPDATE ON contacts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();