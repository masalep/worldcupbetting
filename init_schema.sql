-- init_schema.sql
-- Creates a clean schema for 1X2 betting platform

DROP TABLE IF EXISTS knockout_results;
DROP TABLE IF EXISTS tournament_winner_picks;
DROP TABLE IF EXISTS golden_boot_picks;
DROP TABLE IF EXISTS goal_scorers;
DROP TABLE IF EXISTS final_picks;
DROP TABLE IF EXISTS semi_picks;
DROP TABLE IF EXISTS quarter_picks;
DROP TABLE IF EXISTS round16_picks;
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
    has_valid_round16_picks BOOLEAN DEFAULT FALSE,
    has_valid_quarter_picks BOOLEAN DEFAULT FALSE,
    has_valid_semi_picks BOOLEAN DEFAULT FALSE,
    has_valid_final_picks BOOLEAN DEFAULT FALSE,
    has_valid_winner_pick BOOLEAN DEFAULT FALSE,
    has_valid_golden_boot_pick BOOLEAN DEFAULT FALSE,
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
    bet_amount INTEGER DEFAULT 1 CHECK (bet_amount >= 1 AND bet_amount <= 2),
    points_earned FLOAT DEFAULT 0,
    UNIQUE (username, group_name, match_id)
);

CREATE TABLE knockout_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    team TEXT NOT NULL,
    PRIMARY KEY (username, group_name, team)
);

CREATE TABLE round16_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    team TEXT NOT NULL,
    PRIMARY KEY (username, group_name, team)
);

CREATE TABLE quarter_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    team TEXT NOT NULL,
    PRIMARY KEY (username, group_name, team)
);

CREATE TABLE semi_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    team TEXT NOT NULL,
    PRIMARY KEY (username, group_name, team)
);

CREATE TABLE final_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    team TEXT NOT NULL,
    is_winner BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (username, group_name, team)
);

CREATE TABLE tournament_winner_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    team TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (username, group_name)
);

CREATE TABLE golden_boot_picks (
    username TEXT NOT NULL,
    group_name TEXT NOT NULL,
    player_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (username, group_name)
);

CREATE TABLE goal_scorers (
    player_name TEXT PRIMARY KEY,
    team TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE knockout_results (
    id SERIAL PRIMARY KEY,
    stage TEXT NOT NULL,
    team TEXT,
    player_name TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stage, team, player_name)
);

-- Indexes
CREATE INDEX idx_bets_username ON bets(username);
CREATE INDEX idx_bets_match ON bets(match_id);
CREATE INDEX idx_knockout_picks_user ON knockout_picks(username, group_name);
CREATE INDEX idx_round16_picks_user ON round16_picks(username, group_name);
CREATE INDEX idx_quarter_picks_user ON quarter_picks(username, group_name);
CREATE INDEX idx_semi_picks_user ON semi_picks(username, group_name);
CREATE INDEX idx_final_picks_user ON final_picks(username, group_name);
CREATE INDEX idx_tournament_winner_picks_user ON tournament_winner_picks(username, group_name);
CREATE INDEX idx_golden_boot_picks_user ON golden_boot_picks(username, group_name);
CREATE INDEX idx_goal_scorers_team ON goal_scorers(team);
CREATE INDEX idx_knockout_results_stage ON knockout_results(stage);
