-- migration_knockout_stages.sql
-- Adds Round of 16, Quarter Finals, Semi Finals, and Final picks
-- Run this in Supabase SQL Editor

-- Add columns to group_members for tracking validity of each stage
ALTER TABLE group_members 
ADD COLUMN IF NOT EXISTS has_valid_round16_picks BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_valid_quarter_picks BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_valid_semi_picks BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_valid_final_picks BOOLEAN DEFAULT FALSE;

-- Create table for Round of 16 picks (16 teams)
CREATE TABLE IF NOT EXISTS round16_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    team TEXT NOT NULL,
    PRIMARY KEY (username, group_name, team)
);

-- Create table for Quarter Finals picks (8 teams)
CREATE TABLE IF NOT EXISTS quarter_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    team TEXT NOT NULL,
    PRIMARY KEY (username, group_name, team)
);

-- Create table for Semi Finals picks (4 teams)
CREATE TABLE IF NOT EXISTS semi_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    team TEXT NOT NULL,
    PRIMARY KEY (username, group_name, team)
);

-- Create table for Final picks (2 teams + winner)
CREATE TABLE IF NOT EXISTS final_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    team TEXT NOT NULL,
    is_winner BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (username, group_name, team)
);

-- Add indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_round16_picks_user ON round16_picks(username, group_name);
CREATE INDEX IF NOT EXISTS idx_quarter_picks_user ON quarter_picks(username, group_name);
CREATE INDEX IF NOT EXISTS idx_semi_picks_user ON semi_picks(username, group_name);
CREATE INDEX IF NOT EXISTS idx_final_picks_user ON final_picks(username, group_name);
