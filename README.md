# FPL Team Predictor

Uses past FPL data in a prediction formula that assigns scores to players. Based on these scores, a squad is picked, subject to FPL's real team-building constraints:

1. A squad of 15 players must be picked.
2. Exactly 2 goalkeepers, 5 defenders, 5 midfielders, and 3 forwards must be included.
3. The total cost of the squad cannot exceed £100m.
4. No more than 3 players in the squad can belong to the same real team.
5. Players that are injured or suspended are excluded; doubtful players (`status == 'd'`) are still eligible.

## How to Use

1. Run `data_extractor.py` before every gameweek to pull current FPL player and fixture data. This overwrites `player_data.csv` each time (used by the optimizer), and also saves a permanent dated snapshot to `archive/player_data_gw{N}.csv` for future model training. Each run also backfills the *previous* gameweek's archived file with actual points scored, once known.
2. Run `optimizer.py`. This assigns a score to each player using the formula below, then selects the optimal legal squad and logs it to `predicted_squads_{season}.csv`.
3. After the gameweek concludes, run `manual_point_updation.py` and enter the points scored by each player in the predicted squad.
4. Run `best_11.py` to find the best legal starting 11 from the 15-player squad, along with a predicted captain (chosen by highest pre-GW formula score among the selected 11, doubling their points).
5. Run the weekly comparison logger to record that gameweek's results — your predicted best-11 score, your actual real-world squad score, the FPL average, and the gameweek's highest score — into `weekly_comparison_{season}.csv`.
6. Run `streamlit run dashboard.py` to view an interactive chart and season summary of all logged gameweeks.

## Scoring Formula

$$\text{Score} = \left( \frac{\text{Form}}{\text{Cost}} \right) \times \left( \frac{1}{\text{FDR}} \right)^{\frac{\text{Fixtures}}{2}} + \text{PPG}^{\frac{1}{3}}$$

Form is given the highest priority, as it's one of the most important indicators of how a player is likely to perform. A higher form/cost ratio combined with a lower FDR is expected to correlate with better performance.

The FDR term is raised to the power `fixtures/2` to minimize its influence in a normal single-fixture gameweek, while still punishing players during double gameweeks (fatigue, less rest time, rotation risk, and reduced priority given to some fixtures).

PPG is included as a separate additive term so players can still be meaningfully scored at the start of a season, before `form` (a rolling recent-performance stat) has any real data to draw from.

**Backtest results:** tested against real 2023-24 season data (GW1-9 as history, predicting average actual points across GW10-13). Found ~0.78 Spearman correlation and ~2-3/15 top-player overlap. Several formula variants (sqrt-cost, additive FDR, underlying-stats-based scoring using ICT/xG/xA) were also tested and none meaningfully beat this baseline — suggesting this is close to the ceiling of what's predictable from pre-game stats alone, given the inherent week-to-week variance in football.

## Data Archive

Every run of `data_extractor.py` saves a snapshot of the full player pool (form, cost, FDR, ICT index, xG/xA, minutes, bonus points system score, and more) to `archive/player_data_gw{N}.csv`. Once a gameweek concludes, the following run backfills that snapshot with actual points scored. This builds a season-long, per-player labeled dataset intended for future ML-based scoring (see Future Scope).

## Setup

```bash
pip install -r requirements.txt
python data_extractor.py           # run before each GW deadline
python optimizer.py                # generates + logs that week's predicted squad
python manual_point_updation.py    # after the GW finishes, enter real points
python best_11.py                  # finds your best legal 11 for that GW
python weekly_comparison.py        # logs the week's results for tracking
streamlit run dashboard.py         # view the season's performance visually
```

## Future Scope

- A continuous squad tracker that pulls your live FPL squad and suggests a single transfer per gameweek, looking ~5 weeks ahead, plus recommended chip usage.
- ML-based scoring, trained on the growing `archive/` dataset, to replace or augment the hand-built formula above — directly comparable against it using the same backtest methodology already established.