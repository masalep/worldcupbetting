-- Migration: Add Knockout Results Tables
-- Run this in Supabase SQL Editor

-- Drop the table if it exists (to fix the schema)
DROP TABLE IF EXISTS knockout_results CASCADE;

-- Table to store actual knockout results (admin sets these)
CREATE TABLE knockout_results (
    id SERIAL PRIMARY KEY,
    stage TEXT NOT NULL,
    team TEXT,
    player_name TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stage, team, player_name)
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_knockout_results_stage ON knockout_results(stage);

