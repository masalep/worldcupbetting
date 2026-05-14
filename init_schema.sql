-- init_schema.sql
-- Creates a clean schema for 1X2 betting platform

DROP TABLE IF EXISTS knockout_picks;
DROP TABLE IF EXISTS bets;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS group_members;
DROP TABLE IF EXISTS groups;

CREATE TABLE groups (
    name TEXT PRIMARY KEY,
    password TEXT NOT NULL
);

CREATE TABLE group_members (
    group_name TEXT REFERENCES groups(name),
    username TEXT,
    password TEXT NOT NULL,
    has_valid_slip BOOLEAN DEFAULT FALSE,
    has_valid_knockout_picks BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (group_name, username)
);

CREATE TABLE teams (
    team_name TEXT PRIMARY KEY,
    group_name TEXT NOT NULL
);

CREATE TABLE matches (
    match_id TEXT PRIMARY KEY,
    group_name TEXT,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    matchday INTEGER,
    kickoff TIMESTAMP,
    home_odds FLOAT,
    draw_odds FLOAT,
    away_odds FLOAT,
    betting_locked BOOLEAN DEFAULT FALSE,
    result TEXT CHECK (result IN ('1', 'X', '2'))
);

CREATE TABLE bets (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    match_id TEXT NOT NULL REFERENCES matches(match_id),
    prediction TEXT CHECK (prediction IN ('1', 'X', '2')),
    bet_amount INTEGER DEFAULT 1 CHECK (bet_amount >= 1 AND bet_amount <= 10),
    points_earned FLOAT DEFAULT 0,
    UNIQUE (username, group_name, match_id)
);

CREATE TABLE knockout_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    team TEXT NOT NULL,
    PRIMARY KEY (username, group_name, team)
);
