-- enable_rls.sql
-- Enable Row Level Security on all tables
-- This prevents public access to your data
-- Run this in Supabase SQL Editor

-- Enable RLS on all tables
ALTER TABLE groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE bets ENABLE ROW LEVEL SECURITY;
ALTER TABLE knockout_picks ENABLE ROW LEVEL SECURITY;
ALTER TABLE round16_picks ENABLE ROW LEVEL SECURITY;
ALTER TABLE quarter_picks ENABLE ROW LEVEL SECURITY;
ALTER TABLE semi_picks ENABLE ROW LEVEL SECURITY;
ALTER TABLE final_picks ENABLE ROW LEVEL SECURITY;
ALTER TABLE tournament_winner_picks ENABLE ROW LEVEL SECURITY;
ALTER TABLE golden_boot_picks ENABLE ROW LEVEL SECURITY;
ALTER TABLE goal_scorers ENABLE ROW LEVEL SECURITY;
ALTER TABLE knockout_results ENABLE ROW LEVEL SECURITY;

-- Create policies that BLOCK all anon key access
-- Your Streamlit app uses the service_role key which bypasses RLS entirely
-- So your app will work normally, but the anon key cannot access anything

-- No policies needed! 
-- When RLS is enabled and no policies exist, the default behavior is DENY ALL
-- The service_role key bypasses RLS, so your app can still do everything

-- This means:
-- ✅ Your Streamlit app (service_role key) = full access to everything
-- ❌ Anon key = cannot read, insert, update, or delete anything
-- ❌ Direct API calls with anon key = completely blocked
-- ❌ Someone who finds your anon key = cannot do anything with it
