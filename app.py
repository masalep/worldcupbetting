# app.py — World Cup 2026 Betting Pool
import streamlit as st
from database import (
    get_matches, get_user_bets,
    save_bet, get_leaderboard, set_result, lock_all_odds, unlock_all_odds,
    get_group_bet_analytics, get_group_match_pick_distribution,
    get_groups, create_group, verify_group, join_group, verify_member,
    get_group_members, remove_group_member,
    validate_and_set_slip_status, get_member_slip_status,
    get_all_teams, get_user_knockout_picks, save_knockout_picks, validate_and_set_knockout_status,
    get_user_round16_picks, save_round16_picks, validate_and_set_round16_status,
    get_user_quarter_picks, save_quarter_picks, validate_and_set_quarter_status,
    get_user_semi_picks, save_semi_picks, validate_and_set_semi_status,
    get_user_final_picks, save_final_picks, validate_and_set_final_status,
    get_user_winner_pick, save_winner_pick, validate_and_set_winner_status,
    get_all_goal_scorers, get_user_golden_boot_pick, save_golden_boot_pick, validate_and_set_golden_boot_status,
    save_knockout_result, get_knockout_results, calculate_knockout_points,
)


st.set_page_config(page_title="⚽ WC 2026 Betting", page_icon="⚽", layout="wide")


# ── HELPERS ────────────────────────────────────────────────────────────────────

def is_betting_locked() -> bool:
    """
    True once the admin has clicked 🔒 Lock ALL Betting in the admin panel.
    Used to freeze BOTH group-stage AND all knockout/winner/golden-boot edits
    so nobody can change picks after the tournament has started.
    """
    matches = get_matches()
    return any(m.get("betting_locked", False) for m in matches)


def render_locked_banner():
    """Standard red banner shown on every knockout page when betting is locked."""
    st.error(
        "🔒 **Picks are locked.** The tournament has started — your selections "
        "below are read-only and cannot be changed anymore."
    )


# ── LOGIN ──────────────────────────────────────────────────────────────────────

# Check if user is already logged in via session storage
if "username" not in st.session_state:
    # Try to restore from browser's sessionStorage via query params
    if hasattr(st, 'query_params'):
        query_user = st.query_params.get("u")
        query_group = st.query_params.get("g")
        if query_user:
            st.session_state["username"] = query_user
            st.session_state["group_name"] = query_group or ""

if "username" not in st.session_state:
    st.title("⚽ World Cup 2026 Betting Pool")
    st.divider()

    col, _ = st.columns([1, 2])
    with col:
        groups      = get_groups()
        group_names = [g["name"] for g in groups]

        login_mode = st.radio("Login type", ["Join a group", "Admin login"], horizontal=True, label_visibility="collapsed")

        if login_mode == "Admin login":
            admin_name = st.text_input("Admin username")
            admin_pass = st.text_input("Admin password", type="password")
            if st.button("Login →", type="primary", use_container_width=True):
                if (admin_name.lower() == st.secrets.get("ADMIN_USERNAME", "admin").lower()
                        and admin_pass == st.secrets.get("ADMIN_PASSWORD", "")):
                    st.session_state["username"]   = admin_name
                    st.session_state["group_name"] = ""
                    # Set query params for persistence
                    st.query_params["u"] = admin_name
                    st.query_params["g"] = ""
                    st.rerun()
                else:
                    st.error("Wrong admin credentials!")

        else:
            if not group_names:
                st.info("No groups exist yet — ask the admin to create one.")
                st.stop()

            group      = st.selectbox("Select your group", group_names)
            grp_pass   = st.text_input("Group password", type="password")
            mode       = st.radio("Player mode", ["Returning player", "New player"], horizontal=True, label_visibility="collapsed")
            username   = st.text_input("Your name")
            user_pass  = st.text_input("Your personal password", type="password")

            if mode == "Returning player":
                if st.button("Login →", type="primary", use_container_width=True):
                    if not verify_group(group, grp_pass):
                        st.error("Wrong group password!")
                    elif not username.strip():
                        st.error("Enter your name!")
                    elif not verify_member(group, username.strip(), user_pass):
                        st.error("Wrong personal password, or name not registered yet.")
                    else:
                        st.session_state["username"]   = username.strip()
                        st.session_state["group_name"] = group
                        # Set query params for persistence
                        st.query_params["u"] = username.strip()
                        st.query_params["g"] = group
                        st.rerun()

            else:  # New player
                if st.button("Register & Join →", type="primary", use_container_width=True):
                    if not verify_group(group, grp_pass):
                        st.error("Wrong group password!")
                    elif not username.strip():
                        st.error("Enter your name!")
                    elif not user_pass:
                        st.error("Choose a personal password!")
                    else:
                        members = get_group_members(group)
                        if username.strip() in members:
                            st.error(f"**{username.strip()}** is already registered — choose 'Returning player'.")
                        else:
                            try:
                                join_group(group, username.strip(), user_pass)
                                get_group_members.clear()
                                st.session_state["username"]   = username.strip()
                                st.session_state["group_name"] = group
                                # Set query params for persistence
                                st.query_params["u"] = username.strip()
                                st.query_params["g"] = group
                                st.rerun()
                            except Exception:
                                st.error(f"**{username.strip()}** was just taken by someone else — try a different name.")
    st.stop()


# ── SIDEBAR ────────────────────────────────────────────────────────────────────

username   = st.session_state["username"]
group_name = st.session_state.get("group_name", "")
is_admin   = username.lower() == st.secrets.get("ADMIN_USERNAME", "admin").lower()

with st.sidebar:
    st.title("⚽ WC 2026")
    st.write(f"👤 **{username}**")
    st.caption(f"Group: {group_name}")
    st.divider()

    pages = ["Place Bets", "Leaderboard", "Group Statistics"]
    if is_admin:
        pages.append("Admin")
    else:
        # Only regular users can make knockout picks
        pages.insert(1, "Round of 32")
        pages.insert(2, "Round of 16")
        pages.insert(3, "Quarter Finals")
        pages.insert(4, "Semi Finals")
        pages.insert(5, "Final")
        pages.insert(6, "Winner & Golden Boot")

    page = st.radio("Page navigation", pages, label_visibility="collapsed")
    st.divider()

    if st.button("Logout", use_container_width=True):
        del st.session_state["username"]
        del st.session_state["group_name"]
        # Clear query params
        st.query_params.clear()
        st.rerun()


# ── PAGE: PLACE BETS ───────────────────────────────────────────────────────────

if page == "Place Bets" and is_admin:
    st.info("Admins cannot place bets.")
    st.stop()

if page == "Place Bets":
    st.title("⚽ Place Your Bets")
    
    matches = get_matches()
    if not matches:
        st.info("No matches loaded yet — ask the admin to initialise matches.")
        st.stop()

    # Clear cache to get fresh bet data
    get_user_bets.clear()
    user_bets = get_user_bets(username, group_name)
    
    # Calculate budget statistics
    total_matches = len(matches)
    total_bets_placed = len(user_bets)
    total_coins_used = sum(bet.get("bet_amount", 1) for bet in user_bets.values())
    remaining_coins = 80 - total_coins_used
    
    # Show budget tracker at top
    st.markdown("### 💰 Budget Tracker")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Coins Used", f"{total_coins_used}/80", 
                  delta=f"{remaining_coins} remaining" if remaining_coins > 0 else "Complete!")
    with col2:
        st.metric("Matches Bet", f"{total_bets_placed}/{total_matches}")
    with col3:
        if total_bets_placed == total_matches and total_coins_used == 80:
            st.success("✅ Valid Slip!")
        else:
            st.warning("⏳ Incomplete")
    
    # Show warning if over budget
    if total_coins_used > 80:
        st.error(f"🚨 **BUDGET EXCEEDED!** You've used {total_coins_used} coins but only have 80. You must reduce your bets to create a valid slip.")
    
    st.divider()
    st.caption("Pick 1 (home win), X (draw) or 2 (away win) for each match. Set bet amount (1-2 coins). **Save all bets** when done.")

    match_groups: dict[str, list] = {}
    for m in matches:
        match_groups.setdefault(m["group_name"], []).append(m)

    football_group = st.selectbox(
        "Select group",
        sorted(match_groups.keys()),
        format_func=lambda x: f"Group {x}",
        key="selected_football_group",
    )
    
    # Calculate LIVE preview
    # Start with all saved bets from DB, then add/update with current edits on THIS page
    live_coins_preview = 0
    
    # First: Add all saved bets from database
    for mid, bet in user_bets.items():
        live_coins_preview += bet.get("bet_amount", 1)
    
    # Second: Override with current edits on visible matches in this group
    for match in match_groups[football_group]:
        mid = match["match_id"]
        saved_amount = user_bets.get(mid, {}).get("bet_amount", 0)  # 0 if not saved yet
        current_amount = st.session_state.get(f"amount_{mid}")
        
        if current_amount is not None:
            # User edited this match - replace saved amount with current
            live_coins_preview = live_coins_preview - saved_amount + current_amount
    
    # Always show live preview
    preview_remaining = 80 - live_coins_preview
    if live_coins_preview > 80:
        st.warning(f"💡 **Live Preview**: You're using **{live_coins_preview} coins** ({live_coins_preview - 80} over budget)")
    elif live_coins_preview < 80:
        st.info(f"💡 **Live Preview**: You're using **{live_coins_preview} coins** ({preview_remaining} remaining)")
    else:
        st.success(f"💡 **Live Preview**: Perfect! **{live_coins_preview} coins** ✓")
    
    open_matches = []

    for match in match_groups[football_group]:
        mid         = match["match_id"]
        home        = match["home_team"]
        away        = match["away_team"]
        locked      = match.get("betting_locked", False)
        result      = match.get("result")
        home_odds   = match.get("home_odds")
        draw_odds   = match.get("draw_odds")
        away_odds   = match.get("away_odds")
        bet_row     = user_bets.get(mid, {})
        current_bet = bet_row.get("prediction")

        with st.container(border=True):
            # Match header — full width (odds are shown under the 1/X/2 options below)
            st.markdown(f"**{mid} · {home} vs {away}**")

            if result:
                result_text = {"1": "Home win", "X": "Draw", "2": "Away win"}.get(result, result)
                if home_odds:
                    st.caption(f"📊 Odds — 1: {home_odds:.2f} · X: {draw_odds:.2f} · 2: {away_odds:.2f}")
                if current_bet:
                    pts = bet_row.get("points_earned") or 0
                    if current_bet == result:
                        st.success(f"✅ Your bet: **{current_bet}** · Result: **{result}** ({result_text}) · **+{pts:.2f} pts**")
                    else:
                        st.error(f"❌ Your bet: **{current_bet}** · Result: **{result}** ({result_text}) · **0 pts**")
                else:
                    st.warning(f"No bet placed · Result: **{result}** ({result_text})")

            elif locked:
                if home_odds:
                    st.caption(f"📊 Odds — 1: {home_odds:.2f} · X: {draw_odds:.2f} · 2: {away_odds:.2f}")
                if current_bet:
                    st.info(f"🔒 Locked bet: **{current_bet}**")
                else:
                    st.warning("🔒 Betting closed — no bet placed")

            else:
                options = ["1", "X", "2"]
                labels  = [f"1 — {home} win", "X — Draw", f"2 — {away} win"]
                current_index = options.index(current_bet) if current_bet in options else None
                current_bet_amount = bet_row.get("bet_amount", 1)

                bet_col, amount_col = st.columns([3, 1])
                with bet_col:
                    st.radio(
                        label=mid,
                        options=options,
                        format_func=lambda x, l=labels, o=options: l[o.index(x)],
                        index=current_index,
                        horizontal=True,
                        label_visibility="collapsed",
                        key=f"bet_{mid}",
                    )
                    # Odds row — aligned in 3 columns directly under the 1 / X / 2 options
                    if home_odds:
                        oc1, oc2, oc3 = st.columns(3)
                        with oc1:
                            st.markdown(
                                f"<div style='text-align:center; margin-top:-4px;'>"
                                f"<strong>📊 {home_odds:.2f}</strong></div>",
                                unsafe_allow_html=True,
                            )
                        with oc2:
                            st.markdown(
                                f"<div style='text-align:center; margin-top:-4px;'>"
                                f"<strong>📊 {draw_odds:.2f}</strong></div>",
                                unsafe_allow_html=True,
                            )
                        with oc3:
                            st.markdown(
                                f"<div style='text-align:center; margin-top:-4px;'>"
                                f"<strong>📊 {away_odds:.2f}</strong></div>",
                                unsafe_allow_html=True,
                            )
                    else:
                        st.caption("⚠️ Odds not set yet")
                with amount_col:
                    st.number_input(
                        "Coins",
                        min_value=1,
                        max_value=2,
                        value=current_bet_amount,
                        key=f"amount_{mid}",
                        help="Bet 1-2 coins on this match"
                    )
                open_matches.append(mid)

    if open_matches:
        st.divider()
        
        # Check if any match in this group is locked (betting closed)
        any_locked = any(m.get("betting_locked", False) for m in match_groups[football_group] if not m.get("result"))
        
        if any_locked:
            st.error("🔒 **Betting is locked!** The tournament has started and you can no longer place or change bets.")
        else:
            if st.button(f"💾 Save bets for Group {football_group}", type="primary", key=f"save_{football_group}"):
                # Just save all bets - validation happens after
                saved = 0
                for mid in open_matches:
                    choice = st.session_state.get(f"bet_{mid}")
                    bet_amount = st.session_state.get(f"amount_{mid}", 1)
                    if choice:
                        save_bet(username, group_name, mid, choice, bet_amount)
                        saved += 1
                
                # Clear session state for this group's matches to start fresh
                for mid in open_matches:
                    if f"bet_{mid}" in st.session_state:
                        del st.session_state[f"bet_{mid}"]
                    if f"amount_{mid}" in st.session_state:
                        del st.session_state[f"amount_{mid}"]
                
                # Validate and update slip status
                status = validate_and_set_slip_status(username, group_name)
                
                get_user_bets.clear()
                st.toast(f"✅ Saved {saved} bets for Group {football_group}!", icon="✅")
                
                # Show validation status
                if status["is_valid"]:
                    st.success(f"✅ **Valid slip!** You've bet {status['total_coins']} coins on all {status['total_bets']} matches!")
                else:
                    issues = []
                    if status['total_bets'] < status['required_bets']:
                        issues.append(f"only {status['total_bets']}/{status['required_bets']} matches bet")
                    if status['total_coins'] != 80:
                        issues.append(f"only {status['total_coins']}/80 coins used")
                    elif status['total_coins'] > 80:
                        issues.append(f"{status['total_coins']}/80 coins used (over budget!)")
                    st.warning(f"⏳ Incomplete slip: {' · '.join(issues)}")
                
                st.rerun()


# ── PAGE: ROUND OF 32 ────────────────────────────────────────────────────────

elif page == "Round of 32":
    st.title("Round of 32")
    st.caption("Select exactly 32 teams that you think will advance to the Round of 32 (knockout stage)")
    
    locked = is_betting_locked()
    if locked:
        render_locked_banner()
    
    # Custom CSS for green selected buttons
    st.markdown("""
        <style>
        /* Make primary buttons green for this page */
        div[data-testid="stVerticalBlock"] button[kind="primary"] {
            background-color: #10b981 !important;
            border-color: #10b981 !important;
        }
        div[data-testid="stVerticalBlock"] button[kind="primary"]:hover {
            background-color: #059669 !important;
            border-color: #059669 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    teams_by_group = get_all_teams()
    
    if not teams_by_group:
        st.error("No teams found in database")
        st.stop()
    
    # Get user's current selections
    user_picks = get_user_knockout_picks(username, group_name)
    
    # Initialize session state for selections if not exists
    if "knockout_selections" not in st.session_state:
        st.session_state["knockout_selections"] = set(user_picks)
    
    # Callback for toggling a team selection — fires BEFORE rerun,
    # so the button renders with the new color in a single rerun (no double rerun).
    def _toggle_knockout_team(team_name: str):
        selections = st.session_state["knockout_selections"]
        if team_name in selections:
            selections.discard(team_name)
        else:
            selections.add(team_name)
    
    # Count current selections
    selected_count = len(st.session_state["knockout_selections"])
    
    # Show counter at top
    st.markdown("### Selection Status")
    col1, col2, col3 = st.columns(3)
    with col1:
        if selected_count == 32:
            st.success(f"**{selected_count}/32 teams selected**")
        elif selected_count < 32:
            st.info(f"**{selected_count}/32 teams selected**")
        else:
            st.error(f"**{selected_count}/32 teams selected** (too many!)")
    
    with col2:
        remaining = 32 - selected_count
        if remaining > 0:
            st.metric("Still need", remaining)
        elif remaining == 0:
            st.metric("Ready!", "✓")
        else:
            st.metric("Over by", abs(remaining))
    
    with col3:
        # Show validity status
        all_members = get_member_slip_status(group_name)
        member_status = next((m for m in all_members if m["username"] == username), None)
        
        if member_status and member_status.get("has_valid_knockout_picks"):
            st.success("✓ Valid & Saved")
        elif user_picks:  # reuse already-fetched picks instead of a second DB call
            st.info(f"Draft: {len(user_picks)} saved")
        else:
            st.warning("Not saved yet")
    
    st.divider()
    
    # Display teams by group with toggle buttons - 3 groups per row
    all_groups = sorted(teams_by_group.keys())
    
    # Process groups in chunks of 3
    for i in range(0, len(all_groups), 3):
        group_chunk = all_groups[i:i+3]
        cols = st.columns(len(group_chunk))
        
        for col_idx, group in enumerate(group_chunk):
            with cols[col_idx]:
                st.markdown(f"#### Group {group}")
                teams = teams_by_group[group]
                
                # Display teams vertically in this column
                for team in teams:
                    is_selected = team in st.session_state["knockout_selections"]
                    
                    # Toggle button - green for selected, gray for unselected
                    button_type = "primary" if is_selected else "secondary"
                    
                    # on_click callback updates state BEFORE the rerun → only 1 rerun per click
                    st.button(
                        team,
                        key=f"team_{group}_{team}",
                        type=button_type,
                        use_container_width=True,
                        on_click=None if locked else _toggle_knockout_team,
                        args=(team,),
                        disabled=locked,
                    )
        
        st.divider()
    
    # Save button — disabled when betting is locked
    st.markdown("### Save Your Picks")
    
    if locked:
        st.info(f"🔒 Your final picks: **{selected_count}/32 teams** selected.")
    elif selected_count < 32:
        st.info(f"💡 You can save incomplete picks and return later. Selected: {selected_count}/32")
    elif selected_count == 32:
        st.success(f"✅ Perfect! You have selected exactly 32 teams. Save to complete your picks!")
    else:
        st.error(f"❌ Too many teams selected! You have {selected_count} but need exactly 32.")
    
    col_save, col_clear = st.columns([3, 1])
    
    with col_save:
        if st.button("💾 Save Knockout Picks", type="primary", use_container_width=True, disabled=locked):
            # Save all selections (even if incomplete)
            save_knockout_picks(username, group_name, list(st.session_state["knockout_selections"]))
            
            # Validate and update status (will only mark valid if exactly 32)
            status = validate_and_set_knockout_status(username, group_name)
            
            if status["is_valid"]:
                st.success(f"✅ Saved {status['total_picks']} teams! Your knockout picks are now VALID and locked in!")
                st.rerun()
            else:
                st.warning(f"💾 Saved {status['total_picks']} teams as draft. Complete 32 teams to validate your picks.")
                st.rerun()
    
    with col_clear:
        if st.button("Clear All", use_container_width=True, disabled=locked):
            st.session_state["knockout_selections"] = set()
            st.rerun()


# ── PAGE: ROUND OF 16 ─────────────────────────────────────────────────────────

elif page == "Round of 16":
    st.title("Round of 16")
    st.caption("Select exactly 16 teams that you think will advance to the Round of 16 (knockout stage)")
    
    locked = is_betting_locked()
    if locked:
        render_locked_banner()
    
    # Custom CSS for green selected buttons
    st.markdown("""
        <style>
        /* Make primary buttons green for this page */
        div[data-testid="stVerticalBlock"] button[kind="primary"] {
            background-color: #10b981 !important;
            border-color: #10b981 !important;
        }
        div[data-testid="stVerticalBlock"] button[kind="primary"]:hover {
            background-color: #059669 !important;
            border-color: #059669 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    teams_by_group = get_all_teams()
    
    if not teams_by_group:
        st.error("No teams found in database")
        st.stop()
    
    # Get user's current selections
    user_picks = get_user_round16_picks(username, group_name)
    
    # Initialize session state for selections if not exists
    if "round16_selections" not in st.session_state:
        st.session_state["round16_selections"] = set(user_picks)
    
    # Count current selections
    selected_count = len(st.session_state["round16_selections"])
    
    # Show counter at top
    st.markdown("### Selection Status")
    col1, col2, col3 = st.columns(3)
    with col1:
        if selected_count == 16:
            st.success(f"**{selected_count}/16 teams selected**")
        elif selected_count < 16:
            st.info(f"**{selected_count}/16 teams selected**")
        else:
            st.error(f"**{selected_count}/16 teams selected** (too many!)")
    
    with col2:
        remaining = 16 - selected_count
        if remaining > 0:
            st.metric("Still need", remaining)
        elif remaining == 0:
            st.metric("Ready!", "✓")
        else:
            st.metric("Over by", abs(remaining))
    
    with col3:
        # Show validity status
        all_members = get_member_slip_status(group_name)
        member_status = next((m for m in all_members if m["username"] == username), None)
        
        if member_status and member_status.get("has_valid_round16_picks"):
            st.success("✓ Valid & Saved")
        elif user_picks:  # reuse already-fetched picks instead of a second DB call
            st.info(f"Draft: {len(user_picks)} saved")
        else:
            st.warning("Not saved yet")
    
    st.divider()
    
    # Display teams by group with toggle buttons - 3 groups per row
    all_groups = sorted(teams_by_group.keys())
    
    # Process groups in chunks of 3
    for i in range(0, len(all_groups), 3):
        group_chunk = all_groups[i:i+3]
        cols = st.columns(len(group_chunk))
        
        for col_idx, group in enumerate(group_chunk):
            with cols[col_idx]:
                st.markdown(f"#### Group {group}")
                teams = teams_by_group[group]
                
                # Display teams vertically in this column
                for team in teams:
                    is_selected = team in st.session_state["round16_selections"]
                    
                    # Toggle button - green for selected, gray for unselected
                    button_type = "primary" if is_selected else "secondary"
                    
                    # on_click callback updates state BEFORE rerun → only 1 rerun per click
                    st.button(
                        team,
                        key=f"r16_team_{group}_{team}",
                        type=button_type,
                        use_container_width=True,
                        on_click=None if locked else (lambda t=team: (
                            st.session_state["round16_selections"].discard(t)
                            if t in st.session_state["round16_selections"]
                            else st.session_state["round16_selections"].add(t)
                        )),
                        disabled=locked,
                    )
        
        st.divider()
    
    # Save button — disabled when betting is locked
    st.markdown("### Save Your Picks")
    
    if locked:
        st.info(f"🔒 Your final picks: **{selected_count}/16 teams** selected.")
    elif selected_count < 16:
        st.info(f"💡 You can save incomplete picks and return later. Selected: {selected_count}/16")
    elif selected_count == 16:
        st.success(f"✅ Perfect! You have selected exactly 16 teams. Save to complete your picks!")
    else:
        st.error(f"❌ Too many teams selected! You have {selected_count} but need exactly 16.")
    
    col_save, col_clear = st.columns([3, 1])
    
    with col_save:
        if st.button("💾 Save Round of 16 Picks", type="primary", use_container_width=True, disabled=locked):
            # Save all selections (even if incomplete)
            save_round16_picks(username, group_name, list(st.session_state["round16_selections"]))
            
            # Validate and update status (will only mark valid if exactly 16)
            status = validate_and_set_round16_status(username, group_name)
            
            if status["is_valid"]:
                st.success(f"✅ Saved {status['total_picks']} teams! Your Round of 16 picks are now VALID and locked in!")
                st.rerun()
            else:
                st.warning(f"💾 Saved {status['total_picks']} teams as draft. Complete 16 teams to validate your picks.")
                st.rerun()
    
    with col_clear:
        if st.button("Clear All", use_container_width=True, disabled=locked):
            st.session_state["round16_selections"] = set()
            st.rerun()


# ── PAGE: QUARTER FINALS ──────────────────────────────────────────────────────

elif page == "Quarter Finals":
    st.title("Quarter Finals")
    st.caption("Select exactly 8 teams that you think will advance to the Quarter Finals (knockout stage)")
    
    locked = is_betting_locked()
    if locked:
        render_locked_banner()
    
    # Custom CSS for green selected buttons
    st.markdown("""
        <style>
        /* Make primary buttons green for this page */
        div[data-testid="stVerticalBlock"] button[kind="primary"] {
            background-color: #10b981 !important;
            border-color: #10b981 !important;
        }
        div[data-testid="stVerticalBlock"] button[kind="primary"]:hover {
            background-color: #059669 !important;
            border-color: #059669 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    teams_by_group = get_all_teams()
    
    if not teams_by_group:
        st.error("No teams found in database")
        st.stop()
    
    # Get user's current selections
    user_picks = get_user_quarter_picks(username, group_name)
    
    # Initialize session state for selections if not exists
    if "quarter_selections" not in st.session_state:
        st.session_state["quarter_selections"] = set(user_picks)
    
    # Count current selections
    selected_count = len(st.session_state["quarter_selections"])
    
    # Show counter at top
    st.markdown("### Selection Status")
    col1, col2, col3 = st.columns(3)
    with col1:
        if selected_count == 8:
            st.success(f"**{selected_count}/8 teams selected**")
        elif selected_count < 8:
            st.info(f"**{selected_count}/8 teams selected**")
        else:
            st.error(f"**{selected_count}/8 teams selected** (too many!)")
    
    with col2:
        remaining = 8 - selected_count
        if remaining > 0:
            st.metric("Still need", remaining)
        elif remaining == 0:
            st.metric("Ready!", "✓")
        else:
            st.metric("Over by", abs(remaining))
    
    with col3:
        # Show validity status
        all_members = get_member_slip_status(group_name)
        member_status = next((m for m in all_members if m["username"] == username), None)
        
        if member_status and member_status.get("has_valid_quarter_picks"):
            st.success("✓ Valid & Saved")
        elif user_picks:  # reuse already-fetched picks instead of a second DB call
            st.info(f"Draft: {len(user_picks)} saved")
        else:
            st.warning("Not saved yet")
    
    st.divider()
    
    # Display teams by group with toggle buttons - 3 groups per row
    all_groups = sorted(teams_by_group.keys())
    
    # Process groups in chunks of 3
    for i in range(0, len(all_groups), 3):
        group_chunk = all_groups[i:i+3]
        cols = st.columns(len(group_chunk))
        
        for col_idx, group in enumerate(group_chunk):
            with cols[col_idx]:
                st.markdown(f"#### Group {group}")
                teams = teams_by_group[group]
                
                # Display teams vertically in this column
                for team in teams:
                    is_selected = team in st.session_state["quarter_selections"]
                    
                    # Toggle button - green for selected, gray for unselected
                    button_type = "primary" if is_selected else "secondary"
                    
                    # on_click callback updates state BEFORE rerun → only 1 rerun per click
                    st.button(
                        team,
                        key=f"qf_team_{group}_{team}",
                        type=button_type,
                        use_container_width=True,
                        on_click=None if locked else (lambda t=team: (
                            st.session_state["quarter_selections"].discard(t)
                            if t in st.session_state["quarter_selections"]
                            else st.session_state["quarter_selections"].add(t)
                        )),
                        disabled=locked,
                    )
        
        st.divider()
    
    # Save button — disabled when betting is locked
    st.markdown("### Save Your Picks")
    
    if locked:
        st.info(f"🔒 Your final picks: **{selected_count}/8 teams** selected.")
    elif selected_count < 8:
        st.info(f"💡 You can save incomplete picks and return later. Selected: {selected_count}/8")
    elif selected_count == 8:
        st.success(f"✅ Perfect! You have selected exactly 8 teams. Save to complete your picks!")
    else:
        st.error(f"❌ Too many teams selected! You have {selected_count} but need exactly 8.")
    
    col_save, col_clear = st.columns([3, 1])
    
    with col_save:
        if st.button("💾 Save Quarter Finals Picks", type="primary", use_container_width=True, disabled=locked):
            # Save all selections (even if incomplete)
            save_quarter_picks(username, group_name, list(st.session_state["quarter_selections"]))
            
            # Validate and update status (will only mark valid if exactly 8)
            status = validate_and_set_quarter_status(username, group_name)
            
            if status["is_valid"]:
                st.success(f"✅ Saved {status['total_picks']} teams! Your Quarter Finals picks are now VALID and locked in!")
                st.rerun()
            else:
                st.warning(f"💾 Saved {status['total_picks']} teams as draft. Complete 8 teams to validate your picks.")
                st.rerun()
    
    with col_clear:
        if st.button("Clear All", use_container_width=True, disabled=locked):
            st.session_state["quarter_selections"] = set()
            st.rerun()


# ── PAGE: SEMI FINALS ────────────────────────────────────────────────────────

elif page == "Semi Finals":
    st.title("Semi Finals")
    st.caption("Select exactly 4 teams that you think will advance to the Semi Finals")
    
    locked = is_betting_locked()
    if locked:
        render_locked_banner()
    
    # Custom CSS for green selected buttons
    st.markdown("""
        <style>
        /* Make primary buttons green for this page */
        div[data-testid="stVerticalBlock"] button[kind="primary"] {
            background-color: #10b981 !important;
            border-color: #10b981 !important;
        }
        div[data-testid="stVerticalBlock"] button[kind="primary"]:hover {
            background-color: #059669 !important;
            border-color: #059669 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    teams_by_group = get_all_teams()
    
    if not teams_by_group:
        st.error("No teams found in database")
        st.stop()
    
    # Get user's current selections
    user_picks = get_user_semi_picks(username, group_name)
    
    # Initialize session state for selections if not exists
    if "semi_selections" not in st.session_state:
        st.session_state["semi_selections"] = set(user_picks)
    
    # Count current selections
    selected_count = len(st.session_state["semi_selections"])
    
    # Show counter at top
    st.markdown("### Selection Status")
    col1, col2, col3 = st.columns(3)
    with col1:
        if selected_count == 4:
            st.success(f"**{selected_count}/4 teams selected**")
        elif selected_count < 4:
            st.info(f"**{selected_count}/4 teams selected**")
        else:
            st.error(f"**{selected_count}/4 teams selected** (too many!)")
    
    with col2:
        remaining = 4 - selected_count
        if remaining > 0:
            st.metric("Still need", remaining)
        elif remaining == 0:
            st.metric("Ready!", "✓")
        else:
            st.metric("Over by", abs(remaining))
    
    with col3:
        # Show validity status
        all_members = get_member_slip_status(group_name)
        member_status = next((m for m in all_members if m["username"] == username), None)
        
        if member_status and member_status.get("has_valid_semi_picks"):
            st.success("✓ Valid & Saved")
        elif user_picks:  # reuse already-fetched picks instead of a second DB call
            st.info(f"Draft: {len(user_picks)} saved")
        else:
            st.warning("Not saved yet")
    
    st.divider()
    
    # Display teams by group with toggle buttons - 3 groups per row
    all_groups = sorted(teams_by_group.keys())
    
    # Process groups in chunks of 3
    for i in range(0, len(all_groups), 3):
        group_chunk = all_groups[i:i+3]
        cols = st.columns(len(group_chunk))
        
        for col_idx, group in enumerate(group_chunk):
            with cols[col_idx]:
                st.markdown(f"#### Group {group}")
                teams = teams_by_group[group]
                
                # Display teams vertically in this column
                for team in teams:
                    is_selected = team in st.session_state["semi_selections"]
                    
                    # Toggle button - green for selected, gray for unselected
                    button_type = "primary" if is_selected else "secondary"
                    
                    # on_click callback updates state BEFORE rerun → only 1 rerun per click
                    st.button(
                        team,
                        key=f"semi_team_{group}_{team}",
                        type=button_type,
                        use_container_width=True,
                        on_click=None if locked else (lambda t=team: (
                            st.session_state["semi_selections"].discard(t)
                            if t in st.session_state["semi_selections"]
                            else st.session_state["semi_selections"].add(t)
                        )),
                        disabled=locked,
                    )
        
        st.divider()
    
    # Save button — disabled when betting is locked
    st.markdown("### Save Your Picks")
    
    if locked:
        st.info(f"🔒 Your final picks: **{selected_count}/4 teams** selected.")
    elif selected_count < 4:
        st.info(f"💡 You can save incomplete picks and return later. Selected: {selected_count}/4")
    elif selected_count == 4:
        st.success(f"✅ Perfect! You have selected exactly 4 teams. Save to complete your picks!")
    else:
        st.error(f"❌ Too many teams selected! You have {selected_count} but need exactly 4.")
    
    col_save, col_clear = st.columns([3, 1])
    
    with col_save:
        if st.button("💾 Save Semi Finals Picks", type="primary", use_container_width=True, disabled=locked):
            # Save all selections (even if incomplete)
            save_semi_picks(username, group_name, list(st.session_state["semi_selections"]))
            
            # Validate and update status (will only mark valid if exactly 4)
            status = validate_and_set_semi_status(username, group_name)
            
            if status["is_valid"]:
                st.success(f"✅ Saved {status['total_picks']} teams! Your Semi Finals picks are now VALID and locked in!")
                st.rerun()
            else:
                st.warning(f"💾 Saved {status['total_picks']} teams as draft. Complete 4 teams to validate your picks.")
                st.rerun()
    
    with col_clear:
        if st.button("Clear All", use_container_width=True, disabled=locked):
            st.session_state["semi_selections"] = set()
            st.rerun()


# ── PAGE: FINAL ───────────────────────────────────────────────────────────────

elif page == "Final":
    st.title("Final")
    st.caption("Select exactly 2 teams that you think will advance to the Final")
    
    locked = is_betting_locked()
    if locked:
        render_locked_banner()
    
    # Custom CSS for green selected buttons
    st.markdown("""
        <style>
        /* Make primary buttons green for this page */
        div[data-testid="stVerticalBlock"] button[kind="primary"] {
            background-color: #10b981 !important;
            border-color: #10b981 !important;
        }
        div[data-testid="stVerticalBlock"] button[kind="primary"]:hover {
            background-color: #059669 !important;
            border-color: #059669 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    teams_by_group = get_all_teams()
    
    if not teams_by_group:
        st.error("No teams found in database")
        st.stop()
    
    # Get user's current selections
    user_final_picks = get_user_final_picks(username, group_name)
    
    # Initialize session state for selections if not exists
    if "final_selections" not in st.session_state:
        # Get finalists from the dictionary
        finalists = user_final_picks.get("finalists", [])
        st.session_state["final_selections"] = set(finalists)
    
    # Count current selections
    selected_count = len(st.session_state["final_selections"])
    
    # Show counter at top
    st.markdown("### Selection Status")
    col1, col2, col3 = st.columns(3)
    with col1:
        if selected_count == 2:
            st.success(f"**{selected_count}/2 teams selected**")
        elif selected_count < 2:
            st.info(f"**{selected_count}/2 teams selected**")
        else:
            st.error(f"**{selected_count}/2 teams selected** (too many!)")
    
    with col2:
        remaining = 2 - selected_count
        if remaining > 0:
            st.metric("Still need", remaining)
        elif remaining == 0:
            st.metric("Ready!", "✓")
        else:
            st.metric("Over by", abs(remaining))
    
    with col3:
        # Show validity status
        all_members = get_member_slip_status(group_name)
        member_status = next((m for m in all_members if m["username"] == username), None)
        
        current_saved_picks = get_user_final_picks(username, group_name)
        finalists_saved = current_saved_picks.get("finalists", [])
        
        if member_status and member_status.get("has_valid_final_picks"):
            st.success("✓ Valid & Saved")
        elif finalists_saved:
            st.info(f"Draft: {len(finalists_saved)} saved")
        else:
            st.warning("Not saved yet")
    
    st.divider()
    
    # Display teams by group with toggle buttons - 3 groups per row
    all_groups = sorted(teams_by_group.keys())
    
    # Process groups in chunks of 3
    for i in range(0, len(all_groups), 3):
        group_chunk = all_groups[i:i+3]
        cols = st.columns(len(group_chunk))
        
        for col_idx, group in enumerate(group_chunk):
            with cols[col_idx]:
                st.markdown(f"#### Group {group}")
                teams = teams_by_group[group]
                
                # Display teams vertically in this column
                for team in teams:
                    is_selected = team in st.session_state["final_selections"]
                    
                    # Toggle button - green for selected, gray for unselected
                    button_type = "primary" if is_selected else "secondary"
                    
                    if st.button(
                        team,
                        key=f"final_team_{group}_{team}",
                        type=button_type,
                        use_container_width=True,
                        disabled=locked,
                    ):
                        # Toggle selection
                        if is_selected:
                            st.session_state["final_selections"].discard(team)
                        else:
                            st.session_state["final_selections"].add(team)
                        st.rerun()
        
        st.divider()
    
    # Save button — disabled when betting is locked
    st.markdown("### Save Your Picks")
    
    if locked:
        st.info(f"🔒 Your final picks: **{selected_count}/2 teams** selected.")
    elif selected_count < 2:
        st.info(f"💡 You can save incomplete picks and return later. Selected: {selected_count}/2")
    elif selected_count == 2:
        st.success(f"✅ Perfect! You have selected exactly 2 teams. Save to complete your picks!")
    else:
        st.error(f"❌ Too many teams selected! You have {selected_count} but need exactly 2.")
    
    col_save, col_clear = st.columns([3, 1])
    
    with col_save:
        if st.button("💾 Save Final Picks", type="primary", use_container_width=True, disabled=locked):
            # Save final picks (2 finalists, no winner)
            finalists_list = list(st.session_state["final_selections"])
            
            # Need exactly 2 finalists to save
            if len(finalists_list) >= 2:
                save_final_picks(username, group_name, finalists_list[0], finalists_list[1], "")
            elif len(finalists_list) == 1:
                # Save with empty second finalist
                save_final_picks(username, group_name, finalists_list[0], "", "")
            else:
                # Nothing to save
                save_final_picks(username, group_name, "", "", "")
            
            # Validate
            final_status = validate_and_set_final_status(username, group_name)
            
            if final_status["is_valid"]:
                st.success(f"✅ Saved {final_status['total_finalists']} teams! Your Final picks are now VALID and locked in!")
                st.rerun()
            else:
                st.warning(f"💾 Saved {final_status['total_finalists']} teams as draft. Complete 2 teams to validate your picks.")
                st.rerun()
    
    with col_clear:
        if st.button("Clear All", use_container_width=True, disabled=locked):
            st.session_state["final_selections"] = set()
            st.rerun()


# ── PAGE: WINNER & GOLDEN BOOT ────────────────────────────────────────────────

elif page == "Winner & Golden Boot":
    st.title("Winner & Golden Boot")
    st.caption("Select the tournament winner and the golden boot winner (top scorer)")
    
    locked = is_betting_locked()
    if locked:
        render_locked_banner()
    
    st.divider()
    
    # Load picks from DB into session_state on first visit / user switch.
    # After that, we treat session_state as the source of truth for the "Current Pick"
    # display. On save, we update session_state immediately so the UI reflects the
    # change without needing to wait for a DB roundtrip.
    state_owner = f"{group_name}::{username}"  # detect if user switched accounts
    if st.session_state.get("_picks_owner") != state_owner:
        st.session_state["current_winner"] = get_user_winner_pick(username, group_name)
        st.session_state["current_golden_boot"] = get_user_golden_boot_pick(username, group_name)
        st.session_state["_picks_owner"] = state_owner
    
    current_winner = st.session_state["current_winner"]
    current_golden_boot = st.session_state["current_golden_boot"]
    
    # Get all teams and players (both cached for 1h — basically free)
    teams_by_group = get_all_teams()
    all_teams = []
    for teams in teams_by_group.values():
        all_teams.extend(teams)
    all_teams = sorted(all_teams)
    
    goal_scorers = get_all_goal_scorers()
    players_list = [f"{p['player_name']} ({p['team']})" for p in goal_scorers]
    
    # ── SECTION 1: Tournament Winner ──
    st.markdown("## 🏆 Tournament Winner")
    st.caption("Select which team will win the World Cup 2026")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Find current index
        winner_index = 0
        if current_winner and current_winner in all_teams:
            winner_index = all_teams.index(current_winner)
        
        selected_winner = st.selectbox(
            "Choose the tournament winner:",
            options=all_teams,
            index=winner_index if current_winner else 0,
            key="winner_dropdown",
            disabled=locked,
        )
    
    with col2:
        st.markdown("### Current Pick")
        if current_winner:
            st.success(f"✅ {current_winner}")
        else:
            st.warning("Not selected")
    
    # Save button for winner — disabled when betting is locked
    if st.button("💾 Save Tournament Winner", type="primary", use_container_width=True, disabled=locked):
        # Update session_state FIRST so the next rerun shows the new value instantly
        st.session_state["current_winner"] = selected_winner
        save_winner_pick(username, group_name, selected_winner)
        st.toast(f"✅ Tournament winner saved: {selected_winner}", icon="✅")
        # Force a rerun so the "Current Pick" badge re-renders with the new value
        # (Streamlit only auto-reruns ONCE per click, with old state still in scope above)
        st.rerun()
    
    st.divider()
    
    # ── SECTION 2: Golden Boot Winner ──
    st.markdown("## ⚽ Golden Boot Winner")
    st.caption("Select which player will score the most goals")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Find current index
        boot_index = 0
        if current_golden_boot:
            # Find matching player in list
            for i, player_str in enumerate(players_list):
                if player_str.startswith(current_golden_boot):
                    boot_index = i
                    break
        
        selected_player_full = st.selectbox(
            "Choose the golden boot winner:",
            options=players_list,
            index=boot_index if current_golden_boot else 0,
            key="golden_boot_dropdown",
            disabled=locked,
        )
        
        # Extract player name (without team in parentheses)
        selected_player = selected_player_full.split(" (")[0] if selected_player_full else ""
    
    with col2:
        st.markdown("### Current Pick")
        if current_golden_boot:
            st.success(f"✅ {current_golden_boot}")
        else:
            st.warning("Not selected")
    
    # Save button for golden boot — disabled when betting is locked
    if st.button("💾 Save Golden Boot Pick", type="primary", use_container_width=True, disabled=locked):
        # Update session_state FIRST so the next rerun shows the new value instantly
        st.session_state["current_golden_boot"] = selected_player
        save_golden_boot_pick(username, group_name, selected_player)
        st.toast(f"✅ Golden boot saved: {selected_player}", icon="✅")
        # Force a rerun so the "Current Pick" badge re-renders with the new value
        # (Streamlit only auto-reruns ONCE per click, with old state still in scope above)
        st.rerun()
    
    st.divider()
    
    # Completion status — uses session_state, no DB calls
    st.markdown("### Completion Status")
    col1, col2 = st.columns(2)
    
    with col1:
        if current_winner:
            st.success("✅ Tournament Winner: Complete")
        else:
            st.warning("⚠️ Tournament Winner: Not selected")
    
    with col2:
        if current_golden_boot:
            st.success("✅ Golden Boot: Complete")
        else:
            st.warning("⚠️ Golden Boot: Not selected")


# ── PAGE: LEADERBOARD ─────────────────────────────────────────────────────────

elif page == "Leaderboard" and is_admin:
    st.info("Admins cannot view leaderboards. Log in as a regular user to see group standings.")
    st.stop()

elif page == "Leaderboard":
    st.title(f"🏆 Leaderboard — {group_name}")
    st.caption("💡 Only players who have completed ALL picks appear on the leaderboard: Betting Slip + All Knockout Stages + Tournament Winner + Golden Boot")

    board = get_leaderboard(group_name)
    if not board:
        st.info("No players with complete picks yet! To appear on the leaderboard, you need to complete:")
        st.markdown("""
        - ✅ Valid betting slip (80 coins budget)
        - ✅ Round of 32 picks (32 teams)
        - ✅ Round of 16 picks (16 teams)
        - ✅ Quarter Finals picks (8 teams)
        - ✅ Semi Finals picks (4 teams)
        - ✅ Final picks (2 teams)
        - ✅ Tournament Winner pick
        - ✅ Golden Boot pick
        """)
    else:
        medals = ["🥇", "🥈", "🥉"]

        for i, player in enumerate(board, 1):
            rank  = medals[i - 1] if i <= 3 else f"**{i}.**"
            col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
            with col1:
                st.markdown(rank)
            with col2:
                st.markdown(f"**{player['username']}**")
            with col3:
                match_pts = player['total_points'] - player.get('knockout_points', 0)
                knockout_pts = player.get('knockout_points', 0)
                st.markdown(f"**{player['total_points']:.1f} pts**")
                st.caption(f"Match: {match_pts:.1f} | Knockout: {knockout_pts:.1f}")
            with col4:
                st.caption(f"{player['correct_bets']}/{player['total_bets']} correct")
            if i <= 3:
                st.divider()


# ── PAGE: GROUP STATISTICS ────────────────────────────────────────────────────

elif page == "Group Statistics" and is_admin:
    st.info("Admins cannot view group statistics. Log in as a regular user to see this page.")
    st.stop()

elif page == "Group Statistics":
    st.title(f"📊 Group Statistics — {group_name}")
    st.caption("Analytics across all players in your group.")

    # ── Betting Analytics ─────────────────────────────────────────────────
    st.subheader("Betting Slip Analytics")
    st.caption(
        "Per-user breakdown of the **group stage betting slip**. "
        "Includes everyone in the group who has placed at least one bet "
        "— even if their slip isn't fully valid yet."
    )

    analytics = get_group_bet_analytics(group_name)
    if not analytics:
        st.info("No bets placed in this group yet.")
    else:
        import pandas as pd
        df = pd.DataFrame(analytics)
        df.index = range(1, len(df) + 1)  # 1-based rank by max_payout
        
        # 🐔 Chicken award — bottom 3 by Odds Total get publicly shamed.
        # Lowest odds total = pelkurit (stacking favourites): 3 chickens.
        # 2nd lowest = 2 chickens. 3rd lowest = 1 chicken.
        #
        # 🚀🔥🎲 Gambler award — top 3 by Odds Total get glory emojis.
        # Highest = 🚀 (to the moon). 2nd = 🔥 (on fire). 3rd = 🎲 (dice).
        #
        # Only applied if at least 3 players exist (otherwise meaningless).
        if len(df) >= 3:
            # Ascending rank: 1 = lowest odds (most cowardly)
            chicken_ranking = df["odds_total"].rank(method="min", ascending=True)
            chicken_emojis = chicken_ranking.map({1: " 🐔🐔🐔", 2: " 🐔🐔", 3: " 🐔"}).fillna("")
            
            # Descending rank: 1 = highest odds (biggest gambler)
            gambler_ranking = df["odds_total"].rank(method="min", ascending=False)
            gambler_emojis = gambler_ranking.map({1: " 🚀", 2: " 🔥", 3: " 🎲"}).fillna("")
            
            df["username"] = df["username"] + gambler_emojis + chicken_emojis
        
        df = df.rename(columns={
            "username":    "Player",
            "odds_total":  "Odds Total",
            "max_payout":  "Max Payout",
        })
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Player":     st.column_config.TextColumn("Player", width="medium", help="� highest odds · 🔥 2nd · 🎲 3rd  |  🐔 lowest odds · 🐔🐔 2nd lowest · 🐔🐔🐔 lowest"),
                "Odds Total": st.column_config.NumberColumn("Odds Total", format="%.2f", help="Sum of all odds the user backed (higher = riskier / more upsets predicted)"),
                "Max Payout": st.column_config.NumberColumn("Max Payout", format="%.1f pts", help="Theoretical maximum points if every group stage bet wins (= sum of odds × coins)"),
            },
        )

    # ── Match Pick Distribution ───────────────────────────────────────────
    st.divider()
    st.subheader("Match Pick Distribution")
    st.caption(
        "How your group is voting on each group-stage match. "
        "Percentages are share of picks for **1** (home win), **X** (draw), or **2** (away win)."
    )

    distribution = get_group_match_pick_distribution(group_name)
    if not distribution:
        st.info("No bets placed in this group yet.")
    else:
        import pandas as pd
        df_d = pd.DataFrame(distribution)

        # Build a friendly match label
        df_d["Match"] = df_d["home_team"] + "  vs  " + df_d["away_team"]

        # Result column — plain "1" / "X" / "2", blank until admin sets it
        df_d["Result"] = df_d["result"].fillna("")

        # Keep only the columns we want to display, in display order
        df_view = df_d[[
            "matchday", "Match", "pct_1", "pct_X", "pct_2", "total_picks", "Result"
        ]].rename(columns={
            "matchday":    "MD",
            "pct_1":       "1 (home)",
            "pct_X":       "X (draw)",
            "pct_2":       "2 (away)",
            "total_picks": "Picks",
        })
        df_view.index = range(1, len(df_view) + 1)

        st.dataframe(
            df_view,
            use_container_width=True,
            height=min(35 * (len(df_view) + 1) + 3, 600),
            column_config={
                "MD":       st.column_config.NumberColumn("MD", format="%d", help="Matchday", width="small"),
                "Match":    st.column_config.TextColumn("Match", width="medium"),
                "1 (home)": st.column_config.ProgressColumn(
                    "1 (home)", format="%.0f%%", min_value=0, max_value=100,
                    help="% of group betting on home win",
                ),
                "X (draw)": st.column_config.ProgressColumn(
                    "X (draw)", format="%.0f%%", min_value=0, max_value=100,
                    help="% of group betting on draw",
                ),
                "2 (away)": st.column_config.ProgressColumn(
                    "2 (away)", format="%.0f%%", min_value=0, max_value=100,
                    help="% of group betting on away win",
                ),
                "Picks":    st.column_config.NumberColumn("Picks", format="%d", help="Total bets placed on this match", width="small"),
                "Result":   st.column_config.TextColumn("Result", width="small", help="Actual result once set"),
            },
        )


# ── PAGE: ADMIN ────────────────────────────────────────────────────────────────

elif page == "Admin" and is_admin:
    st.title("🛠️ Admin Panel")

    tab_groups, tab_odds, tab_results, tab_knockout = st.tabs(["👥 Groups", "📊 Odds", "⚽ Match Results", "🏆 Knockout Results"])

    with tab_groups:
        st.subheader("Create a new group")
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            new_group_name = st.text_input("Group name", placeholder="e.g. Work Colleagues")
        with g_col2:
            new_group_pass = st.text_input("Group password", placeholder="e.g. sauna2026")
        if st.button("Create group", type="primary"):
            if new_group_name and new_group_pass:
                try:
                    create_group(new_group_name, new_group_pass)
                    st.success(f"✅ Group **{new_group_name}** created!")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Fill in both fields.")

        st.divider()
        st.subheader("Groups & players")
        groups = get_groups()
        if not groups:
            st.info("No groups yet.")
        else:
            selected_group = st.selectbox(
                "Select group to manage",
                [g["name"] for g in groups],
                key="admin_group_select",
            )
            grp = next(g for g in groups if g["name"] == selected_group)
            st.caption(f"Password: `{grp['password']}`")

            members = get_group_members(selected_group)
            if not members:
                st.info("No players in this group yet.")
            else:
                st.markdown(f"**{len(members)} player(s):**")
                for member in members:
                    col_name, col_btn = st.columns([4, 1])
                    with col_name:
                        st.write(f"👤 {member}")
                    with col_btn:
                        if st.button("Remove", key=f"remove_{selected_group}_{member}"):
                            remove_group_member(selected_group, member)
                            st.toast(f"Removed {member} from {selected_group}")
                            st.rerun()

    with tab_odds:
        st.subheader(" Lock/Unlock Betting")
        st.warning("⚠️ **Lock betting when tournament starts. Users cannot place or change bets when locked!**")
        
        col_lock, col_unlock = st.columns(2)
        with col_lock:
            if st.button("🔒 Lock ALL Betting", type="primary", key="lock_betting"):
                lock_all_odds()
                get_matches.clear()
                st.success("✅ All betting is now LOCKED!")
        
        with col_unlock:
            if st.button("🔓 Unlock ALL Betting", key="unlock_betting"):
                unlock_all_odds()
                get_matches.clear()
                st.success("✅ All betting is now UNLOCKED!")
        
        st.divider()
        st.info("💡 **Tip:** Set odds manually in your database, then lock betting when the tournament starts.")

    with tab_results:
        st.subheader("Enter match results")
        st.caption("Click on any cell in the **Result** column to edit. Choose **1** (home win), **X** (draw), or **2** (away win).")
        
        import pandas as pd
        from datetime import datetime
        
        matches = get_matches()
        
        # Create editable dataframe
        df = pd.DataFrame([
            {
                "Match ID": m["match_id"],
                "Group": m.get("group_name", ""),
                "Date": datetime.fromisoformat(m["kickoff"].replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M") if m.get("kickoff") else "—",
                "Home": m["home_team"],
                "Away": m["away_team"],
                "Result": m.get("result", ""),
            }
            for m in matches
        ])
        
        # Show editable table
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            disabled=["Match ID", "Group", "Date", "Home", "Away"],  # Only Result is editable
            column_config={
                "Result": st.column_config.SelectboxColumn(
                    "Result",
                    help="Select 1 (home win), X (draw), or 2 (away win)",
                    options=["", "1", "X", "2"],
                    required=False,
                ),
            },
            key="results_editor"
        )
        
        # Save button
        if st.button("💾 Save all changes", type="primary", key="save_results"):
            changes_made = 0
            for idx, row in edited_df.iterrows():
                original_result = df.loc[idx, "Result"]
                new_result = row["Result"]
                
                # Handle empty/NaN values
                if pd.isna(new_result) or new_result == "":
                    new_result = ""
                if pd.isna(original_result) or original_result == "":
                    original_result = ""
                
                # Only update if result changed
                if new_result != original_result:
                    match_id = row["Match ID"]
                    # If empty string, clear the result (set to None)
                    if new_result == "":
                        set_result(match_id, None)
                    elif new_result in ["1", "X", "2"]:
                        set_result(match_id, new_result)
                    else:
                        continue  # Skip invalid values
                    changes_made += 1
            
            if changes_made > 0:
                get_matches.clear()
                get_leaderboard.clear()
                get_user_bets.clear()
                st.success(f"✅ Updated {changes_made} match result(s)!")
                st.rerun()
            else:
                st.info("No changes detected.")
    
    with tab_knockout:
        st.subheader("🏆 Set Knockout Stage Results")
        st.caption("Mark which teams actually advanced in each knockout stage. This determines which users' predictions were correct.")
        
        knockout_stage = st.selectbox(
            "Select knockout stage:",
            ["Round of 32", "Round of 16", "Quarter Finals", "Semi Finals", "Tournament Winner", "Golden Boot"]
        )
        
        st.divider()
        
        # Get all teams for selection
        teams_by_group = get_all_teams()
        all_teams = []
        for teams in teams_by_group.values():
            all_teams.extend(teams)
        all_teams = sorted(all_teams)
        
        if knockout_stage == "Round of 32":
            st.markdown("### Round of 32 - Select teams that advanced")
            st.caption("⚠️ Eventually select 32 teams. You can save progressively as teams qualify. Users get **1 point** per correct team.")
            
            # Get current results
            stage_key = "round32"
            current_teams = get_knockout_results(stage_key) or []
            
            # Initialize session state
            if f"admin_{stage_key}" not in st.session_state:
                st.session_state[f"admin_{stage_key}"] = set(current_teams)
            
            selected_count = len(st.session_state[f"admin_{stage_key}"])
            if selected_count == 32:
                st.success(f"✅ Selected: {selected_count}/32 teams — complete!")
            elif selected_count > 32:
                st.error(f"⚠️ Selected: {selected_count}/32 teams — too many!")
            else:
                st.info(f"📊 Selected: {selected_count}/32 teams (saving partial results is OK)")
            
            # Team selection in 4 columns
            cols = st.columns(4)
            for idx, team in enumerate(all_teams):
                with cols[idx % 4]:
                    is_selected = team in st.session_state[f"admin_{stage_key}"]
                    if st.button(
                        team,
                        key=f"admin_{stage_key}_{team}",
                        type="primary" if is_selected else "secondary",
                        use_container_width=True
                    ):
                        if is_selected:
                            st.session_state[f"admin_{stage_key}"].remove(team)
                        else:
                            st.session_state[f"admin_{stage_key}"].add(team)
                        st.rerun()
            
            st.divider()
            col_save, col_clear = st.columns([3, 1])
            with col_save:
                save_label = "💾 Save Round of 32 Results" if selected_count == 32 else f"💾 Save partial results ({selected_count} teams)"
                if st.button(save_label, type="primary", use_container_width=True, disabled=(selected_count > 32)):
                    save_knockout_result(stage_key, list(st.session_state[f"admin_{stage_key}"]))
                    get_knockout_results.clear()
                    if selected_count == 32:
                        st.success("✅ Round of 32 complete! All points recalculated.")
                    else:
                        st.success(f"✅ Saved {selected_count} teams. Points recalculated — you can add more later.")
                    st.rerun()
            with col_clear:
                if st.button("Clear", use_container_width=True):
                    st.session_state[f"admin_{stage_key}"] = set()
                    st.rerun()
            
        elif knockout_stage == "Round of 16":
            st.markdown("### Round of 16 - Select teams that advanced")
            st.caption("⚠️ Eventually select 16 teams. You can save progressively as teams qualify. Users get **2 points** per correct team.")
            
            stage_key = "round16"
            current_teams = get_knockout_results(stage_key) or []
            
            if f"admin_{stage_key}" not in st.session_state:
                st.session_state[f"admin_{stage_key}"] = set(current_teams)
            
            selected_count = len(st.session_state[f"admin_{stage_key}"])
            if selected_count == 16:
                st.success(f"✅ Selected: {selected_count}/16 teams — complete!")
            elif selected_count > 16:
                st.error(f"⚠️ Selected: {selected_count}/16 teams — too many!")
            else:
                st.info(f"📊 Selected: {selected_count}/16 teams (saving partial results is OK)")
            
            cols = st.columns(4)
            for idx, team in enumerate(all_teams):
                with cols[idx % 4]:
                    is_selected = team in st.session_state[f"admin_{stage_key}"]
                    if st.button(
                        team,
                        key=f"admin_{stage_key}_{team}",
                        type="primary" if is_selected else "secondary",
                        use_container_width=True
                    ):
                        if is_selected:
                            st.session_state[f"admin_{stage_key}"].remove(team)
                        else:
                            st.session_state[f"admin_{stage_key}"].add(team)
                        st.rerun()
            
            st.divider()
            col_save, col_clear = st.columns([3, 1])
            with col_save:
                save_label = "💾 Save Round of 16 Results" if selected_count == 16 else f"💾 Save partial results ({selected_count} teams)"
                if st.button(save_label, type="primary", use_container_width=True, disabled=(selected_count > 16)):
                    save_knockout_result(stage_key, list(st.session_state[f"admin_{stage_key}"]))
                    get_knockout_results.clear()
                    if selected_count == 16:
                        st.success("✅ Round of 16 complete! All points recalculated.")
                    else:
                        st.success(f"✅ Saved {selected_count} teams. Points recalculated — you can add more later.")
                    st.rerun()
            with col_clear:
                if st.button("Clear", use_container_width=True):
                    st.session_state[f"admin_{stage_key}"] = set()
                    st.rerun()
            
        elif knockout_stage == "Quarter Finals":
            st.markdown("### Quarter Finals - Select teams that advanced")
            st.caption("⚠️ Eventually select 8 teams. You can save progressively as teams qualify. Users get **4 points** per correct team.")
            
            stage_key = "quarter"
            current_teams = get_knockout_results(stage_key) or []
            
            if f"admin_{stage_key}" not in st.session_state:
                st.session_state[f"admin_{stage_key}"] = set(current_teams)
            
            selected_count = len(st.session_state[f"admin_{stage_key}"])
            if selected_count == 8:
                st.success(f"✅ Selected: {selected_count}/8 teams — complete!")
            elif selected_count > 8:
                st.error(f"⚠️ Selected: {selected_count}/8 teams — too many!")
            else:
                st.info(f"📊 Selected: {selected_count}/8 teams (saving partial results is OK)")
            
            cols = st.columns(4)
            for idx, team in enumerate(all_teams):
                with cols[idx % 4]:
                    is_selected = team in st.session_state[f"admin_{stage_key}"]
                    if st.button(
                        team,
                        key=f"admin_{stage_key}_{team}",
                        type="primary" if is_selected else "secondary",
                        use_container_width=True
                    ):
                        if is_selected:
                            st.session_state[f"admin_{stage_key}"].remove(team)
                        else:
                            st.session_state[f"admin_{stage_key}"].add(team)
                        st.rerun()
            
            st.divider()
            col_save, col_clear = st.columns([3, 1])
            with col_save:
                save_label = "💾 Save Quarter Finals Results" if selected_count == 8 else f"💾 Save partial results ({selected_count} teams)"
                if st.button(save_label, type="primary", use_container_width=True, disabled=(selected_count > 8)):
                    save_knockout_result(stage_key, list(st.session_state[f"admin_{stage_key}"]))
                    get_knockout_results.clear()
                    if selected_count == 8:
                        st.success("✅ Quarter Finals complete! All points recalculated.")
                    else:
                        st.success(f"✅ Saved {selected_count} teams. Points recalculated — you can add more later.")
                    st.rerun()
            with col_clear:
                if st.button("Clear", use_container_width=True):
                    st.session_state[f"admin_{stage_key}"] = set()
                    st.rerun()
            
        elif knockout_stage == "Semi Finals":
            st.markdown("### Semi Finals - Select teams that advanced")
            st.caption("⚠️ Eventually select 4 teams. You can save progressively as teams qualify. Users get **5 points** per correct team.")
            
            stage_key = "semi"
            current_teams = get_knockout_results(stage_key) or []
            
            if f"admin_{stage_key}" not in st.session_state:
                st.session_state[f"admin_{stage_key}"] = set(current_teams)
            
            selected_count = len(st.session_state[f"admin_{stage_key}"])
            if selected_count == 4:
                st.success(f"✅ Selected: {selected_count}/4 teams — complete!")
            elif selected_count > 4:
                st.error(f"⚠️ Selected: {selected_count}/4 teams — too many!")
            else:
                st.info(f"📊 Selected: {selected_count}/4 teams (saving partial results is OK)")
            
            cols = st.columns(4)
            for idx, team in enumerate(all_teams):
                with cols[idx % 4]:
                    is_selected = team in st.session_state[f"admin_{stage_key}"]
                    if st.button(
                        team,
                        key=f"admin_{stage_key}_{team}",
                        type="primary" if is_selected else "secondary",
                        use_container_width=True
                    ):
                        if is_selected:
                            st.session_state[f"admin_{stage_key}"].remove(team)
                        else:
                            st.session_state[f"admin_{stage_key}"].add(team)
                        st.rerun()
            
            st.divider()
            col_save, col_clear = st.columns([3, 1])
            with col_save:
                save_label = "💾 Save Semi Finals Results" if selected_count == 4 else f"💾 Save partial results ({selected_count} teams)"
                if st.button(save_label, type="primary", use_container_width=True, disabled=(selected_count > 4)):
                    save_knockout_result(stage_key, list(st.session_state[f"admin_{stage_key}"]))
                    get_knockout_results.clear()
                    if selected_count == 4:
                        st.success("✅ Semi Finals complete! All points recalculated.")
                    else:
                        st.success(f"✅ Saved {selected_count} teams. Points recalculated — you can add more later.")
                    st.rerun()
            with col_clear:
                if st.button("Clear", use_container_width=True):
                    st.session_state[f"admin_{stage_key}"] = set()
                    st.rerun()
            
        elif knockout_stage == "Tournament Winner":
            st.markdown("### Tournament Winner")
            st.caption("Select the team that won the World Cup 2026. Winner gets **10 points**.")
            
            stage_key = "winner"
            current_winner = get_knockout_results(stage_key)
            winner_team = current_winner[0] if current_winner else ""
            
            selected_winner = st.selectbox(
                "Select tournament winner:", 
                [""] + all_teams,
                index=(all_teams.index(winner_team) + 1) if winner_team in all_teams else 0
            )
            
            if st.button("💾 Save Tournament Winner", type="primary"):
                if selected_winner:
                    save_knockout_result(stage_key, [selected_winner])
                    get_knockout_results.clear()
                    st.success(f"✅ Tournament winner set to: {selected_winner}")
                    st.rerun()
                else:
                    st.warning("Please select a team")
                    
        elif knockout_stage == "Golden Boot":
            st.markdown("### Golden Boot Winner")
            st.caption("Select the player who won the Golden Boot (top scorer). Winner gets **5 points**.")
            
            stage_key = "golden_boot"
            current_boot = get_knockout_results(stage_key)
            
            goal_scorers = get_all_goal_scorers()
            players_list = [""] + [f"{p['player_name']} ({p['team']})" for p in goal_scorers]
            
            # Find current index
            boot_index = 0
            if current_boot:
                for i, player_str in enumerate(players_list):
                    if player_str.startswith(current_boot):
                        boot_index = i
                        break
            
            golden_boot_player = st.selectbox(
                "Select golden boot winner:", 
                players_list,
                index=boot_index
            )
            
            if st.button("💾 Save Golden Boot Winner", type="primary"):
                if golden_boot_player and golden_boot_player != "":
                    player_name = golden_boot_player.split(" (")[0]
                    save_knockout_result(stage_key, player_name=player_name)
                    get_knockout_results.clear()
                    st.success(f"✅ Golden Boot winner set to: {player_name}")
                    st.rerun()
                else:
                    st.warning("Please select a player")


