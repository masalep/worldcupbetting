-- migration_budget_system.sql
-- Adds budget betting system with bet amounts and valid slip tracking
-- Run this in Supabase SQL Editor

-- 1. Add bet_amount column to bets table
ALTER TABLE bets 
ADD COLUMN IF NOT EXISTS bet_amount INTEGER DEFAULT 1 
CHECK (bet_amount >= 1 AND bet_amount <= 10);

-- 2. Add has_valid_slip column to group_members table
ALTER TABLE group_members 
ADD COLUMN IF NOT EXISTS has_valid_slip BOOLEAN DEFAULT FALSE;

-- 3. Update existing bets to have bet_amount = 1 (if any exist)
UPDATE bets SET bet_amount = 1 WHERE bet_amount IS NULL;

-- 4. Update init_schema.sql reference for future rebuilds:
-- The bets table should now include bet_amount
-- The group_members table should now include has_valid_slip
