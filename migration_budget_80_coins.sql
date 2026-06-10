-- migration_budget_80_coins.sql
-- Updates betting constraints: 80 coins total, max 2 coins per match
-- Run this in Supabase SQL Editor if you already have the database initialized
--
-- NOTE: The 80-coin total budget is enforced in application code (database.py),
-- not as a SQL constraint. This migration only enforces the per-match cap (1-2)
-- and resets slip validation so users must re-confirm their slips.

-- 1. Drop old constraint on bet_amount
ALTER TABLE bets 
DROP CONSTRAINT IF EXISTS bets_bet_amount_check;

-- 2. Add new constraint: bet_amount between 1-2
ALTER TABLE bets 
ADD CONSTRAINT bets_bet_amount_check 
CHECK (bet_amount >= 1 AND bet_amount <= 2);

-- 3. Update any existing bets that exceed 2 coins to 2 coins
UPDATE bets 
SET bet_amount = 2 
WHERE bet_amount > 2;

-- 4. Reset all slip validation status (users need to revalidate with new rules)
UPDATE group_members 
SET has_valid_slip = FALSE;

-- Note: Users must now:
-- - Use exactly 80 coins total
-- - Bet max 2 coins per match
-- - Still need to bet on all 72 matches
