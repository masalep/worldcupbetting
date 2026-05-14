# app.py — World Cup 2026 Betting Pool
import streamlit as st
from database import (
    get_matches, get_user_bets,
    save_bet, get_leaderboard, set_result, lock_all_odds, unlock_all_odds,
    get_groups, create_group, verify_group, join_group, verify_member,
    get_group_members, remove_group_member,
    validate_and_set_slip_status, get_member_slip_status,
)

st.set_page_config(page_title="⚽ WC 2026 Betting", page_icon="⚽", layout="wide")


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

        login_mode = st.radio("", ["Join a group", "Admin login"], horizontal=True, label_visibility="collapsed")

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
            mode       = st.radio("", ["Returning player", "New player"], horizontal=True, label_visibility="collapsed")
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

    pages = ["⚽ Place Bets", "🏆 Leaderboard"]
    if is_admin:
        pages.append("🛠️ Admin")

    page = st.radio("", pages, label_visibility="collapsed")
    st.divider()

    if st.button("Logout", use_container_width=True):
        del st.session_state["username"]
        del st.session_state["group_name"]
        # Clear query params
        st.query_params.clear()
        st.rerun()


# ── PAGE: PLACE BETS ───────────────────────────────────────────────────────────

if page == "⚽ Place Bets" and is_admin:
    st.info("Admins cannot place bets.")
    st.stop()

if page == "⚽ Place Bets":
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
    remaining_coins = 10 - total_coins_used
    
    # Show budget tracker at top
    st.markdown("### 💰 Budget Tracker")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Coins Used", f"{total_coins_used}/10", 
                  delta=f"{remaining_coins} remaining" if remaining_coins > 0 else "Complete!")
    with col2:
        st.metric("Matches Bet", f"{total_bets_placed}/{total_matches}")
    with col3:
        if total_bets_placed == total_matches and total_coins_used == 10:
            st.success("✅ Valid Slip!")
        else:
            st.warning("⏳ Incomplete")
    
    # Show warning if over budget
    if total_coins_used > 10:
        st.error(f"🚨 **BUDGET EXCEEDED!** You've used {total_coins_used} coins but only have 10. You must reduce your bets to create a valid slip.")
    
    st.divider()
    st.caption("Pick 1 (home win), X (draw) or 2 (away win) for each match. Set bet amount (1-10 coins). **Save all bets** when done.")

    match_groups: dict[str, list] = {}
    for m in matches:
        match_groups.setdefault(m["group_name"], []).append(m)

    football_group = st.selectbox(
        "Select group",
        sorted(match_groups.keys()),
        format_func=lambda x: f"Group {x}",
        key="selected_football_group",
    )
    
    # Calculate LIVE preview of coins being used (from session state)
    live_coins_preview = 0
    for match in matches:
        mid = match["match_id"]
        # Check if there's an amount in session state (user is editing)
        if f"amount_{mid}" in st.session_state:
            live_coins_preview += st.session_state[f"amount_{mid}"]
        # Otherwise use saved amount
        elif mid in user_bets:
            live_coins_preview += user_bets[mid].get("bet_amount", 1)
    
    # Always show live preview
    preview_remaining = 10 - live_coins_preview
    if live_coins_preview > 10:
        st.warning(f"💡 **Live Preview**: You're using **{live_coins_preview} coins** ({live_coins_preview - 10} over budget)")
    elif live_coins_preview < 10:
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
            head_col, odds_col = st.columns([3, 2])
            with head_col:
                st.markdown(f"**{mid} · {home} vs {away}**")
            with odds_col:
                if home_odds:
                    st.caption(f"1: {home_odds:.2f} · X: {draw_odds:.2f} · 2: {away_odds:.2f}")
                else:
                    st.caption("Odds not set yet")

            if result:
                result_text = {"1": "Home win", "X": "Draw", "2": "Away win"}.get(result, result)
                if current_bet:
                    pts = bet_row.get("points_earned") or 0
                    if current_bet == result:
                        st.success(f"✅ Your bet: **{current_bet}** · Result: **{result}** ({result_text}) · **+{pts:.2f} pts**")
                    else:
                        st.error(f"❌ Your bet: **{current_bet}** · Result: **{result}** ({result_text}) · **0 pts**")
                else:
                    st.warning(f"No bet placed · Result: **{result}** ({result_text})")

            elif locked:
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
                with amount_col:
                    st.number_input(
                        "Coins",
                        min_value=1,
                        max_value=10,
                        value=current_bet_amount,
                        key=f"amount_{mid}",
                        help="Bet 1-10 coins on this match"
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
                    if status['total_coins'] != 10:
                        issues.append(f"only {status['total_coins']}/10 coins used")
                    elif status['total_coins'] > 10:
                        issues.append(f"{status['total_coins']}/10 coins used (over budget!)")
                    st.warning(f"⏳ Incomplete slip: {' · '.join(issues)}")
                
                st.rerun()


# ── PAGE: LEADERBOARD ─────────────────────────────────────────────────────────

elif page == "🏆 Leaderboard" and is_admin:
    st.info("Admins cannot view leaderboards. Log in as a regular user to see group standings.")
    st.stop()

elif page == "🏆 Leaderboard":
    st.title(f"🏆 Leaderboard — {group_name}")
    st.caption("💡 Only players with valid betting slips (all matches bet with exact coin budget) appear on the leaderboard.")

    board = get_leaderboard(group_name)
    if not board:
        st.info("No players with valid betting slips yet! Complete your slip to compete.")
        st.stop()

    medals = ["🥇", "🥈", "🥉"]

    for i, player in enumerate(board, 1):
        rank  = medals[i - 1] if i <= 3 else f"**{i}.**"
        col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
        with col1:
            st.markdown(rank)
        with col2:
            st.markdown(f"**{player['username']}**")
        with col3:
            st.markdown(f"**{player['total_points']:.2f} pts**")
        with col4:
            st.caption(f"{player['correct_bets']}/{player['total_bets']} correct")
        if i <= 3:
            st.divider()


# ── PAGE: ADMIN ────────────────────────────────────────────────────────────────

elif page == "🛠️ Admin" and is_admin:
    st.title("🛠️ Admin Panel")

    tab_groups, tab_odds, tab_results = st.tabs(["👥 Groups", "📊 Odds", "⚽ Results"])

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

