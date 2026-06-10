-- clear_all_bets.sql
-- Deletes ALL betting data (bets and picks) while keeping matches, teams, groups, and users
-- Run in Supabase SQL Editor to reset all betting

-- Delete all group stage bets
DELETE FROM bets;

-- Delete all knockout stage picks
DELETE FROM knockout_picks;
DELETE FROM round16_picks;
DELETE FROM quarter_picks;
DELETE FROM semi_picks;
DELETE FROM final_picks;

-- Delete tournament winner and golden boot picks
DELETE FROM tournament_winner_picks;
DELETE FROM golden_boot_picks;

-- Note: This keeps your:
-- ✅ groups table (group data intact)
-- ✅ group_members table (users still in their groups)
-- ✅ teams table (team data intact)
-- ✅ matches table (matches and odds intact)
-- ✅ goal_scorers table (player list intact)
-- ✅ knockout_results table (if you've entered any results)

-- After running this, all users can start fresh with their 80 kredit budget
