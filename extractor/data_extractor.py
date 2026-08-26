import pandas as pd
import requests
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
ARCHIVE_DIR = os.path.join(SCRIPT_DIR, '..', 'archive')

def extractor():
    sys.stdout.reconfigure(encoding='utf-8')
    pd.set_option('display.precision', 3)

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
    data = df[['id', 'web_name', 'element_type', 'form', 'now_cost', 'points_per_game',
           'team', 'status', 'chance_of_playing_next_round',
           'selected_by_percent', 'ict_index', 'influence', 'creativity', 'threat',
           'expected_goals', 'expected_assists', 'expected_goal_involvements',
           'minutes', 'bps', 'event_points']].copy()

    data = data.astype({
        'form': 'float',
        'points_per_game': 'float',
        'selected_by_percent': 'float',
        'ict_index': 'float',
        'influence': 'float',
        'creativity': 'float',
        'threat': 'float',
        'expected_goals': 'float',
        'expected_assists': 'float',
        'expected_goal_involvements': 'float'
    })

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

    os.makedirs(DATA_DIR, exist_ok=True)
    data.to_csv(os.path.join(DATA_DIR, 'player_data.csv'), index=False, encoding='utf-8')

    archive_data = data.copy()
    archive_data['gw'] = next_gw
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    archive_path = os.path.join(ARCHIVE_DIR, f'player_data_gw{next_gw}.csv')
    archive_data.to_csv(archive_path, index=False, encoding='utf-8')

    prev_gw = next_gw - 1
    prev_archive_path = os.path.join(ARCHIVE_DIR, f'player_data_gw{prev_gw}.csv')

    if os.path.exists(prev_archive_path):
        prev_data = pd.read_csv(prev_archive_path)
        actual_points = data[['id', 'event_points']].rename(columns={'event_points': 'actual_points'})

        if 'actual_points' in prev_data.columns:
            prev_data = prev_data.drop(columns=['actual_points'])

        prev_data = prev_data.merge(actual_points, on='id', how='left')
        prev_data.to_csv(prev_archive_path, index=False, encoding='utf-8')
        print(f"Backfilled actual points into GW{prev_gw}'s archive.")

if __name__ == '__main__':
    extractor()