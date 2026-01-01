-- Migration: Add 'role' column to users table if it does not exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='role'
    ) THEN
        ALTER TABLE users ADD COLUMN role VARCHAR;
    END IF;
END $$;