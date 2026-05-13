-- init_matches.sql
-- All 72 group stage matches for the 2026 FIFA World Cup.
-- Kickoff times in UTC (converted from official local times).
-- Run in Supabase SQL Editor. Safe to re-run — updates kickoff times on conflict.

INSERT INTO matches (match_id, group_name, home_team, away_team, matchday, kickoff, home_odds, draw_odds, away_odds, betting_locked)
VALUES
-- GROUP A: Mexico, South Africa, South Korea, Czech Republic
('A1', 'A', 'Mexico', 'South Africa', 1, '2026-06-11T19:00:00+00:00', NULL, NULL, NULL, FALSE),
('A2', 'A', 'South Korea', 'Czech Republic', 1, '2026-06-12T02:00:00+00:00', NULL, NULL, NULL, FALSE),
('A3', 'A', 'Czech Republic', 'South Africa', 2, '2026-06-18T16:00:00+00:00', NULL, NULL, NULL, FALSE),
('A4', 'A', 'Mexico', 'South Korea', 2, '2026-06-19T01:00:00+00:00', NULL, NULL, NULL, FALSE),
('A5', 'A', 'Czech Republic', 'Mexico', 3, '2026-06-25T01:00:00+00:00', NULL, NULL, NULL, FALSE),
('A6', 'A', 'South Africa', 'South Korea', 3, '2026-06-25T01:00:00+00:00', NULL, NULL, NULL, FALSE),

-- GROUP B: Canada, Bosnia and Herzegovina, Qatar, Switzerland
('B1', 'B', 'Canada', 'Bosnia and Herzegovina', 1, '2026-06-12T19:00:00+00:00', NULL, NULL, NULL, FALSE),
('B2', 'B', 'Qatar', 'Switzerland', 1, '2026-06-13T19:00:00+00:00', NULL, NULL, NULL, FALSE),
('B3', 'B', 'Switzerland', 'Bosnia and Herzegovina', 2, '2026-06-18T19:00:00+00:00', NULL, NULL, NULL, FALSE),
('B4', 'B', 'Canada', 'Qatar', 2, '2026-06-18T22:00:00+00:00', NULL, NULL, NULL, FALSE),
('B5', 'B', 'Switzerland', 'Canada', 3, '2026-06-24T19:00:00+00:00', NULL, NULL, NULL, FALSE),
('B6', 'B', 'Bosnia and Herzegovina', 'Qatar', 3, '2026-06-24T19:00:00+00:00', NULL, NULL, NULL, FALSE),

-- GROUP C: Brazil, Morocco, Haiti, Scotland
('C1', 'C', 'Brazil', 'Morocco', 1, '2026-06-13T22:00:00+00:00', NULL, NULL, NULL, FALSE),
('C2', 'C', 'Haiti', 'Scotland', 1, '2026-06-14T01:00:00+00:00', NULL, NULL, NULL, FALSE),
('C3', 'C', 'Scotland', 'Morocco', 2, '2026-06-19T22:00:00+00:00', NULL, NULL, NULL, FALSE),
('C4', 'C', 'Brazil', 'Haiti', 2, '2026-06-20T00:30:00+00:00', NULL, NULL, NULL, FALSE),
('C5', 'C', 'Scotland', 'Brazil', 3, '2026-06-24T22:00:00+00:00', NULL, NULL, NULL, FALSE),
('C6', 'C', 'Morocco', 'Haiti', 3, '2026-06-24T22:00:00+00:00', NULL, NULL, NULL, FALSE),

-- GROUP D: USA, Paraguay, Australia, Turkey
('D1', 'D', 'USA', 'Paraguay', 1, '2026-06-13T01:00:00+00:00', NULL, NULL, NULL, FALSE),
('D2', 'D', 'Australia', 'Turkey', 1, '2026-06-14T04:00:00+00:00', NULL, NULL, NULL, FALSE),
('D3', 'D', 'USA', 'Australia', 2, '2026-06-19T19:00:00+00:00', NULL, NULL, NULL, FALSE),
('D4', 'D', 'Turkey', 'Paraguay', 2, '2026-06-20T03:00:00+00:00', NULL, NULL, NULL, FALSE),
('D5', 'D', 'Turkey', 'USA', 3, '2026-06-26T02:00:00+00:00', NULL, NULL, NULL, FALSE),
('D6', 'D', 'Paraguay', 'Australia', 3, '2026-06-26T02:00:00+00:00', NULL, NULL, NULL, FALSE),

-- GROUP E: Germany, Curaçao, Ivory Coast, Ecuador
('E1', 'E', 'Germany', 'Curaçao', 1, '2026-06-14T17:00:00+00:00', NULL, NULL, NULL, FALSE),
('E2', 'E', 'Ivory Coast', 'Ecuador', 1, '2026-06-14T23:00:00+00:00', NULL, NULL, NULL, FALSE),
('E3', 'E', 'Germany', 'Ivory Coast', 2, '2026-06-20T20:00:00+00:00', NULL, NULL, NULL, FALSE),
('E4', 'E', 'Ecuador', 'Curaçao', 2, '2026-06-21T00:00:00+00:00', NULL, NULL, NULL, FALSE),
('E5', 'E', 'Curaçao', 'Ivory Coast', 3, '2026-06-25T20:00:00+00:00', NULL, NULL, NULL, FALSE),
('E6', 'E', 'Ecuador', 'Germany', 3, '2026-06-25T20:00:00+00:00', NULL, NULL, NULL, FALSE),

-- GROUP F: Netherlands, Japan, Sweden, Tunisia
('F1', 'F', 'Netherlands', 'Japan', 1, '2026-06-14T20:00:00+00:00', NULL, NULL, NULL, FALSE),
('F2', 'F', 'Sweden', 'Tunisia', 1, '2026-06-15T02:00:00+00:00', NULL, NULL, NULL, FALSE),
('F3', 'F', 'Netherlands', 'Sweden', 2, '2026-06-20T17:00:00+00:00', NULL, NULL, NULL, FALSE),
('F4', 'F', 'Tunisia', 'Japan', 2, '2026-06-21T04:00:00+00:00', NULL, NULL, NULL, FALSE),
('F5', 'F', 'Japan', 'Sweden', 3, '2026-06-25T23:00:00+00:00', NULL, NULL, NULL, FALSE),
('F6', 'F', 'Tunisia', 'Netherlands', 3, '2026-06-25T23:00:00+00:00', NULL, NULL, NULL, FALSE),

-- GROUP G: Belgium, Egypt, Iran, New Zealand
('G1', 'G', 'Belgium', 'Egypt', 1, '2026-06-15T19:00:00+00:00', NULL, NULL, NULL, FALSE),
('G2', 'G', 'Iran', 'New Zealand', 1, '2026-06-16T01:00:00+00:00', NULL, NULL, NULL, FALSE),
('G3', 'G', 'Belgium', 'Iran', 2, '2026-06-21T19:00:00+00:00', NULL, NULL, NULL, FALSE),
('G4', 'G', 'New Zealand', 'Egypt', 2, '2026-06-22T01:00:00+00:00', NULL, NULL, NULL, FALSE),
('G5', 'G', 'Egypt', 'Iran', 3, '2026-06-27T03:00:00+00:00', NULL, NULL, NULL, FALSE),
('G6', 'G', 'New Zealand', 'Belgium', 3, '2026-06-27T03:00:00+00:00', NULL, NULL, NULL, FALSE),

-- GROUP H: Spain, Cape Verde, Saudi Arabia, Uruguay
('H1', 'H', 'Spain', 'Cape Verde', 1, '2026-06-15T16:00:00+00:00', NULL, NULL, NULL, FALSE),
('H2', 'H', 'Saudi Arabia', 'Uruguay', 1, '2026-06-15T22:00:00+00:00', NULL, NULL, NULL, FALSE),
('H3', 'H', 'Spain', 'Saudi Arabia', 2, '2026-06-21T16:00:00+00:00', NULL, NULL, NULL, FALSE),
('H4', 'H', 'Uruguay', 'Cape Verde', 2, '2026-06-21T22:00:00+00:00', NULL, NULL, NULL, FALSE),
('H5', 'H', 'Cape Verde', 'Saudi Arabia', 3, '2026-06-27T00:00:00+00:00', NULL, NULL, NULL, FALSE),
('H6', 'H', 'Uruguay', 'Spain', 3, '2026-06-27T00:00:00+00:00', NULL, NULL, NULL, FALSE),

-- GROUP I: France, Senegal, Iraq, Norway
('I1', 'I', 'France', 'Senegal', 1, '2026-06-16T19:00:00+00:00', NULL, NULL, NULL, FALSE),
('I2', 'I', 'Iraq', 'Norway', 1, '2026-06-16T22:00:00+00:00', NULL, NULL, NULL, FALSE),
('I3', 'I', 'France', 'Iraq', 2, '2026-06-22T21:00:00+00:00', NULL, NULL, NULL, FALSE),
('I4', 'I', 'Norway', 'Senegal', 2, '2026-06-23T00:00:00+00:00', NULL, NULL, NULL, FALSE),
('I5', 'I', 'Norway', 'France', 3, '2026-06-26T19:00:00+00:00', NULL, NULL, NULL, FALSE),
('I6', 'I', 'Senegal', 'Iraq', 3, '2026-06-26T19:00:00+00:00', NULL, NULL, NULL, FALSE),

-- GROUP J: Argentina, Algeria, Austria, Jordan
('J1', 'J', 'Argentina', 'Algeria', 1, '2026-06-17T01:00:00+00:00', NULL, NULL, NULL, FALSE),
('J2', 'J', 'Austria', 'Jordan', 1, '2026-06-17T04:00:00+00:00', NULL, NULL, NULL, FALSE),
('J3', 'J', 'Argentina', 'Austria', 2, '2026-06-22T17:00:00+00:00', NULL, NULL, NULL, FALSE),
('J4', 'J', 'Jordan', 'Algeria', 2, '2026-06-23T03:00:00+00:00', NULL, NULL, NULL, FALSE),
('J5', 'J', 'Algeria', 'Austria', 3, '2026-06-28T02:00:00+00:00', NULL, NULL, NULL, FALSE),
('J6', 'J', 'Jordan', 'Argentina', 3, '2026-06-28T02:00:00+00:00', NULL, NULL, NULL, FALSE),

-- GROUP K: Portugal, DR Congo, Uzbekistan, Colombia
('K1', 'K', 'Portugal', 'DR Congo', 1, '2026-06-17T17:00:00+00:00', NULL, NULL, NULL, FALSE),
('K2', 'K', 'Uzbekistan', 'Colombia', 1, '2026-06-18T02:00:00+00:00', NULL, NULL, NULL, FALSE),
('K3', 'K', 'Portugal', 'Uzbekistan', 2, '2026-06-23T17:00:00+00:00', NULL, NULL, NULL, FALSE),
('K4', 'K', 'Colombia', 'DR Congo', 2, '2026-06-24T02:00:00+00:00', NULL, NULL, NULL, FALSE),
('K5', 'K', 'Colombia', 'Portugal', 3, '2026-06-27T23:30:00+00:00', NULL, NULL, NULL, FALSE),
('K6', 'K', 'DR Congo', 'Uzbekistan', 3, '2026-06-27T23:30:00+00:00', NULL, NULL, NULL, FALSE),

-- GROUP L: England, Croatia, Ghana, Panama
('L1', 'L', 'England', 'Croatia', 1, '2026-06-17T20:00:00+00:00', NULL, NULL, NULL, FALSE),
('L2', 'L', 'Ghana', 'Panama', 1, '2026-06-17T23:00:00+00:00', NULL, NULL, NULL, FALSE),
('L3', 'L', 'England', 'Ghana', 2, '2026-06-23T20:00:00+00:00', NULL, NULL, NULL, FALSE),
('L4', 'L', 'Panama', 'Croatia', 2, '2026-06-23T23:00:00+00:00', NULL, NULL, NULL, FALSE),
('L5', 'L', 'Panama', 'England', 3, '2026-06-27T21:00:00+00:00', NULL, NULL, NULL, FALSE),
('L6', 'L', 'Croatia', 'Ghana', 3, '2026-06-27T21:00:00+00:00', NULL, NULL, NULL, FALSE)

ON CONFLICT (match_id) DO UPDATE SET kickoff = EXCLUDED.kickoff;
