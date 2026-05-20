-- migration_budget_90_coins.sql
-- Updates betting constraints: 90 coins total, max 2 coins per match
-- Run this in Supabase SQL Editor if you already have the database initialized

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
-- - Use exactly 90 coins total (not 10)
-- - Bet max 2 coins per match (not 10)
-- - Still need to bet on all 72 matches
