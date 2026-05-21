-- init_teams.sql
-- Inserts all 48 teams and their groups for 2026 World Cup
-- Run in Supabase SQL Editor after creating tables
-- Teams extracted from matches.json

INSERT INTO teams (team_name, group_name) VALUES
-- GROUP A
('Czech Republic', 'A'),
('Mexico', 'A'),
('South Africa', 'A'),
('South Korea', 'A'),

-- GROUP B
('Bosnia & Herzegovina', 'B'),
('Canada', 'B'),
('Qatar', 'B'),
('Switzerland', 'B'),

-- GROUP C
('Brazil', 'C'),
('Haiti', 'C'),
('Morocco', 'C'),
('Scotland', 'C'),

-- GROUP D
('Australia', 'D'),
('Paraguay', 'D'),
('Turkey', 'D'),
('USA', 'D'),

-- GROUP E
('Curaçao', 'E'),
('Ecuador', 'E'),
('Germany', 'E'),
('Ivory Coast', 'E'),

-- GROUP F
('Japan', 'F'),
('Netherlands', 'F'),
('Sweden', 'F'),
('Tunisia', 'F'),

-- GROUP G
('Belgium', 'G'),
('Egypt', 'G'),
('Iran', 'G'),
('New Zealand', 'G'),

-- GROUP H
('Cape Verde', 'H'),
('Saudi Arabia', 'H'),
('Spain', 'H'),
('Uruguay', 'H'),

-- GROUP I
('France', 'I'),
('Iraq', 'I'),
('Norway', 'I'),
('Senegal', 'I'),

-- GROUP J
('Algeria', 'J'),
('Argentina', 'J'),
('Austria', 'J'),
('Jordan', 'J'),

-- GROUP K
('Colombia', 'K'),
('DR Congo', 'K'),
('Portugal', 'K'),
('Uzbekistan', 'K'),

-- GROUP L
('Croatia', 'L'),
('England', 'L'),
('Ghana', 'L'),
('Panama', 'L')

ON CONFLICT (team_name) DO NOTHING;
