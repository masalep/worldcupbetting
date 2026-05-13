-- Run this in Supabase SQL Editor (Dashboard → SQL Editor → New query)

-- Groups table
create table groups (
    id         serial primary key,
    name       text unique not null,   -- display name, e.g. "Work Colleagues"
    password   text not null,          -- group-specific password
    created_at timestamptz default now()
);

-- Matches table
create table matches (
    id          serial primary key,
    match_id    text unique not null,   -- e.g. "A1", "G4"
    group_name  text not null,
    home_team   text not null,
    away_team   text not null,
    matchday    int,
    kickoff     timestamptz,
    home_odds   float,
    draw_odds   float,
    away_odds   float,
    odds_locked boolean default false,
    home_score  int,
    away_score  int,
    result      text check (result in ('1', 'X', '2') or result is null)
);

-- Bets table
create table bets (
    id            serial primary key,
    username      text not null,
    group_name    text not null references groups(name),
    match_id      text not null references matches(match_id),
    prediction    text not null check (prediction in ('1', 'X', '2')),
    points_earned float,              -- null = match not resolved yet
    created_at    timestamptz default now(),
    unique(username, group_name, match_id)  -- one bet per user per group per match
);

-- Group members — tracks which users belong to which groups
create table group_members (
    id         serial primary key,
    group_name text not null references groups(name),
    username   text not null,
    password   text,                   -- personal password set at registration
    unique(group_name, username)
);

-- Optional: speed up leaderboard queries
create index on bets(username);
create index on bets(match_id);
create index on group_members(group_name);
