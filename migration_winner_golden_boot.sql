-- Migration: Add Winner and Golden Boot picks
-- Run this in Supabase SQL Editor

-- Add validation columns to group_members
ALTER TABLE group_members 
ADD COLUMN IF NOT EXISTS has_valid_winner_pick BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_valid_golden_boot_pick BOOLEAN DEFAULT FALSE;

-- Create tournament_winner_picks table
CREATE TABLE IF NOT EXISTS tournament_winner_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    team TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (username, group_name)
);

-- Create golden_boot_picks table
CREATE TABLE IF NOT EXISTS golden_boot_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    player_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (username, group_name)
);

-- Create goal_scorers table (list of all players for dropdown)
CREATE TABLE IF NOT EXISTS goal_scorers (
    player_name TEXT PRIMARY KEY,
    team TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tournament_winner_picks_user ON tournament_winner_picks(username, group_name);
CREATE INDEX IF NOT EXISTS idx_golden_boot_picks_user ON golden_boot_picks(username, group_name);
CREATE INDEX IF NOT EXISTS idx_goal_scorers_team ON goal_scorers(team);

-- Insert some sample goal scorers (you can add more later)
INSERT INTO goal_scorers (player_name, team) VALUES
('Lionel Messi', 'Argentina'),
('Cristiano Ronaldo', 'Portugal'),
('Kylian Mbappé', 'France'),
('Harry Kane', 'England'),
('Neymar Jr', 'Brazil'),
('Erling Haaland', 'Norway'),
('Mohamed Salah', 'Egypt'),
('Kevin De Bruyne', 'Belgium'),
('Luka Modrić', 'Croatia'),
('Robert Lewandowski', 'Poland')
ON CONFLICT (player_name) DO NOTHING;
