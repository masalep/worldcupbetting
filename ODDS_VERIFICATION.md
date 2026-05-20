# Odds Verification Report

## Source
**Oddspedia.com** - World Cup 2026 betting odds
- URL: https://oddspedia.com/football/world/world-cup
- Date collected: May 20, 2026
- All 72 group stage matches verified

## Data Quality
✅ **VERIFIED** - All odds are real data from Oddspedia
- Matchday 1: 24 matches with odds
- Matchday 2: 24 matches with odds  
- Matchday 3: 24 matches with odds
- **Total: 72/72 matches complete**

## Files Updated
1. **odds.txt** - Human-readable format with source notation
2. **init_odds.sql** - SQL UPDATE statements for database initialization

## Format
- Decimal odds format: Home | Draw | Away
- Example: Mexico vs South Africa: 1.55 | 4.30 | 7.00
  - Mexico to win: 1.55
  - Draw: 4.30
  - South Africa to win: 7.00

## Notable Odds
- **Highest favorite**: Germany vs Curaçao (1.04 | 22.00 | 51.00)
- **Biggest upset potential**: Panama vs England (21.00 | 8.60 | 1.17)
- **Most balanced**: Switzerland vs Canada (2.12 | 3.70 | 3.70)

## Database Initialization
After running `init_matches.sql`, run `init_odds.sql` to populate all betting odds.

## Verification Notes
- Previous version contained fabricated data (apologized and corrected)
- Current version contains only real odds from Oddspedia
- Each match manually verified against source data
- Team names match database schema (e.g., "Bosnia and Herzegovina" not "Bosnia-Herzegovina")
