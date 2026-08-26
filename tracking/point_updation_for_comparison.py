import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')

def main():
    season = '2026-27'
    log_path = os.path.join(DATA_DIR, f'weekly_comparison_{season}.csv')

    try:
        gw = int(input("Gameweek: "))
        highest_score_may_include_chips = float(input("Maximum points scored: "))
        my_best11_points = float(input("Your best legal 11 points: "))
        fpl_average = float(input("FPL average points: "))
        p_1_points = float(input("Enter player 1's points: "))
    except ValueError:
        print("Enter valid numbers.")
        return

    new_row = pd.DataFrame([{
        'gw': gw,
        'my_best11_points': my_best11_points,
        'highest_score_may_include_chips': highest_score_may_include_chips,
        'fpl_average': fpl_average,
        'p_1': p_1_points
    }])

    if os.path.exists(log_path):
        data = pd.read_csv(log_path)
        data = data[data['gw'] != gw]
        data = pd.concat([data, new_row], ignore_index=True).sort_values('gw')
    else:
        data = new_row

    data.to_csv(log_path, index=False)
    print(f"GW{gw} logged to {log_path}.")

if __name__ == '__main__':
    main()