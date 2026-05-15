# Database Initialization Guide

## Fresh Database Setup (Run in this order)

To set up the database from scratch, run these SQL files in Supabase SQL Editor in the following order:

### 1. **init_schema.sql** (REQUIRED - Run first)
Creates all database tables and indexes:
- groups, group_members (with 8 validation columns)
- teams, matches, bets
- All knockout picks tables (knockout_picks, round16_picks, quarter_picks, semi_picks, final_picks)
- tournament_winner_picks, golden_boot_picks, goal_scorers
- knockout_results (for admin to set actual results)

### 2. **init_teams.sql** (REQUIRED)
Inserts all 48 teams into their groups (A through L)

### 3. **init_matches.sql** (REQUIRED)
Inserts all 72 group stage matches with kickoff times

### 4. **init_odds.sql** (OPTIONAL)
Sets default odds (2.2 / 1.9 / 3.15) for all matches
- You can skip this and set custom odds manually via Admin panel

### 5. **init_goalscorers.sql** (REQUIRED)
Inserts sample goal scorers (20 players) for Golden Boot predictions
- Add more players as needed before tournament starts

## Migration Files (For Updating Existing Databases)

These are for adding features to an already-running database:

- **migration_winner_golden_boot.sql** - Adds winner and golden boot picks (already included in init_schema.sql)
- **migration_knockout_results.sql** - Adds knockout_results table (already included in init_schema.sql)

⚠️ **Note**: If you're starting fresh, you only need the init_*.sql files above. Migration files are only for updating existing databases.

## Initialization Order Summary

```bash
1. init_schema.sql       # Create all tables
2. init_teams.sql        # Insert 48 teams
3. init_matches.sql      # Insert 72 matches
4. init_odds.sql         # (Optional) Set default odds
5. init_goalscorers.sql  # Insert goal scorers
```

## After Initialization

The admin can then:
- Create groups via Admin panel
- Users can join groups and start making predictions
- Admin sets match results as games are played
- Admin sets knockout results to calculate knockout points
