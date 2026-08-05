import pandas as pd
import pulp

data = pd.read_csv(r'player_data.csv')

cost_safe = data['now_cost'].replace(0, pd.NA)
fdr_term = (1/data['fdr_avg'])**(data['fixture_count']/2)
data['score'] = ((data['form']/cost_safe)*fdr_term + data['points_per_game']**(1/3)).fillna(0)

#initializieng problem
problem = pulp.LpProblem('Squad_Optimizer', pulp.LpMaximize)
player_vars = pulp.LpVariable.dicts("Select", data.index, cat='Binary')

#def problem
problem += pulp.lpSum([data.loc[i, 'score'] * player_vars[i] for i in data.index])

#15 player squad
problem += pulp.lpSum([player_vars[i] for i in data.index]) == 15

#total cost cant exceed 100
problem += pulp.lpSum([data.loc[i, 'now_cost']*player_vars[i] for i in data.index]) <= 100

#positional constraints:

#  2 goalkeepers:
problem += pulp.lpSum([player_vars[i] for i in data.index if data.loc[i, 'element_type'] == 1]) == 2

#   5 defenders:
problem += pulp.lpSum([player_vars[i] for i in data.index if data.loc[i, 'element_type'] == 2]) == 5

#   5 midfielders:
problem += pulp.lpSum([player_vars[i] for i in data.index if data.loc[i, 'element_type'] == 3]) == 5

#   3 forwards:
problem += pulp.lpSum([player_vars[i] for i in data.index if data.loc[i, 'element_type'] == 4]) == 3


#   3 players per team
for team_id in data['team'].unique():
  problem += (
      pulp.lpSum([
          player_vars[i] for i in data.index if data.loc[i, 'team'] == team_id
      ])
      <= 3
  )

problem.solve(pulp.PULP_CBC_CMD(msg=False))

selected_indices = [i for i in data.index if player_vars[i].varValue == 1]
squad = data.loc[selected_indices].copy()

