import pandas as pd

data = pd.read_csv(r'player_data.csv')

cost_safe = data['now_cost'].replace(0, pd.NA)
fdr_term = (1/data['fdr_avg'])**(data['fixture_count']/2)
data['score'] = ((data['form']/cost_safe)*fdr_term + data['ppg']**(1/3)).fillna(0)

print(data.head().to_string())