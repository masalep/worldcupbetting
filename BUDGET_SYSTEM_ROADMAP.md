# Budget Betting System Implementation Roadmap

## ✅ COMPLETED:
1. Database migration (bet_amount, has_valid_slip columns)
2. Updated init_schema.sql for clean builds
3. Updated database.py:
   - save_bet() now accepts bet_amount
   - validate_and_set_slip_status() function
   - get_member_slip_status() function

## 🚧 TODO:

### Phase 1: Update Betting UI
- [ ] Add bet amount input (1-10 coins) next to each match prediction
- [ ] Show running total at top: "Budget: 45/100 coins used · 28/72 matches bet"
- [ ] Validate on save:
  - All 72 matches must have bets
  - Total coins must equal exactly 100
  - Each bet between 1-10 coins
- [ ] Call validate_and_set_slip_status() after successful save
- [ ] Show success/error messages based on validation

### Phase 2: Update Admin Panel
- [ ] In Groups tab, show member slip status:
  - ✅ Matti (Valid slip - 100 coins on 72 matches)
  - ⏳ Pekka (Incomplete - 50 coins on 30 matches)
- [ ] Add "Remind incomplete" button (optional)

### Phase 3: Update Leaderboard
- [ ] Change from points to total_winnings
- [ ] Show: Username, Total Winnings, Current Balance, ROI%
- [ ] Add badge/filter for valid slips only
- [ ] Sort by total winnings DESC

### Phase 4: Update Points Calculation
- [ ] When set_result() is called:
  - Calculate: winnings = bet_amount × odds (if correct)
  - Update points_earned in bets table
  - These become the "total_winnings"

## UI Mockup for Betting Page:

```
⚽ Place Your Bets
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 Budget: 45/100 coins · 🎯 Matches: 28/72 bet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Group: [A ▼]

┌─────────────────────────────────────────────┐
│ A1 · Mexico vs South Africa                │
│ Odds: 1: 2.20 · X: 1.90 · 2: 3.15         │
│                                              │
│ Prediction: ( 1 ) ( X ) ( 2 )              │
│ Bet amount: [5 ▼] coins                    │
└─────────────────────────────────────────────┘

[💾 Save All Bets]
```

## Validation Messages:

❌ "You must bet on all 72 matches! Currently: 28/72"
❌ "Budget must equal 100 coins! Currently: 45 coins"
✅ "Valid slip! 100 coins on all 72 matches. Ready to compete!"

## Database Query for Leaderboard:

```sql
SELECT 
  username,
  SUM(points_earned) as total_winnings,
  100 + SUM(points_earned) - SUM(bet_amount) as current_balance,
  (SUM(points_earned) / 100.0 * 100) as roi_percent
FROM bets
WHERE group_name = 'MyGroup'
GROUP BY username
ORDER BY total_winnings DESC
```
