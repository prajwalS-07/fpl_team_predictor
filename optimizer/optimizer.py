import pandas as pd
import pulp
import requests
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')

def optimizer():

    sys.stdout.reconfigure(encoding='utf-8')
    pd.set_option('display.precision',3)

    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        d = response.json()
    except requests.exceptions.ConnectionError:
        print("Couldn't reach the FPL API — check your internet connection.")
        return
    except requests.exceptions.Timeout:
        print("Request to the FPL API timed out. Try again.")
        return
    except requests.exceptions.HTTPError as e:
        print(f"FPL API returned an error: {e}")
        return

    data = pd.read_csv(os.path.join(DATA_DIR, 'player_data.csv'))
    data = data[data['status'].isin(['a', 'd'])].reset_index(drop=True)

    cost_safe = data['now_cost'].replace(0, pd.NA)
    fdr_term = (1 / data['fdr_avg']) ** (data['fixture_count'] / 2)
    availability_weight = data['chance_of_playing_next_round'] / 100

    score = ((data['form'] / cost_safe) * fdr_term + data['points_per_game'] ** (1/3)) * availability_weight
    data['score'] = score.where(data['fixture_count'] > 0, 0).fillna(0)

    max_budget = 100.0
    max_players = 15
    max_players_per_team = 3
    gks = 2
    defenders = 5
    midfielders = 5
    forwards = 3

    #initializieng problem
    problem = pulp.LpProblem('Squad_Optimizer', pulp.LpMaximize)
    player_vars = pulp.LpVariable.dicts("Select", data.index, cat='Binary')

    #def problem
    problem += pulp.lpSum([data.loc[i, 'score'] * player_vars[i] for i in data.index])

    #15 player squad
    problem += pulp.lpSum([player_vars[i] for i in data.index]) == max_players

    #total cost cant exceed 100
    problem += pulp.lpSum([data.loc[i, 'now_cost']*player_vars[i] for i in data.index]) <= max_budget

    #positional constraints:

    #  2 goalkeepers:
    problem += pulp.lpSum([player_vars[i] for i in data.index if data.loc[i, 'element_type'] == 1]) == gks

    #   5 defenders:
    problem += pulp.lpSum([player_vars[i] for i in data.index if data.loc[i, 'element_type'] == 2]) == defenders

    #   5 midfielders:
    problem += pulp.lpSum([player_vars[i] for i in data.index if data.loc[i, 'element_type'] == 3]) == midfielders

    #   3 forwards:
    problem += pulp.lpSum([player_vars[i] for i in data.index if data.loc[i, 'element_type'] == 4]) == forwards


    #   3 players per team
    for team_id in data['team'].unique():
        problem += (
        pulp.lpSum([
            player_vars[i] for i in data.index if data.loc[i, 'team'] == team_id
        ])
        <= max_players_per_team
    )

    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    selected_indices = [i for i in data.index if player_vars[i].varValue == 1]
    optimized_players = data.loc[selected_indices].copy()

    team_map = {team['id']: team['name'] for team in d['teams']}

    pos_map = {
        pos['id']: pos['singular_name_short'] for pos in d['element_types']
    }

    squad = optimized_players[['web_name','element_type','team','now_cost','score','chance_of_playing_next_round']].copy()
    squad = squad.sort_values(['element_type', 'score'], ascending=[True, False])

    squad['team'] = squad['team'].map(team_map)
    squad['element_type'] = squad['element_type'].map(pos_map)

    print(squad)

    log_path = os.path.join(DATA_DIR, 'predicted_squads_2026-27.csv')
    next_gw = next(e['id'] for e in d['events'] if e['is_next'])

    squad_to_log = optimized_players[['id', 'web_name', 'element_type', 'team', 'now_cost', 'score','chance_of_playing_next_round']].copy()
    squad_to_log = squad_to_log.sort_values(['element_type', 'score'], ascending=[True, False])

    squad_to_log['team'] = squad_to_log['team'].map(team_map)
    squad_to_log['element_type'] = squad_to_log['element_type'].map(pos_map)
    squad_to_log.insert(0, 'gw', next_gw)
    squad_to_log['points_scored'] = pd.NA 

    write_header = not os.path.exists(log_path)
    squad_to_log.to_csv(log_path, mode='a', header=write_header, index=False, encoding='utf-8')


if __name__ == '__main__':
    optimizer()