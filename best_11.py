import pandas as pd
import pulp
import requests

url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
d = requests.get(url).json()

current_gw = next(e['id'] for e in d['events'] if e['is_previous'])

log_path = r'predicted_squads_2026-27.csv'
all_data = pd.read_csv(log_path, encoding='utf-8')

data = (all_data[(all_data['gw']).astype(int) == current_gw].copy().reset_index(drop=True))

prob = pulp.LpProblem("find_best_11",pulp.LpMaximize)
player_vars = pulp.LpVariable.dicts("Select", data.index, cat='Binary')

# defining the problem. we wanna find max points scored. constriants will be dealt with soon.
prob += pulp.lpSum([data.loc[i, 'points_scored']*player_vars[i] for i in data.index])

# single goalkeeper
prob += pulp.lpSum([player_vars[i] for i in data.index if data.loc[i,'element_type'] == 'GKP']) == 1

# minimum 3 defenders
prob += pulp.lpSum([player_vars[i] for i in data.index if data.loc[i,'element_type'] == 'DEF']) >= 3

# minimum 2 midfielders
prob += pulp.lpSum([player_vars[i] for i in data.index if data.loc[i,'element_type'] == 'MID']) >= 2

# min 1 forward
prob += pulp.lpSum([player_vars[i] for i in data.index if data.loc[i,'element_type'] == 'FWD']) >= 1

# we need exactly 11 players
prob += pulp.lpSum([player_vars[i] for i in data.index]) == 11

prob.solve(pulp.PULP_CBC_CMD(msg=False))

selected_indices = [i for i in data.index if player_vars[i].varValue == 1]
playing_11 = data.loc[selected_indices].copy()

print(playing_11.to_string())
captain_row = playing_11.loc[playing_11['score'].idxmax()]
captain_points = captain_row['points_scored']

max_points = playing_11['points_scored'].sum() + captain_points
print(f"Predicted captain: {captain_row['web_name']} ({captain_points} pts, doubled)")
print(f"Total points (with captain bonus) = {max_points}")