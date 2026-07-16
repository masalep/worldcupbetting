# database.py — all Supabase operations
import streamlit as st
from supabase import create_client


@st.cache_resource
def get_supabase():
    """Create and cache the Supabase client."""
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def _fetch_all(build_query, page_size: int = 1000) -> list:
    """
    Fetch every row from a Supabase query, paginating past PostgREST's
    1000-row default cap.

    `build_query` MUST be a zero-arg callable that returns a fresh query
    builder (e.g. lambda: sb.table("bets").select("*").eq("group_name", g))
    — because supabase-py mutates the builder when .range() is applied, so
    each page needs a new builder instance.
    """
    rows: list = []
    offset = 0
    while True:
        chunk = build_query().range(offset, offset + page_size - 1).execute().data
        if not chunk:
            break
        rows.extend(chunk)
        if len(chunk) < page_size:
            break
        offset += page_size
    return rows


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
        bets = _fetch_all(lambda: sb.table("bets").select("*").eq("match_id", match_id))
        for bet in bets:
            sb.table("bets").update({"points_earned": 0}).eq("id", bet["id"]).execute()
        return

    match    = sb.table("matches").select("*" ).eq("match_id", match_id).execute().data[0]
    bets     = _fetch_all(lambda: sb.table("bets").select("*").eq("match_id", match_id))
    odds_map = {"1": match["home_odds"], "X": match["draw_odds"], "2": match["away_odds"]}

    for bet in bets:
        if bet["prediction"] == result:
            odds = odds_map.get(result, 0) or 0
            stake = bet.get("bet_amount", 1) or 1
            # Points = odds × coins staked (e.g. 2 coins × 7.00 odds = 14 points)
            pts = odds * stake
        else:
            pts = 0
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

@st.cache_data(ttl=10)
def get_leaderboard(group_name: str) -> list:
    """Return leaderboard for a specific group, sorted by points. Only includes users with ALL picks complete."""
    sb = get_supabase()

    # Only get members with ALL validations complete
    members   = sb.table("group_members").select("username") \
                  .eq("group_name", group_name) \
                  .eq("has_valid_slip", True) \
                  .eq("has_valid_knockout_picks", True) \
                  .eq("has_valid_round16_picks", True) \
                  .eq("has_valid_quarter_picks", True) \
                  .eq("has_valid_semi_picks", True) \
                  .eq("has_valid_final_picks", True) \
                  .eq("has_valid_winner_pick", True) \
                  .eq("has_valid_golden_boot_pick", True) \
                  .execute().data
    usernames = [m["username"] for m in members]

    if not usernames:
        return []

    # Only bets placed within this group (paginated — past 1000-row PostgREST cap)
    bets = _fetch_all(lambda: sb.table("bets").select("username, points_earned")
                                  .eq("group_name", group_name)
                                  .in_("username", usernames))

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
    
    # Add knockout points to each player's total
    for u in usernames:
        knockout_points = calculate_knockout_points(u, group_name)
        players[u]["total_points"] += knockout_points["total_points"]
        players[u]["knockout_points"] = knockout_points["total_points"]  # Store separately for display

    return sorted(players.values(), key=lambda x: x["total_points"], reverse=True)


@st.cache_data(ttl=30)
def get_group_bet_analytics(group_name: str) -> list:
    """
    Read-only analytics for the group stage betting slip.
    For every user in the group with at least one bet, returns:
      - odds_total    : sum of odds matching each prediction (a "riskiness" indicator)
      - max_payout    : sum of (odds * bet_amount) — theoretical max points if every bet wins
    Sorted by max_payout descending.
    """
    sb = get_supabase()

    # One paginated read — all bets in this group (past 1000-row PostgREST cap)
    bets = _fetch_all(lambda: sb.table("bets")
                                  .select("username, match_id, prediction, bet_amount")
                                  .eq("group_name", group_name))

    if not bets:
        return []

    # One query — all matches with their odds (single dict lookup)
    matches = sb.table("matches") \
        .select("match_id, home_odds, draw_odds, away_odds") \
        .execute().data
    odds_by_match = {
        m["match_id"]: {
            "1": m.get("home_odds") or 0,
            "X": m.get("draw_odds") or 0,
            "2": m.get("away_odds") or 0,
        }
        for m in matches
    }

    # Aggregate per user
    players: dict = {}
    for bet in bets:
        user = bet["username"]
        if user not in players:
            players[user] = {
                "username": user,
                "odds_total": 0.0,
                "max_payout": 0.0,
            }

        stake = bet.get("bet_amount", 1) or 1
        pred = bet.get("prediction")
        odds = odds_by_match.get(bet["match_id"], {}).get(pred, 0) or 0

        players[user]["odds_total"] += odds
        players[user]["max_payout"] += odds * stake

    return sorted(players.values(), key=lambda x: x["max_payout"], reverse=True)


@st.cache_data(ttl=30)
def get_group_match_pick_distribution(group_name: str) -> list:
    """
    Read-only per-match pick distribution for the group.
    For every group-stage match returns:
      - match_id, matchday, kickoff, home_team, away_team
      - count_1 / count_X / count_2 — number of picks for each outcome
      - pct_1   / pct_X   / pct_2   — percentage of picks for each outcome (0-100)
      - total_picks — total number of bets placed on this match
      - result      — actual result if set ('1'/'X'/'2'), else None
    Sorted chronologically by kickoff, then match_id.
    """
    sb = get_supabase()

    # Paginated read — all bets in this group (handles >1000 rows)
    bets = _fetch_all(lambda: sb.table("bets")
                                  .select("match_id, prediction")
                                  .eq("group_name", group_name))

    # All matches (with result if available)
    matches = sb.table("matches") \
        .select("match_id, matchday, kickoff, home_team, away_team, result") \
        .execute().data

    # Count picks per (match_id, prediction)
    counts: dict = {}
    for bet in bets:
        mid = bet["match_id"]
        pred = bet.get("prediction")
        if pred not in ("1", "X", "2"):
            continue
        if mid not in counts:
            counts[mid] = {"1": 0, "X": 0, "2": 0}
        counts[mid][pred] += 1

    # Build output rows
    rows = []
    for m in matches:
        mid = m["match_id"]
        c = counts.get(mid, {"1": 0, "X": 0, "2": 0})
        total = c["1"] + c["X"] + c["2"]
        if total > 0:
            pct_1 = 100.0 * c["1"] / total
            pct_x = 100.0 * c["X"] / total
            pct_2 = 100.0 * c["2"] / total
        else:
            pct_1 = pct_x = pct_2 = 0.0

        rows.append({
            "match_id": mid,
            "matchday": m.get("matchday"),
            "kickoff": m.get("kickoff"),
            "home_team": m.get("home_team"),
            "away_team": m.get("away_team"),
            "result": m.get("result"),
            "count_1": c["1"],
            "count_X": c["X"],
            "count_2": c["2"],
            "total_picks": total,
            "pct_1": pct_1,
            "pct_X": pct_x,
            "pct_2": pct_2,
        })

    # Sort chronologically — kickoff first (None goes last), then match_id
    rows.sort(key=lambda r: (r["kickoff"] is None, r["kickoff"] or "", r["match_id"]))
    return rows


@st.cache_data(ttl=30)
def get_group_knockout_pick_distribution(group_name: str) -> list:
    """
    Read-only per-team knockout pick distribution for the group.
    For every team that has been picked by at least one player in this group,
    returns absolute counts of how many players selected the team to reach each round:
      - team       : team name
      - r32        : # of players who put this team in their Round of 32
      - r16        : # of players who advanced this team to Round of 16
      - qf         : # of players who advanced this team to Quarter Finals
      - sf         : # of players who advanced this team to Semi Finals
      - final      : # of players who advanced this team to the Final
      - winner     : # of players who picked this team to win the tournament
    Sorted by winner desc, then final desc, then sf desc, etc. (most-backed teams on top).
    """
    sb = get_supabase()

    # Each table holds (username, group_name, team) rows — one row per (player, team) pick.
    # Counting rows per team = counting players who chose that team for that round.
    r32_rows   = _fetch_all(lambda: sb.table("knockout_picks").select("team").eq("group_name", group_name))
    r16_rows   = _fetch_all(lambda: sb.table("round16_picks").select("team").eq("group_name", group_name))
    qf_rows    = _fetch_all(lambda: sb.table("quarter_picks").select("team").eq("group_name", group_name))
    sf_rows    = _fetch_all(lambda: sb.table("semi_picks").select("team").eq("group_name", group_name))
    final_rows = _fetch_all(lambda: sb.table("final_picks").select("team").eq("group_name", group_name))
    win_rows   = _fetch_all(lambda: sb.table("tournament_winner_picks").select("team").eq("group_name", group_name))

    # Aggregate counts per team per round
    teams: dict = {}
    def _bump(rows, key):
        for r in rows:
            t = r.get("team")
            if not t:
                continue
            if t not in teams:
                teams[t] = {"team": t, "r32": 0, "r16": 0, "qf": 0, "sf": 0, "final": 0, "winner": 0}
            teams[t][key] += 1

    _bump(r32_rows,   "r32")
    _bump(r16_rows,   "r16")
    _bump(qf_rows,    "qf")
    _bump(sf_rows,    "sf")
    _bump(final_rows, "final")
    _bump(win_rows,   "winner")

    # Sort: deepest predictions first (winner desc → final desc → sf desc → ... → r32 desc → team asc)
    rows = sorted(
        teams.values(),
        key=lambda r: (-r["winner"], -r["final"], -r["sf"], -r["qf"], -r["r16"], -r["r32"], r["team"]),
    )
    return rows


# ── Budget System ──────────────────────────────────────────────────────────────

def validate_and_set_slip_status(username: str, group_name: str) -> dict:
    """
    Check if user has a valid betting slip:
    - Bet on all matches (72 matches)
    - Total bet amount = 80 coins
    - Each bet between 1-2 coins
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
    
    # Validation (72 matches, 80 coins total)
    is_valid = (total_bets == total_matches and total_coins == 80)
    
    # Update has_valid_slip in group_members
    sb.table("group_members").update({
        "has_valid_slip": is_valid
    }).eq("username", username).eq("group_name", group_name).execute()
    
    # Invalidate cached slip status so UI shows fresh data after save
    get_member_slip_status.clear()
    
    return {
        "is_valid": is_valid,
        "total_bets": total_bets,
        "required_bets": total_matches,
        "total_coins": total_coins,
        "required_coins": 80,
    }


@st.cache_data(ttl=30)
def get_member_slip_status(group_name: str) -> list:
    """Get all members and their slip status for a group."""
    sb = get_supabase()
    members = sb.table("group_members").select("username, has_valid_slip, has_valid_knockout_picks")\
                .eq("group_name", group_name).execute().data
    return members


# ── Knockout Picks ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)  # teams never change during the tournament — cache for 1 hour
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
    """Save user's knockout picks (replaces all existing picks). Automatically validates."""
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
    
    # Auto-validate after saving
    validate_and_set_knockout_status(username, group_name)


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
    
    # Invalidate cached slip status so UI shows fresh data after save
    get_member_slip_status.clear()
    
    return {
        "is_valid": is_valid,
        "total_picks": total_picks,
        "required_picks": 32,
    }


# ── Round of 16 Picks ──────────────────────────────────────────────────────────

@st.cache_data(ttl=10)
def get_user_round16_picks(username: str, group_name: str) -> list:
    """Get user's Round of 16 picks."""
    sb = get_supabase()
    picks = sb.table("round16_picks").select("team")\
             .eq("username", username)\
             .eq("group_name", group_name)\
             .execute().data
    return [p["team"] for p in picks]


def save_round16_picks(username: str, group_name: str, teams: list):
    """Save user's Round of 16 picks (replaces all existing picks). Automatically validates."""
    sb = get_supabase()
    
    # Delete existing picks
    sb.table("round16_picks")\
      .delete()\
      .eq("username", username)\
      .eq("group_name", group_name)\
      .execute()
    
    # Insert new picks
    if teams:
        picks_data = [{"username": username, "group_name": group_name, "team": team} for team in teams]
        sb.table("round16_picks").insert(picks_data).execute()
    
    # Clear cache before validation so it reads fresh data
    get_user_round16_picks.clear()
    
    # Auto-validate after saving
    validate_and_set_round16_status(username, group_name)


def validate_and_set_round16_status(username: str, group_name: str) -> dict:
    """Check if user has valid Round of 16 picks (exactly 16 teams)."""
    sb = get_supabase()
    
    picks = get_user_round16_picks(username, group_name)
    total_picks = len(picks)
    is_valid = (total_picks == 16)
    
    # Update has_valid_round16_picks in group_members
    sb.table("group_members").update({
        "has_valid_round16_picks": is_valid
    }).eq("username", username).eq("group_name", group_name).execute()
    
    # Invalidate cached slip status so UI shows fresh data after save
    get_member_slip_status.clear()
    
    return {
        "is_valid": is_valid,
        "total_picks": total_picks,
        "required_picks": 16,
    }


# ── Quarter Finals Picks ───────────────────────────────────────────────────────

@st.cache_data(ttl=10)
def get_user_quarter_picks(username: str, group_name: str) -> list:
    """Get user's Quarter Finals picks."""
    sb = get_supabase()
    picks = sb.table("quarter_picks").select("team")\
             .eq("username", username)\
             .eq("group_name", group_name)\
             .execute().data
    return [p["team"] for p in picks]


def save_quarter_picks(username: str, group_name: str, teams: list):
    """Save user's Quarter Finals picks (replaces all existing picks). Automatically validates."""
    sb = get_supabase()
    
    # Delete existing picks
    sb.table("quarter_picks")\
      .delete()\
      .eq("username", username)\
      .eq("group_name", group_name)\
      .execute()
    
    # Insert new picks
    if teams:
        picks_data = [{"username": username, "group_name": group_name, "team": team} for team in teams]
        sb.table("quarter_picks").insert(picks_data).execute()
    
    # Clear cache before validation so it reads fresh data
    get_user_quarter_picks.clear()
    
    # Auto-validate after saving
    validate_and_set_quarter_status(username, group_name)


def validate_and_set_quarter_status(username: str, group_name: str) -> dict:
    """Check if user has valid Quarter Finals picks (exactly 8 teams)."""
    sb = get_supabase()
    
    picks = get_user_quarter_picks(username, group_name)
    total_picks = len(picks)
    is_valid = (total_picks == 8)
    
    # Update has_valid_quarter_picks in group_members
    sb.table("group_members").update({
        "has_valid_quarter_picks": is_valid
    }).eq("username", username).eq("group_name", group_name).execute()
    
    # Invalidate cached slip status so UI shows fresh data after save
    get_member_slip_status.clear()
    
    return {
        "is_valid": is_valid,
        "total_picks": total_picks,
        "required_picks": 8,
    }


# ── Semi Finals Picks ──────────────────────────────────────────────────────────

@st.cache_data(ttl=10)
def get_user_semi_picks(username: str, group_name: str) -> list:
    """Get user's Semi Finals picks."""
    sb = get_supabase()
    picks = sb.table("semi_picks").select("team")\
             .eq("username", username)\
             .eq("group_name", group_name)\
             .execute().data
    return [p["team"] for p in picks]


def save_semi_picks(username: str, group_name: str, teams: list):
    """Save user's Semi Finals picks (replaces all existing picks). Automatically validates."""
    sb = get_supabase()
    
    # Delete existing picks
    sb.table("semi_picks")\
      .delete()\
      .eq("username", username)\
      .eq("group_name", group_name)\
      .execute()
    
    # Insert new picks
    if teams:
        picks_data = [{"username": username, "group_name": group_name, "team": team} for team in teams]
        sb.table("semi_picks").insert(picks_data).execute()
    
    # Clear cache before validation so it reads fresh data
    get_user_semi_picks.clear()
    
    # Auto-validate after saving
    validate_and_set_semi_status(username, group_name)


def validate_and_set_semi_status(username: str, group_name: str) -> dict:
    """Check if user has valid Semi Finals picks (exactly 4 teams)."""
    sb = get_supabase()
    
    picks = get_user_semi_picks(username, group_name)
    total_picks = len(picks)
    is_valid = (total_picks == 4)
    
    # Update has_valid_semi_picks in group_members
    sb.table("group_members").update({
        "has_valid_semi_picks": is_valid
    }).eq("username", username).eq("group_name", group_name).execute()
    
    # Invalidate cached slip status so UI shows fresh data after save
    get_member_slip_status.clear()
    
    return {
        "is_valid": is_valid,
        "total_picks": total_picks,
        "required_picks": 4,
    }


# ── Final Picks ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=10)
def get_user_final_picks(username: str, group_name: str) -> dict:
    """Get user's Final picks (2 teams + winner)."""
    sb = get_supabase()
    picks = sb.table("final_picks").select("team, is_winner")\
             .eq("username", username)\
             .eq("group_name", group_name)\
             .execute().data
    
    finalists = [p["team"] for p in picks]
    winner = next((p["team"] for p in picks if p["is_winner"]), None)
    
    return {
        "finalists": finalists,
        "winner": winner
    }


def save_final_picks(username: str, group_name: str, team1: str, team2: str, winner: str):
    """Save user's Final picks (2 finalists + winner). Automatically validates."""
    sb = get_supabase()
    
    # Delete existing picks
    sb.table("final_picks")\
      .delete()\
      .eq("username", username)\
      .eq("group_name", group_name)\
      .execute()
    
    # Insert new picks
    if team1 and team2:
        picks_data = [
            {"username": username, "group_name": group_name, "team": team1, "is_winner": (team1 == winner)},
            {"username": username, "group_name": group_name, "team": team2, "is_winner": (team2 == winner)}
        ]
        sb.table("final_picks").insert(picks_data).execute()
    
    # Clear cache before validation so it reads fresh data
    get_user_final_picks.clear()
    
    # Auto-validate after saving
    validate_and_set_final_status(username, group_name)


def validate_and_set_final_status(username: str, group_name: str) -> dict:
    """Check if user has valid Final picks (2 teams)."""
    sb = get_supabase()
    
    picks = get_user_final_picks(username, group_name)
    total_finalists = len(picks["finalists"])
    is_valid = (total_finalists == 2)
    
    # Update has_valid_final_picks in group_members
    sb.table("group_members").update({
        "has_valid_final_picks": is_valid
    }).eq("username", username).eq("group_name", group_name).execute()
    
    # Invalidate cached slip status so UI shows fresh data after save
    get_member_slip_status.clear()
    
    return {
        "is_valid": is_valid,
        "total_finalists": total_finalists,
    }


# ── TOURNAMENT WINNER PICKS ────────────────────────────────────────────────────

@st.cache_data(ttl=10)
@st.cache_data(ttl=10)
def get_user_winner_pick(username: str, group_name: str) -> str:
    """Get user's tournament winner pick."""
    sb = get_supabase()
    result = sb.table("tournament_winner_picks").select("team")\
               .eq("username", username)\
               .eq("group_name", group_name)\
               .execute()
    
    return result.data[0]["team"] if result.data else None


def save_winner_pick(username: str, group_name: str, team: str):
    """Save user's tournament winner pick (single fast UPSERT + status update)."""
    sb = get_supabase()
    
    if not team:
        return
    
    # UPSERT — single round-trip instead of delete + insert (table has PK on username+group_name)
    sb.table("tournament_winner_picks").upsert({
        "username": username,
        "group_name": group_name,
        "team": team
    }, on_conflict="username,group_name").execute()
    
    # Clear cache so any reader sees fresh data
    get_user_winner_pick.clear()
    
    # Update validation flag DIRECTLY (no need to re-read — we know team is valid)
    sb.table("group_members").update({
        "has_valid_winner_pick": True
    }).eq("username", username).eq("group_name", group_name).execute()
    
    # Invalidate slip status cache (used by leaderboard / other pages)
    get_member_slip_status.clear()


def validate_and_set_winner_status(username: str, group_name: str) -> dict:
    """Check if user has valid winner pick."""
    sb = get_supabase()
    
    pick = get_user_winner_pick(username, group_name)
    is_valid = pick is not None
    
    # Update has_valid_winner_pick in group_members
    sb.table("group_members").update({
        "has_valid_winner_pick": is_valid
    }).eq("username", username).eq("group_name", group_name).execute()
    
    # Invalidate cached slip status so UI shows fresh data after save
    get_member_slip_status.clear()
    
    return {
        "is_valid": is_valid,
        "team": pick
    }


# ── GOLDEN BOOT PICKS ──────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)  # goal scorers list rarely changes — cache for 1 hour
def get_all_goal_scorers() -> list:
    """Get all goal scorers for dropdown."""
    sb = get_supabase()
    result = sb.table("goal_scorers").select("player_name, team")\
               .order("player_name")\
               .execute()
    
    return result.data


@st.cache_data(ttl=10)
def get_user_golden_boot_pick(username: str, group_name: str) -> str:
    """Get user's golden boot pick."""
    sb = get_supabase()
    result = sb.table("golden_boot_picks").select("player_name")\
               .eq("username", username)\
               .eq("group_name", group_name)\
               .execute()
    
    return result.data[0]["player_name"] if result.data else None


def save_golden_boot_pick(username: str, group_name: str, player_name: str):
    """Save user's golden boot pick (single fast UPSERT + status update)."""
    sb = get_supabase()
    
    if not player_name:
        return
    
    # UPSERT — single round-trip instead of delete + insert (table has PK on username+group_name)
    sb.table("golden_boot_picks").upsert({
        "username": username,
        "group_name": group_name,
        "player_name": player_name
    }, on_conflict="username,group_name").execute()
    
    # Clear cache so any reader sees fresh data
    get_user_golden_boot_pick.clear()
    
    # Update validation flag DIRECTLY (no need to re-read — we know pick is valid)
    sb.table("group_members").update({
        "has_valid_golden_boot_pick": True
    }).eq("username", username).eq("group_name", group_name).execute()
    
    # Invalidate slip status cache (used by leaderboard / other pages)
    get_member_slip_status.clear()


def validate_and_set_golden_boot_status(username: str, group_name: str) -> dict:
    """Check if user has valid golden boot pick."""
    sb = get_supabase()
    
    pick = get_user_golden_boot_pick(username, group_name)
    is_valid = pick is not None
    
    # Update has_valid_golden_boot_pick in group_members
    sb.table("group_members").update({
        "has_valid_golden_boot_pick": is_valid
    }).eq("username", username).eq("group_name", group_name).execute()
    
    # Invalidate cached slip status so UI shows fresh data after save
    get_member_slip_status.clear()
    
    return {
        "is_valid": is_valid,
        "player": pick
    }


# ── Knockout Results (Admin) ───────────────────────────────────────────────────

def save_knockout_result(stage: str, teams: list = None, player_name: str = None):
    """Save actual knockout results set by admin. Stage: 'round32', 'round16', 'quarter', 'semi', 'final', 'winner', 'golden_boot'"""
    sb = get_supabase()
    
    # Clear existing results for this stage
    sb.table("knockout_results").delete().eq("stage", stage).execute()
    
    # Insert new results
    if stage == "golden_boot" and player_name:
        sb.table("knockout_results").insert({
            "stage": stage,
            "team": None,
            "player_name": player_name
        }).execute()
    elif teams:
        results_data = [{"stage": stage, "team": team, "player_name": None} for team in teams]
        sb.table("knockout_results").insert(results_data).execute()


@st.cache_data(ttl=60)
def get_knockout_results(stage: str) -> list:
    """Get actual knockout results for a stage."""
    sb = get_supabase()
    
    if stage == "golden_boot":
        result = sb.table("knockout_results").select("player_name")\
                  .eq("stage", stage)\
                  .execute().data
        return result[0]["player_name"] if result else None
    else:
        results = sb.table("knockout_results").select("team")\
                   .eq("stage", stage)\
                   .execute().data
        return [r["team"] for r in results]


def calculate_knockout_points(username: str, group_name: str) -> dict:
    """Calculate points for all knockout predictions based on actual results."""
    points_breakdown = {
        "round32": {"points": 0, "correct": 0, "total": 32, "points_per": 1},
        "round16": {"points": 0, "correct": 0, "total": 16, "points_per": 2},
        "quarter": {"points": 0, "correct": 0, "total": 8, "points_per": 4},
        "semi": {"points": 0, "correct": 0, "total": 4, "points_per": 5},
        "final": {"points": 0, "correct": 0, "total": 2, "points_per": 7},
        "winner": {"points": 0, "correct": 0, "total": 1, "points_per": 10},
        "golden_boot": {"points": 0, "correct": 0, "total": 1, "points_per": 5},
    }
    
    # Round of 32
    actual_round32 = get_knockout_results("round32")
    if actual_round32:
        user_round32 = get_user_knockout_picks(username, group_name)
        correct = len(set(user_round32) & set(actual_round32))
        points_breakdown["round32"]["correct"] = correct
        points_breakdown["round32"]["points"] = correct * 1
    
    # Round of 16
    actual_round16 = get_knockout_results("round16")
    if actual_round16:
        user_round16 = get_user_round16_picks(username, group_name)
        correct = len(set(user_round16) & set(actual_round16))
        points_breakdown["round16"]["correct"] = correct
        points_breakdown["round16"]["points"] = correct * 2
    
    # Quarter Finals
    actual_quarter = get_knockout_results("quarter")
    if actual_quarter:
        user_quarter = get_user_quarter_picks(username, group_name)
        correct = len(set(user_quarter) & set(actual_quarter))
        points_breakdown["quarter"]["correct"] = correct
        points_breakdown["quarter"]["points"] = correct * 4
    
    # Semi Finals
    actual_semi = get_knockout_results("semi")
    if actual_semi:
        user_semi = get_user_semi_picks(username, group_name)
        correct = len(set(user_semi) & set(actual_semi))
        points_breakdown["semi"]["correct"] = correct
        points_breakdown["semi"]["points"] = correct * 5
    
    # Final (2 finalists) — 7 pts per correct finalist
    actual_final = get_knockout_results("final")
    if actual_final:
        user_final = get_user_final_picks(username, group_name)
        user_finalists = user_final.get("finalists", []) if isinstance(user_final, dict) else []
        correct = len(set(user_finalists) & set(actual_final))
        points_breakdown["final"]["correct"] = correct
        points_breakdown["final"]["points"] = correct * 7
    
    # Tournament Winner
    actual_winner = get_knockout_results("winner")
    if actual_winner:
        user_winner = get_user_winner_pick(username, group_name)
        if user_winner in actual_winner:
            points_breakdown["winner"]["correct"] = 1
            points_breakdown["winner"]["points"] = 10
    
    # Golden Boot
    actual_golden_boot = get_knockout_results("golden_boot")
    if actual_golden_boot:
        user_golden_boot = get_user_golden_boot_pick(username, group_name)
        if user_golden_boot == actual_golden_boot:
            points_breakdown["golden_boot"]["correct"] = 1
            points_breakdown["golden_boot"]["points"] = 5
    
    total_points = sum(stage["points"] for stage in points_breakdown.values())
    
    return {
        "total_points": total_points,
        "breakdown": points_breakdown
    }
