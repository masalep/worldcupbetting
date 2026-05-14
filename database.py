# database.py — all Supabase operations
import streamlit as st
from supabase import create_client


@st.cache_resource
def get_supabase():
    """Create and cache the Supabase client."""
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


# ── Groups ─────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def get_groups() -> list:
    sb = get_supabase()
    return sb.table("groups").select("*").order("name").execute().data


def create_group(name: str, password: str):
    sb = get_supabase()
    sb.table("groups").insert({"name": name, "password": password}).execute()
    get_groups.clear()


def verify_group(name: str, password: str) -> bool:
    """Return True if group exists and password matches."""
    sb = get_supabase()
    rows = sb.table("groups").select("password").eq("name", name).execute().data
    return bool(rows) and rows[0]["password"] == password


def join_group(group_name: str, username: str, password: str):
    """Add user to group with a personal password. Raises if username already exists in group."""
    sb = get_supabase()
    sb.table("group_members").insert(
        {"group_name": group_name, "username": username, "password": password}
    ).execute()


def verify_member(group_name: str, username: str, password: str) -> bool:
    """Return True if the username+password match in this group."""
    sb = get_supabase()
    rows = sb.table("group_members").select("password") \
             .eq("group_name", group_name).eq("username", username).execute().data
    return bool(rows) and rows[0]["password"] == password


@st.cache_data(ttl=30)
def get_group_members(group_name: str) -> list:
    """Return list of usernames in a group."""
    sb = get_supabase()
    rows = sb.table("group_members").select("username").eq("group_name", group_name).order("username").execute().data
    return [r["username"] for r in rows]


def remove_group_member(group_name: str, username: str):
    """Remove a player from a group."""
    sb = get_supabase()
    sb.table("group_members").delete().eq("group_name", group_name).eq("username", username).execute()
    get_group_members.clear()



def init_matches(matches: list):
    """Insert all matches into Supabase (upsert — safe to run multiple times)."""
    sb = get_supabase()
    sb.table("matches").upsert(matches, on_conflict="match_id").execute()


@st.cache_data(ttl=3600)  # matches rarely change — cache for 1 hour, cleared manually after admin actions
def get_matches() -> list:
    """Return all matches ordered by matchday."""
    sb = get_supabase()
    return sb.table("matches").select("*").order("matchday").order("match_id").execute().data


def lock_all_odds():
    """Lock all matches that already have odds set."""
    sb = get_supabase()
    sb.table("matches").update({"betting_locked": True}).not_.is_("home_odds", "null").execute()


def unlock_all_odds():
    """Unlock all matches to allow betting again."""
    sb = get_supabase()
    sb.table("matches").update({"betting_locked": False}).not_.is_("home_odds", "null").execute()


def set_result(match_id: str, result: str):
    """Set or update the 1/X/2 result for a match and calculate points for all bets."""
    sb = get_supabase()

    if result not in ("1", "X", "2", None):
        raise ValueError("Result must be '1', 'X', '2', or None")

    sb.table("matches").update({
        "result": result,
    }).eq("match_id", match_id).execute()

    if result is None:
        # If result is cleared, also clear points for all bets
        bets = sb.table("bets").select("*" ).eq("match_id", match_id).execute().data
        for bet in bets:
            sb.table("bets").update({"points_earned": 0}).eq("id", bet["id"]).execute()
        return

    match    = sb.table("matches").select("*" ).eq("match_id", match_id).execute().data[0]
    bets     = sb.table("bets").select("*" ).eq("match_id", match_id).execute().data
    odds_map = {"1": match["home_odds"], "X": match["draw_odds"], "2": match["away_odds"]}

    for bet in bets:
        pts = odds_map.get(result, 0) if bet["prediction"] == result else 0
        sb.table("bets").update({"points_earned": pts}).eq("id", bet["id"]).execute()


# ── Bets ───────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=10)
def get_user_bets(username: str, group_name: str) -> dict:
    """Return {match_id: bet_row} for a user within a specific group."""
    sb = get_supabase()
    rows = sb.table("bets").select("*").eq("username", username).eq("group_name", group_name).execute().data
    return {row["match_id"]: row for row in rows}


def save_bet(username: str, group_name: str, match_id: str, prediction: str, bet_amount: int = 1):
    """Upsert a bet (one bet per user per group per match)."""
    sb = get_supabase()
    sb.table("bets").upsert({
        "username":   username,
        "group_name": group_name,
        "match_id":   match_id,
        "prediction": prediction,
        "bet_amount": bet_amount,
    }, on_conflict="username,group_name,match_id").execute()
    get_user_bets.clear()


# ── Leaderboard ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def get_leaderboard(group_name: str) -> list:
    """Return leaderboard for a specific group, sorted by points. Only includes users with valid slips."""
    sb = get_supabase()

    # Only get members with valid slips
    members   = sb.table("group_members").select("username") \
                  .eq("group_name", group_name) \
                  .eq("has_valid_slip", True) \
                  .execute().data
    usernames = [m["username"] for m in members]

    if not usernames:
        return []

    # Only bets placed within this group
    bets = sb.table("bets").select("username, points_earned") \
             .eq("group_name", group_name) \
             .in_("username", usernames) \
             .execute().data

    players = {}
    for bet in bets:
        u = bet["username"]
        if u not in players:
            players[u] = {"username": u, "total_points": 0.0, "correct_bets": 0, "total_bets": 0}
        players[u]["total_bets"] += 1
        if bet["points_earned"] is not None:
            players[u]["total_points"] += bet["points_earned"]
            if bet["points_earned"] > 0:
                players[u]["correct_bets"] += 1

    # Include valid members who haven't earned points yet
    for u in usernames:
        if u not in players:
            players[u] = {"username": u, "total_points": 0.0, "correct_bets": 0, "total_bets": 0}

    return sorted(players.values(), key=lambda x: x["total_points"], reverse=True)


# ── Budget System ──────────────────────────────────────────────────────────────

def validate_and_set_slip_status(username: str, group_name: str) -> dict:
    """
    Check if user has a valid betting slip:
    - Bet on all matches (6 matches for testing)
    - Total bet amount = 10 coins
    - Each bet between 1-10 coins
    Returns status dict with is_valid, messages, and stats.
    """
    sb = get_supabase()
    
    # Get all matches
    total_matches = len(sb.table("matches").select("match_id").execute().data)
    
    # Get user's bets
    bets = sb.table("bets").select("*").eq("username", username).eq("group_name", group_name).execute().data
    
    # Calculate stats
    total_bets = len(bets)
    total_coins = sum(bet.get("bet_amount", 1) for bet in bets)
    
    # Validation (6 matches, 10 coins total for testing)
    is_valid = (total_bets == total_matches and total_coins == 10)
    
    # Update has_valid_slip in group_members
    sb.table("group_members").update({
        "has_valid_slip": is_valid
    }).eq("username", username).eq("group_name", group_name).execute()
    
    return {
        "is_valid": is_valid,
        "total_bets": total_bets,
        "required_bets": total_matches,
        "total_coins": total_coins,
        "required_coins": 10,
    }


def get_member_slip_status(group_name: str) -> list:
    """Get all members and their slip status for a group."""
    sb = get_supabase()
    members = sb.table("group_members").select("username, has_valid_slip")\
                .eq("group_name", group_name).execute().data
    return members


# ── Knockout Picks ─────────────────────────────────────────────────────────────

def get_all_teams() -> dict:
    """Return all teams organized by group. Returns {group: [team1, team2, ...]}"""
    sb = get_supabase()
    teams = sb.table("teams").select("*").order("group_name").order("team_name").execute().data
    
    teams_by_group = {}
    for team in teams:
        group = team["group_name"]
        if group not in teams_by_group:
            teams_by_group[group] = []
        teams_by_group[group].append(team["team_name"])
    
    return teams_by_group


@st.cache_data(ttl=10)
def get_user_knockout_picks(username: str, group_name: str) -> list:
    """Return list of teams user has picked to advance to knockouts."""
    sb = get_supabase()
    picks = sb.table("knockout_picks").select("team")\
              .eq("username", username).eq("group_name", group_name).execute().data
    return [p["team"] for p in picks]


def save_knockout_picks(username: str, group_name: str, teams: list):
    """Save user's knockout picks (replaces all existing picks)."""
    sb = get_supabase()
    
    # Delete existing picks
    sb.table("knockout_picks")\
      .delete()\
      .eq("username", username)\
      .eq("group_name", group_name)\
      .execute()
    
    # Insert new picks
    if teams:
        picks_data = [{"username": username, "group_name": group_name, "team": team} for team in teams]
        sb.table("knockout_picks").insert(picks_data).execute()
    
    get_user_knockout_picks.clear()


def validate_and_set_knockout_status(username: str, group_name: str) -> dict:
    """
    Check if user has valid knockout picks (exactly 32 teams).
    Updates has_valid_knockout_picks in group_members.
    """
    sb = get_supabase()
    
    picks = get_user_knockout_picks(username, group_name)
    total_picks = len(picks)
    is_valid = (total_picks == 32)
    
    # Update has_valid_knockout_picks in group_members
    sb.table("group_members").update({
        "has_valid_knockout_picks": is_valid
    }).eq("username", username).eq("group_name", group_name).execute()
    
    return {
        "is_valid": is_valid,
        "total_picks": total_picks,
        "required_picks": 32,
    }
