import pandas as pd

# 1. Recharger (ou réutiliser) les CSVs pour être sûr d'avoir bien les dates sous forme datetime
matches_df = pd.read_csv('./csv_output/matches.csv', parse_dates=['date'])
players_df = pd.read_csv('./csv_output/players.csv')
teams_df   = pd.read_csv('./csv_output/teams.csv')
match_players_df = pd.read_csv('./csv_output/match_players.csv')

# 2. Fusionner match_players avec la date et le nom d'équipe
mp = (
    match_players_df
    .merge(matches_df[['matchid', 'date']], on='matchid')
    .merge(teams_df[['idteam', 'name']], left_on='team_id', right_on='idteam')
    .rename(columns={'name': 'team_name'})
)

# 3. Trier et détecter les changements de club
mp = mp.sort_values(by=['playerid', 'date'])
transfers = []
for pid, group in mp.groupby('playerid'):
    group = group.reset_index(drop=True)
    start_date = group.at[0, 'date']
    current_team = group.at[0, 'team_name']
    player_name = players_df.loc[players_df['playerid'] == pid, 'lastname'].iat[0]

    for i in range(1, len(group)):
        row = group.loc[i]
        if row['team_name'] != current_team:
            # fin de la période
            end_date = row['date'] - pd.Timedelta(days=1)
            transfers.append({
                'playerid': pid,
                'player_name': player_name,
                'team': current_team,
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat(),
            })
            # nouveau club
            current_team = row['team_name']
            start_date = row['date']

    # ajouter la dernière période jusqu'au dernier match
    last_date = group['date'].max()
    transfers.append({
        'playerid': pid,
        'player_name': player_name,
        'team': current_team,
        'start_date': start_date.date().isoformat(),
        'end_date': last_date.date().isoformat(),
    })

# 4. Sauvegarde dans un CSV
transfers_df = pd.DataFrame(transfers)
transfers_df.to_csv('./csv_output/transfers.csv', index=False)
print(f"{len(transfers_df)} transferts détectés et exportés dans transfers.csv")
