import pandas as pd
import json
import os
import zipfile

ZIP_FILE = '../data.zip'
EXTRACT_DIR = '../'  # On extrait dans le dossier courant

# Si le dossier ./data/ n'existe pas mais le zip oui
if not os.path.exists('./data'):
    if os.path.exists(ZIP_FILE):
        with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)
            print("✅ Archive extraite")
    else:
        raise FileNotFoundError(f"❌ Ni dossier './data' ni fichier '{ZIP_FILE}' trouvés.")
else:
    print("📁 Le dossier './data' existe déjà.")

# Directory containing JSON files and output
json_directory = '../data'
output_dir = './csv_output'
os.makedirs(output_dir, exist_ok=True)

# Initialize lists
teams = []
players = []
matches = []
highlights = []
substitutions = []
match_players = []

# Sets for deduplication
seen_teams = set()
seen_players = set()

# Helper to safely get nested keys
def safe_get(d, *keys, default=None):
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            return default
        d = d[k]
    return d

def is_goal_valid(goal_event):
    # Si le type est "var", c'est un but annulé
    if goal_event.get('type') == 'var':
        return False
    # On peut ajouter d'autres conditions ici si besoin
    return True


# Process each JSON file
for fname in os.listdir(json_directory):
    if not fname.endswith('.json'):
        continue
    path = os.path.join(json_directory, fname)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Skipping {fname}, error: {e}")
        continue

    # Teams
    for side in ['Home', 'Away']:
        tid = safe_get(data, side, 'id')
        tname = safe_get(data, side, 'club', default='Unknown')
        if tid and tid not in seen_teams:
            teams.append({'idteam': tid, 'name': tname})
            seen_teams.add(tid)

    # Matches
    timeline = data.get('timeline', [])

    # Filtre les buts validés uniquement
    home_goals = [
        g for g in safe_get(data, 'matchData', 'home', 'goals', default=[])
        if is_goal_valid(g)
    ]
    away_goals = [
        g for g in safe_get(data, 'matchData', 'away', 'goals', default=[])
        if is_goal_valid(g)
    ]

    mid = safe_get(data, 'id')
    matches.append({
        'matchid': mid,
        'date': safe_get(data, 'dateMatch'),
        'home_idteam': safe_get(data, 'Home', 'id'),
        'away_idteam': safe_get(data, 'Away', 'id'),
        'duration': safe_get(data, 'matchTime'),
        'period': safe_get(data, 'period'),
        'championship': safe_get(data, 'championship'),
        'home_formation': safe_get(data, 'Home', 'players') and next(iter(data['Home']['players'].values()))['info'].get('formation_used'),
        'away_formation': safe_get(data, 'Away', 'players') and next(iter(data['Away']['players'].values()))['info'].get('formation_used'),
        'quotation_home': safe_get(data, 'quotationPreGame', 'Home'),
        'quotation_away': safe_get(data, 'quotationPreGame', 'Away'),
        'quotation_draw': safe_get(data, 'quotationPreGame', 'Draw'),
        'home_score': len(home_goals),
        'away_score': len(away_goals)
    })

    # Players and match_players
    for side in ['Home', 'Away']:
        team_id = safe_get(data, side, 'id')
        for pid, info in safe_get(data, side, 'players', default={}).items():
            pinfo = safe_get(info, 'info', default={})
            pid_val = pinfo.get('idplayer')
            lname = pinfo.get('lastname')
            if pid_val and pid_val not in seen_players:
                players.append({'playerid': pid_val, 'lastname': lname})
                seen_players.add(pid_val)

            # Record per-match player entry
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
            stats = safe_get(info, 'stat', default={})
            for k, v in stats.items():
                row[k] = v
            match_players.append(row)

    # Highlights (goals, bookings)
    for event in safe_get(data, 'matchData', 'home', 'goals', default=[]) + safe_get(data, 'matchData', 'away', 'goals',
                                                                                     default=[]):
        highlights.append({
            'matchid': mid,
            'time': event.get('time'),
            'playerid': event.get('playerId'),
            'type': 'goal'
        })

    for event in safe_get(data, 'matchData', 'home', 'bookings', default=[]) + safe_get(data, 'matchData', 'away',
                                                                                        'bookings', default=[]):
        booking_type = event.get('type')
        if booking_type == 'yellow':
            booking_type = 'yellowcard'
        elif booking_type == 'red':
            booking_type = 'redcard'

        highlights.append({
            'matchid': mid,
            'time': event.get('time'),
            'playerid': event.get('playerId'),
            'type': booking_type
        })

    # Substitutions
    for sub in safe_get(data, 'matchData', 'home', 'substitutions', default=[]) + safe_get(data, 'matchData', 'away', 'substitutions', default=[]):
        substitutions.append({'matchid': mid, 'time': sub.get('time'), 'off_playerid': sub.get('subOff'), 'on_playerid': sub.get('subOn'), 'reason': sub.get('reason', 'Unknown')})
    for ev in safe_get(data, 'timeline', default=[]):
        if ev.get('type') == 'substitution':
            substitutions.append({'matchid': mid, 'time': ev.get('time'), 'off_playerid': ev.get('subOff'), 'on_playerid': ev.get('subOn'), 'reason': ev.get('reason', 'Unknown')})

# Build DataFrames
teams_df = pd.DataFrame(teams).drop_duplicates(subset=['idteam'])
players_df = pd.DataFrame(players).drop_duplicates(subset=['playerid'])
matches_df = pd.DataFrame(matches).drop_duplicates(subset=['matchid'])
highlights_df = pd.DataFrame(highlights)
substitutions_df = pd.DataFrame(substitutions)
match_players_df = pd.DataFrame(match_players)

# Save to CSV
teams_df.to_csv(os.path.join(output_dir, 'teams.csv'), index=False)
players_df.to_csv(os.path.join(output_dir, 'players.csv'), index=False)
matches_df.to_csv(os.path.join(output_dir, 'matches.csv'), index=False)
highlights_df.to_csv(os.path.join(output_dir, 'highlights.csv'), index=False)
substitutions_df.to_csv(os.path.join(output_dir, 'substitutions.csv'), index=False)
match_players_df.to_csv(os.path.join(output_dir, 'match_players.csv'), index=False)

print("CSV export completed.")
print(f"Teams: {len(teams_df)}")
print(f"Players: {len(players_df)}")
print(f"Matches: {len(matches_df)}")
print(f"Highlights: {len(highlights_df)}")
print(f"Substitutions: {len(substitutions_df)}")
print(f"Match Players: {len(match_players_df)}")