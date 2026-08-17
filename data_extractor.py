import pandas as pd
import requests
import sys

def extractor():
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

    df = pd.DataFrame(d['elements'])
    teams = pd.DataFrame(d['teams'])
    data = df[['id','web_name', 'element_type', 'form', 'now_cost', 'points_per_game','team','status','chance_of_playing_next_round']].copy()
    data = data.astype({'form':'float', 'points_per_game':'float'})
    data['now_cost'] /= 10
    data['chance_of_playing_next_round'] = data['chance_of_playing_next_round'].fillna(100)

    next_gw = next(e['id'] for e in d['events'] if e['is_next'])
    url2 = f'https://fantasy.premierleague.com/api/fixtures/?event={next_gw}'
    fixtures = requests.get(url2).json()
    fix = pd.DataFrame(fixtures)
    home = fix[['team_h','team_h_difficulty']].copy().rename(columns={'team_h':'team','team_h_difficulty':'fdr'})
    away = fix[['team_a','team_a_difficulty']].copy().rename(columns={'team_a':'team','team_a_difficulty':'fdr'})

    fdr_stuff = pd.concat([home,away],ignore_index=True)
    fdr_summary = fdr_stuff.groupby('team')['fdr'].agg(
        fdr_avg='mean',
        fixture_count='count'
    ).reset_index()

    fdr_d1 = dict(zip(fdr_summary['team'],fdr_summary['fdr_avg']))
    fdr_d2 = dict(zip(fdr_summary['team'],fdr_summary['fixture_count']))

    data['fdr_avg'] = data['team'].map(fdr_d1)
    data['fixture_count'] = data['team'].map(fdr_d2)

    data.to_csv('player_data.csv',index= False)

if __name__ == '__main__':
    extractor()