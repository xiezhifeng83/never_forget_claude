-- Never Forget Claude - Initial Database Schema
-- Per data-model.md: PostgreSQL 15+ schema for tasks table

-- Create tasks table with all constraints and indexes
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY,
    device_token UUID NOT NULL,
    text VARCHAR(500) NOT NULL CHECK (length(trim(text)) > 0),
    position INTEGER NOT NULL DEFAULT 0 CHECK (position >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT check_updated_after_created CHECK (updated_at >= created_at)
);

-- Create indexes per data-model.md for optimal query performance
CREATE INDEX IF NOT EXISTS idx_tasks_device_token ON tasks(device_token);
CREATE INDEX IF NOT EXISTS idx_tasks_device_position ON tasks(device_token, position);
CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks(updated_at);

-- Create trigger function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to call function before updates
CREATE TRIGGER tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Migration complete
-- Version: 001
-- Description: Initial schema with tasks table, indexes, and timestamp trigger
