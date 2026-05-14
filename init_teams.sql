-- init_teams.sql
-- Inserts all 48 teams and their groups for 2026 World Cup
-- Run in Supabase SQL Editor after creating tables

INSERT INTO teams (team_name, group_name) VALUES
-- GROUP A
('Mexico', 'A'),
('South Africa', 'A'),
('South Korea', 'A'),
('Czech Republic', 'A'),

-- GROUP B
('Canada', 'B'),
('Bosnia and Herzegovina', 'B'),
('Qatar', 'B'),
('Switzerland', 'B'),

-- GROUP C
('Brazil', 'C'),
('Morocco', 'C'),
('Haiti', 'C'),
('Scotland', 'C'),

-- GROUP D
('USA', 'D'),
('Paraguay', 'D'),
('Australia', 'D'),
('Turkey', 'D'),

-- GROUP E
('Germany', 'E'),
('Curaçao', 'E'),
('Ivory Coast', 'E'),
('Ecuador', 'E'),

-- GROUP F
('Netherlands', 'F'),
('Japan', 'F'),
('Sweden', 'F'),
('Tunisia', 'F'),

-- GROUP G
('Argentina', 'G'),
('Colombia', 'G'),
('Jamaica', 'G'),
('Peru', 'G'),

-- GROUP H
('England', 'H'),
('Wales', 'H'),
('Belgium', 'H'),
('Saudi Arabia', 'H'),

-- GROUP I
('Spain', 'I'),
('Poland', 'I'),
('Ukraine', 'I'),
('Costa Rica', 'I'),

-- GROUP J
('France', 'J'),
('Denmark', 'J'),
('Senegal', 'J'),
('Uruguay', 'J'),

-- GROUP K
('Portugal', 'K'),
('Croatia', 'K'),
('Egypt', 'K'),
('Serbia', 'K'),

-- GROUP L
('Italy', 'L'),
('Norway', 'L'),
('Algeria', 'L'),
('Chile', 'L')

ON CONFLICT (team_name) DO NOTHING;
