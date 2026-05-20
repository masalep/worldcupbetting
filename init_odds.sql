-- init_odds.sql
-- Sets betting odds for all 72 group stage matches.
-- Decimal odds format (Home | Draw | Away)
-- Source: Oddspedia.com (verified real odds as of May 2026)
-- Run in Supabase SQL Editor after running init_matches.sql
-- Safe to re-run — updates odds for matches.

-- GROUP A
UPDATE matches SET home_odds = 1.55, draw_odds = 4.30, away_odds = 7.00 WHERE match_id = 'A1';
UPDATE matches SET home_odds = 2.75, draw_odds = 3.33, away_odds = 2.83 WHERE match_id = 'A2';
UPDATE matches SET home_odds = 2.10, draw_odds = 3.50, away_odds = 4.15 WHERE match_id = 'A3';
UPDATE matches SET home_odds = 1.96, draw_odds = 3.70, away_odds = 4.75 WHERE match_id = 'A4';
UPDATE matches SET home_odds = 4.20, draw_odds = 3.65, away_odds = 2.12 WHERE match_id = 'A5';
UPDATE matches SET home_odds = 3.95, draw_odds = 3.40, away_odds = 2.47 WHERE match_id = 'A6';

-- GROUP B
UPDATE matches SET home_odds = 1.83, draw_odds = 4.00, away_odds = 4.80 WHERE match_id = 'B1';
UPDATE matches SET home_odds = 12.00, draw_odds = 6.00, away_odds = 1.33 WHERE match_id = 'B2';
UPDATE matches SET home_odds = 1.58, draw_odds = 4.30, away_odds = 6.75 WHERE match_id = 'B3';
UPDATE matches SET home_odds = 1.53, draw_odds = 4.50, away_odds = 7.50 WHERE match_id = 'B4';
UPDATE matches SET home_odds = 2.12, draw_odds = 3.70, away_odds = 3.70 WHERE match_id = 'B5';
UPDATE matches SET home_odds = 1.95, draw_odds = 3.60, away_odds = 4.25 WHERE match_id = 'B6';

-- GROUP C
UPDATE matches SET home_odds = 1.65, draw_odds = 4.10, away_odds = 6.20 WHERE match_id = 'C1';
UPDATE matches SET home_odds = 8.00, draw_odds = 5.00, away_odds = 1.48 WHERE match_id = 'C2';
UPDATE matches SET home_odds = 3.76, draw_odds = 3.32, away_odds = 2.17 WHERE match_id = 'C3';
UPDATE matches SET home_odds = 1.07, draw_odds = 17.00, away_odds = 51.00 WHERE match_id = 'C4';
UPDATE matches SET home_odds = 9.00, draw_odds = 5.33, away_odds = 1.40 WHERE match_id = 'C5';
UPDATE matches SET home_odds = 1.31, draw_odds = 5.80, away_odds = 11.00 WHERE match_id = 'C6';

-- GROUP D
UPDATE matches SET home_odds = 2.06, draw_odds = 3.60, away_odds = 3.90 WHERE match_id = 'D1';
UPDATE matches SET home_odds = 5.00, draw_odds = 3.80, away_odds = 1.86 WHERE match_id = 'D2';
UPDATE matches SET home_odds = 1.77, draw_odds = 4.05, away_odds = 5.00 WHERE match_id = 'D3';
UPDATE matches SET home_odds = 2.30, draw_odds = 3.28, away_odds = 3.50 WHERE match_id = 'D4';
UPDATE matches SET home_odds = 3.05, draw_odds = 3.50, away_odds = 2.54 WHERE match_id = 'D5';
UPDATE matches SET home_odds = 2.36, draw_odds = 3.55, away_odds = 4.20 WHERE match_id = 'D6';

-- GROUP E
UPDATE matches SET home_odds = 1.04, draw_odds = 22.00, away_odds = 51.00 WHERE match_id = 'E1';
UPDATE matches SET home_odds = 3.71, draw_odds = 3.20, away_odds = 2.41 WHERE match_id = 'E2';
UPDATE matches SET home_odds = 1.61, draw_odds = 4.35, away_odds = 6.00 WHERE match_id = 'E3';
UPDATE matches SET home_odds = 1.27, draw_odds = 6.25, away_odds = 14.00 WHERE match_id = 'E4';
UPDATE matches SET home_odds = 12.20, draw_odds = 6.00, away_odds = 1.29 WHERE match_id = 'E5';
UPDATE matches SET home_odds = 5.80, draw_odds = 4.20, away_odds = 1.62 WHERE match_id = 'E6';

-- GROUP F
UPDATE matches SET home_odds = 2.08, draw_odds = 3.76, away_odds = 3.88 WHERE match_id = 'F1';
UPDATE matches SET home_odds = 2.00, draw_odds = 3.54, away_odds = 4.30 WHERE match_id = 'F2';
UPDATE matches SET home_odds = 1.72, draw_odds = 4.15, away_odds = 5.65 WHERE match_id = 'F3';
UPDATE matches SET home_odds = 4.80, draw_odds = 3.44, away_odds = 1.94 WHERE match_id = 'F4';
UPDATE matches SET home_odds = 2.30, draw_odds = 3.45, away_odds = 3.25 WHERE match_id = 'F5';
UPDATE matches SET home_odds = 7.95, draw_odds = 4.70, away_odds = 1.53 WHERE match_id = 'F6';

-- GROUP G
UPDATE matches SET home_odds = 1.73, draw_odds = 4.10, away_odds = 5.20 WHERE match_id = 'G1';
UPDATE matches SET home_odds = 1.88, draw_odds = 3.75, away_odds = 4.90 WHERE match_id = 'G2';
UPDATE matches SET home_odds = 1.45, draw_odds = 4.70, away_odds = 8.25 WHERE match_id = 'G3';
UPDATE matches SET home_odds = 5.25, draw_odds = 3.90, away_odds = 1.75 WHERE match_id = 'G4';
UPDATE matches SET home_odds = 2.53, draw_odds = 3.31, away_odds = 3.40 WHERE match_id = 'G5';
UPDATE matches SET home_odds = 15.00, draw_odds = 7.20, away_odds = 1.22 WHERE match_id = 'G6';

-- GROUP H
UPDATE matches SET home_odds = 1.11, draw_odds = 11.00, away_odds = 33.00 WHERE match_id = 'H1';
UPDATE matches SET home_odds = 7.00, draw_odds = 4.40, away_odds = 1.54 WHERE match_id = 'H2';
UPDATE matches SET home_odds = 1.13, draw_odds = 9.00, away_odds = 36.00 WHERE match_id = 'H3';
UPDATE matches SET home_odds = 1.48, draw_odds = 4.55, away_odds = 7.75 WHERE match_id = 'H4';
UPDATE matches SET home_odds = 3.80, draw_odds = 3.52, away_odds = 2.27 WHERE match_id = 'H5';
UPDATE matches SET home_odds = 7.33, draw_odds = 4.71, away_odds = 1.67 WHERE match_id = 'H6';

-- GROUP I
UPDATE matches SET home_odds = 1.48, draw_odds = 4.70, away_odds = 7.60 WHERE match_id = 'I1';
UPDATE matches SET home_odds = 14.25, draw_odds = 6.50, away_odds = 1.28 WHERE match_id = 'I2';
UPDATE matches SET home_odds = 1.15, draw_odds = 8.60, away_odds = 26.00 WHERE match_id = 'I3';
UPDATE matches SET home_odds = 2.15, draw_odds = 3.68, away_odds = 3.70 WHERE match_id = 'I4';
UPDATE matches SET home_odds = 6.21, draw_odds = 4.57, away_odds = 1.70 WHERE match_id = 'I5';
UPDATE matches SET home_odds = 1.56, draw_odds = 5.96, away_odds = 13.90 WHERE match_id = 'I6';

-- GROUP J
UPDATE matches SET home_odds = 1.43, draw_odds = 4.75, away_odds = 9.50 WHERE match_id = 'J1';
UPDATE matches SET home_odds = 1.37, draw_odds = 5.50, away_odds = 9.50 WHERE match_id = 'J2';
UPDATE matches SET home_odds = 1.74, draw_odds = 3.80, away_odds = 5.50 WHERE match_id = 'J3';
UPDATE matches SET home_odds = 5.25, draw_odds = 3.82, away_odds = 1.77 WHERE match_id = 'J4';
UPDATE matches SET home_odds = 3.10, draw_odds = 3.30, away_odds = 2.44 WHERE match_id = 'J5';
UPDATE matches SET home_odds = 21.00, draw_odds = 8.60, away_odds = 1.16 WHERE match_id = 'J6';

-- GROUP K
UPDATE matches SET home_odds = 1.29, draw_odds = 6.00, away_odds = 12.50 WHERE match_id = 'K1';
UPDATE matches SET home_odds = 8.40, draw_odds = 4.80, away_odds = 1.47 WHERE match_id = 'K2';
UPDATE matches SET home_odds = 1.26, draw_odds = 7.00, away_odds = 17.00 WHERE match_id = 'K3';
UPDATE matches SET home_odds = 1.55, draw_odds = 4.25, away_odds = 7.75 WHERE match_id = 'K4';
UPDATE matches SET home_odds = 3.44, draw_odds = 3.60, away_odds = 2.24 WHERE match_id = 'K5';
UPDATE matches SET home_odds = 2.47, draw_odds = 3.36, away_odds = 3.45 WHERE match_id = 'K6';

-- GROUP L
UPDATE matches SET home_odds = 1.73, draw_odds = 4.00, away_odds = 5.25 WHERE match_id = 'L1';
UPDATE matches SET home_odds = 2.01, draw_odds = 4.00, away_odds = 4.35 WHERE match_id = 'L2';
UPDATE matches SET home_odds = 1.35, draw_odds = 5.40, away_odds = 10.50 WHERE match_id = 'L3';
UPDATE matches SET home_odds = 7.80, draw_odds = 4.30, away_odds = 1.56 WHERE match_id = 'L4';
UPDATE matches SET home_odds = 21.00, draw_odds = 8.60, away_odds = 1.17 WHERE match_id = 'L5';
UPDATE matches SET home_odds = 1.97, draw_odds = 3.71, away_odds = 4.30 WHERE match_id = 'L6';
