import json

with open('matches.json', 'r') as f:
    data = json.load(f)

teams_by_group = {}
for match in data['matches']:
    if 'group' not in match:
        continue  # Skip knockout stage matches
    
    group = match['group'].replace('Group ', '')
    team1 = match['team1']
    team2 = match['team2']
    
    if group not in teams_by_group:
        teams_by_group[group] = set()
    teams_by_group[group].add(team1)
    teams_by_group[group].add(team2)

# Print SQL
print('-- init_teams.sql')
print('-- Auto-generated from matches.json - ACTUAL 2026 World Cup teams')
print('-- All 48 teams for 2026 World Cup')
print()
print('DELETE FROM teams;')
print()
print('INSERT INTO teams (team_name, group_name) VALUES')

all_values = []
for group in sorted(teams_by_group.keys()):
    for team in sorted(teams_by_group[group]):
        all_values.append(f"('{team}', '{group}')")

print(',\n'.join(all_values) + ';')
