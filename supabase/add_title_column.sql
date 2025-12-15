-- Migration: Add title column to chat_sessions if it doesn't exist
-- This script is safe to run multiple times

DO $$ 
BEGIN
    -- Check if the column exists, if not add it
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'chat_sessions' 
        AND column_name = 'title'
    ) THEN
        ALTER TABLE chat_sessions 
        ADD COLUMN title VARCHAR(100) DEFAULT 'New Chat';
        
        RAISE NOTICE 'Added title column to chat_sessions table';
    ELSE
        RAISE NOTICE 'Title column already exists in chat_sessions table';
    END IF;
END $$;
