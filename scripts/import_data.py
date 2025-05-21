import pandas as pd
import json
import os

# Répertoires
output_dir = './csv_output'
os.makedirs(output_dir, exist_ok=True)

# Conteneurs pour les données
teams = []
players = []
matches = []
highlights = []
substitutions = []
match_players = []
transfers = []

# Pour éviter les doublons
seen_teams = set()
seen_players = set()

# Fonction utilitaire pour accéder à des clés imbriquées sans erreur
def safe_get(d, *keys, default=None):
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            return default
        d = d[k]
    return d

# Filtre des buts valides (exclure ceux annulés par VAR par exemple)
def is_goal_valid(goal_event):
    return goal_event.get('type') != 'var'

def parse_json_files(json_directory):
    teams, players, matches, highlights, substitutions, match_players, transfers = [], [], [], [], [], [], []
    seen_teams, seen_players = set(), set()


    # Parcours des fichiers JSON
    if not os.path.exists(json_directory):
        print(f"Le dossier {json_directory} n'existe pas !")
        os.makedirs(json_directory)
    else:
        for fname in os.listdir(json_directory):
            if not fname.endswith('.json'):
                continue
            path = os.path.join(json_directory, fname)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Skipping {fname} due to error: {e}")
                continue

            # --- Equipes ---
            for side in ['Home', 'Away']:
                tid = safe_get(data, side, 'id')
                tname = safe_get(data, side, 'club', default='Unknown')
                if tid and tid not in seen_teams:
                    teams.append({'idteam': tid, 'name': tname})
                    seen_teams.add(tid)

            # --- Match ---
            mid = safe_get(data, 'id')
            home_goals = [g for g in safe_get(data, 'matchData', 'home', 'goals', default=[]) if is_goal_valid(g)]
            away_goals = [g for g in safe_get(data, 'matchData', 'away', 'goals', default=[]) if is_goal_valid(g)]

            # Récupération formations home/away (en protégeant si players est vide)
            def get_formation(side):
                players_data = safe_get(data, side, 'players', default={})
                if players_data:
                    first_player = next(iter(players_data.values()))
                    return first_player.get('info', {}).get('formation_used')
                return None

            matches.append({
                'matchid': mid,
                'date': safe_get(data, 'dateMatch'),
                'home_idteam': safe_get(data, 'Home', 'id'),
                'away_idteam': safe_get(data, 'Away', 'id'),
                'duration': safe_get(data, 'matchTime'),
                'period': safe_get(data, 'period'),
                'championship': safe_get(data, 'championship'),
                'home_formation': get_formation('Home'),
                'away_formation': get_formation('Away'),
                'quotation_home': safe_get(data, 'quotationPreGame', 'Home'),
                'quotation_away': safe_get(data, 'quotationPreGame', 'Away'),
                'quotation_draw': safe_get(data, 'quotationPreGame', 'Draw'),
                'home_score': len(home_goals),
                'away_score': len(away_goals)
            })

            # --- Joueurs et joueurs par match ---
            for side in ['Home', 'Away']:
                team_id = safe_get(data, side, 'id')
                players_data = safe_get(data, side, 'players', default={})

                for pid, info in players_data.items():
                    pinfo = safe_get(info, 'info', default={})
                    pid_val = pinfo.get('idplayer')
                    lname = pinfo.get('lastname')

                    if pid_val and pid_val not in seen_players:
                        players.append({'playerid': pid_val, 'lastname': lname})
                        seen_players.add(pid_val)

                    # Infos joueur dans ce match
                    row = {
                        'playerid': pid_val,
                        'matchid': mid,
                        'team_id': team_id,
                        'position': pinfo.get('position'),
                        'formation_place': pinfo.get('formation_place'),
                        'play_duration': pinfo.get('mins_played'),
                        'final_mark_2015': pinfo.get('note_final_2015'),
                        'quotation_player': safe_get(data, 'quotationPlayers', f'player_{pid_val}')
                    }
                    # Stats diverses ajoutées dynamiquement
                    stats = safe_get(info, 'stat', default={})
                    row.update(stats)
                    match_players.append(row)

            # --- Highlights : buts & cartons ---
            for event in safe_get(data, 'matchData', 'home', 'goals', default=[]) + safe_get(data, 'matchData', 'away', 'goals', default=[]):
                highlights.append({
                    'matchid': mid,
                    'time': event.get('time'),
                    'playerid': event.get('playerId'),
                    'type': 'goal'
                })

            for event in safe_get(data, 'matchData', 'home', 'bookings', default=[]) + safe_get(data, 'matchData', 'away', 'bookings', default=[]):
                btype = event.get('type')
                if btype == 'yellow':
                    btype = 'yellowcard'
                elif btype == 'red':
                    btype = 'redcard'

                highlights.append({
                    'matchid': mid,
                    'time': event.get('time'),
                    'playerid': event.get('playerId'),
                    'type': btype
                })

            # --- Substitutions (deux sources possibles) ---
            for sub in safe_get(data, 'matchData', 'home', 'substitutions', default=[]) + safe_get(data, 'matchData', 'away', 'substitutions', default=[]):
                substitutions.append({
                    'matchid': mid,
                    'time': sub.get('time'),
                    'off_playerid': sub.get('subOff'),
                    'on_playerid': sub.get('subOn'),
                    'reason': sub.get('reason', 'Unknown')
                })
            for ev in safe_get(data, 'timeline', default=[]):
                if ev.get('type') == 'substitution':
                    substitutions.append({
                        'matchid': mid,
                        'time': ev.get('time'),
                        'off_playerid': ev.get('subOff'),
                        'on_playerid': ev.get('subOn'),
                        'reason': ev.get('reason', 'Unknown')
                    })

            # --- Transferts ---
            # 1. Recharger (ou réutiliser) les CSVs pour être sûr d'avoir bien les dates sous forme datetime
            matches_df = pd.read_csv('./csv_output/matches.csv', parse_dates=['date'])
            players_df = pd.read_csv('./csv_output/players.csv')
            teams_df = pd.read_csv('./csv_output/teams.csv')
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


        # Création DataFrames
        teams_df = pd.DataFrame(teams).drop_duplicates(subset=['idteam'])
        players_df = pd.DataFrame(players).drop_duplicates(subset=['playerid'])
        matches_df = pd.DataFrame(matches).drop_duplicates(subset=['matchid'])
        highlights_df = pd.DataFrame(highlights)
        substitutions_df = pd.DataFrame(substitutions)
        match_players_df = pd.DataFrame(match_players)
        transfers_df = pd.DataFrame(transfers)

        # Sauvegarde
        teams_df.to_csv(os.path.join(output_dir, 'teams.csv'), index=False)
        players_df.to_csv(os.path.join(output_dir, 'players.csv'), index=False)
        matches_df.to_csv(os.path.join(output_dir, 'matches.csv'), index=False)
        highlights_df.to_csv(os.path.join(output_dir, 'highlights.csv'), index=False)
        substitutions_df.to_csv(os.path.join(output_dir, 'substitutions.csv'), index=False)
        match_players_df.to_csv(os.path.join(output_dir, 'match_players.csv'), index=False)
        transfers_df.to_csv('./csv_output/transfers.csv', index=False)

        print("✅ Export CSV terminé.")
        print(f"Teams: {len(teams_df)}")
        print(f"Players: {len(players_df)}")
        print(f"Matches: {len(matches_df)}")
        print(f"Highlights: {len(highlights_df)}")
        print(f"Substitutions: {len(substitutions_df)}")
        print(f"Match Players: {len(match_players_df)}")
        print(f"{len(transfers_df)} transferts détectés et exportés dans transfers.csv")

        return teams_df, players_df, matches_df, highlights_df, substitutions_df, match_players_df, transfers_df


def load_data(json_directory='../data', force_refresh=False):
    csv_files = ['teams.csv', 'players.csv', 'matches.csv', 'highlights.csv', 'substitutions.csv',
                 'match_players.csv', 'transfers.csv']
    csv_paths = [os.path.join(output_dir, f) for f in csv_files]

    if all(os.path.exists(p) for p in csv_paths) and not force_refresh:
        teams_df = pd.read_csv(csv_paths[0])
        players_df = pd.read_csv(csv_paths[1])
        matches_df = pd.read_csv(csv_paths[2])
        highlights_df = pd.read_csv(csv_paths[3])
        substitutions_df = pd.read_csv(csv_paths[4])
        match_players_df = pd.read_csv(csv_paths[5])
        transfers_df = pd.read_csv(csv_paths[6])
        print("✅ Données chargées depuis les CSV.")
    else:
        teams_df, players_df, matches_df, highlights_df, substitutions_df, match_players_df, transfers_df = parse_json_files(json_directory)

    return teams_df, players_df, matches_df, highlights_df, substitutions_df, match_players_df, transfers_df
