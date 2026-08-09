import pandas as pd

def updation():

    log_path = 'predicted_squads_2026-27.csv'
    data = pd.read_csv(log_path, encoding='utf-8')

    gw = int(input("Gameweek to update: "))
    mask = data['gw'] == gw

    if not mask.any():
        print(f"No rows found for GW{gw}. Check the number and try again.")
    else:
        subset = data[mask]
        for idx, row in subset.iterrows():
            while True:
                entry = input(f"{row['web_name']} ({row['element_type']}) points scored: ")
                try:
                    data.loc[idx, 'points_scored'] = float(entry)
                    break
                except ValueError:
                    print("Enter a number.")

        data.to_csv(log_path, index=False, encoding='utf-8')
        print(f"GW{gw} updated and saved.")

if __name__ == '__main__':
    updation()