contains 2 parts: 
1. a data extractor that pulls data (like player_id, team, form, cost, ppg, fdr) from fpl's api and writes it onto a csv file. run this prog before every gw to get the latest info.
2. an optimizer that selects the best team every week based on certain factors and fpl constraints (15 player team with 2 gks, 5 def, 5 mid, 3 fwd, max 3 players per team, 100 mil budget).
