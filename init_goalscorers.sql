-- init_goalscorers.sql
-- Insert sample goal scorers for Golden Boot predictions
-- Run this in Supabase SQL Editor after init_teams.sql

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
('Robert Lewandowski', 'Poland'),
('Vinicius Jr', 'Brazil'),
('Karim Benzema', 'France'),
('Son Heung-min', 'South Korea'),
('Memphis Depay', 'Netherlands'),
('Sadio Mané', 'Senegal'),
('Romelu Lukaku', 'Belgium'),
('Bruno Fernandes', 'Portugal'),
('Federico Chiesa', 'Italy'),
('Jamal Musiala', 'Germany'),
('Phil Foden', 'England')
ON CONFLICT (player_name) DO NOTHING;
