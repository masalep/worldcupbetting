# ⚽ World Cup 2026 Betting Pool

A Streamlit-based betting pool application for the 2026 FIFA World Cup (or any tournament).

## Features

- 🎯 **1X2 Betting System** - Predict Home win (1), Draw (X), or Away win (2)
- 📊 **Odds-based Scoring** - Earn points based on betting odds
- 👥 **Group Management** - Create multiple betting groups with passwords
- 🔒 **Betting Lock Control** - Lock betting when tournament starts
- 🏆 **Live Leaderboard** - Real-time standings with points tracking
- ✏️ **Easy Result Entry** - Editable table for entering match results

## Setup

### Prerequisites

- Python 3.11+
- Supabase account
- uv package manager (or pip)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd worldcup
```

2. Install dependencies:
```bash
uv venv
uv pip install -r requirements.txt
```

3. Set up Supabase:
   - Create a new project at [supabase.com](https://supabase.com)
   - Run `init_schema.sql` in the SQL Editor
   - Run `init_matches.sql` to load matches
   - Run `init_odds.sql` to set odds

4. Configure secrets:
   - Create `.streamlit/secrets.toml`
   - Add your Supabase credentials:
```toml
SUPABASE_URL = "your-project-url"
SUPABASE_KEY = "your-anon-key"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "your-admin-password"
```

5. Run the app:
```bash
uv run streamlit run app.py
```

## Deployment to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add secrets in Streamlit Cloud settings
5. Deploy!

## Usage

### For Users
1. Join a group with the group password
2. Create an account with your name and personal password
3. Place your bets before tournament starts
4. Watch the leaderboard update as results come in!

### For Admins
1. Login with admin credentials
2. **Groups tab**: Create groups and manage members
3. **Odds tab**: Lock/unlock betting
4. **Results tab**: Enter match results in the editable table

## Database Schema

- `groups` - Betting groups
- `group_members` - Users in each group
- `matches` - All tournament matches with odds
- `bets` - User predictions and points earned

## License

MIT
