import streamlit as st
from database import get_supabase

st.set_page_config(page_title="Debug Bets")

sb = get_supabase()

# Get all bets
st.title("All Bets in Database")
bets = sb.table("bets").select("*").execute().data

st.write(f"Total bets: {len(bets)}")

for bet in bets:
    st.write(bet)

# Calculate total coins per user
st.divider()
st.title("Coins per User")

user_coins = {}
for bet in bets:
    username = bet['username']
    group = bet['group_name']
    key = f"{username} ({group})"
    if key not in user_coins:
        user_coins[key] = 0
    user_coins[key] += bet.get('bet_amount', 1)

for user, coins in user_coins.items():
    st.write(f"{user}: {coins} coins")
