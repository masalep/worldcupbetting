-- migration_knockout_picks.sql
-- Adds knockout picks feature to existing database
-- Run this in Supabase SQL Editor if you already have the budget system running

-- Add has_valid_knockout_picks column to group_members
ALTER TABLE group_members 
ADD COLUMN IF NOT EXISTS has_valid_knockout_picks BOOLEAN DEFAULT FALSE;

-- Create teams table
CREATE TABLE IF NOT EXISTS teams (
    team_name TEXT PRIMARY KEY,
    group_name TEXT NOT NULL
);

-- Create knockout_picks table
CREATE TABLE IF NOT EXISTS knockout_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    team TEXT NOT NULL,
    PRIMARY KEY (username, group_name, team)
);

-- Optional: Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_knockout_picks_user 
ON knockout_picks(username, group_name);

-- Insert all teams (run init_teams.sql separately for full data)
-- Or insert just Group A for testing:
INSERT INTO teams (team_name, group_name) VALUES
('Mexico', 'A'),
('South Africa', 'A'),
('South Korea', 'A'),
('Czech Republic', 'A')
ON CONFLICT (team_name) DO NOTHING;
