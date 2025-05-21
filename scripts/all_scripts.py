import re

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random

from scipy.stats import chi2_contingency
from import_data import teams_df, players_df, matches_df

teams_df['idteam'] = teams_df['idteam'].astype(int)
matches_df['home_idteam'] = matches_df['home_idteam'].astype(int)
matches_df['away_idteam'] = matches_df['away_idteam'].astype(int)

st.set_page_config(page_title="⚽️ Statistiques de Football", layout="wide")
st.title("📊 Football Data Explorer")

tabs = st.tabs([
    "⚽️ 4.1 - Clubs",
    "🧍‍♂️ 4.2 - Joueurs",
    "📅 4.3 - Matchs",
    "📈 5.1 - Résultats",
    "⚡️ 5.2 - Messi",
    "👕 5.3 - Stats Liverpool/Arsenal",
    "🏠📊 5.4 - Corrélation lieu du match/résultat",
    "💸 5.5 - Paris sportif",
    "🧠 5.6 - Corrélation formation/victoire"
])

# 4.1. Liste des clubs
with tabs[0]:
    st.header("⚽️ 4.1 - Informations sur les clubs")
    clubs_df = teams_df[['idteam', 'name']].sort_values('name').reset_index(drop=True)
    st.dataframe(clubs_df, use_container_width=True)

    # 4.1 Nom du club dont l'id est 43
    # Rechercher le club avec l'ID 43
    st.subheader("🔍 Recherche de club par ID")

    # S'assurer que les ID sont bien des entiers
    teams_df['idteam'] = teams_df['idteam'].astype(int)
    id_disponibles = sorted(teams_df['idteam'].unique())

    # Trouver l'index de 43 si présent
    index_defaut = id_disponibles.index(43) if 43 in id_disponibles else 0

    id_selection = st.selectbox("Sélectionnez un ID de club :", id_disponibles, index=index_defaut)

    club_nom = teams_df.loc[teams_df['idteam'] == id_selection, 'name'].iloc[0]
    st.success(f"Le club avec l'ID **{id_selection}** est : **{club_nom}**")

    # 4.1 Nombre total de clubs
    nombre_clubs = len(teams_df['idteam'].unique())
    st.info(f"Nombre total de clubs : **{nombre_clubs}**")


# 4.2 Liste des joueurs
with tabs[1]:
    st.header("🧍‍♂️ 4.2 - Informations sur les joueurs")

    joueurs_df = players_df[['playerid', 'lastname']].sort_values('lastname').reset_index(drop=True)

    st.subheader("Liste des joueurs :")
    st.dataframe(joueurs_df, use_container_width=True)

    # 4.2 Nombre total de joueurs
    nombre_joueurs = len(joueurs_df)
    st.info(f"Nombre total de joueurs : **{nombre_joueurs}**")

# 4.3
with tabs[2]:
    st.header("📅 4.3 - Informations sur les matchs")

    # Préparer le DataFrame des matchs
    matchs_df = matches_df[['matchid', 'date', 'home_idteam', 'away_idteam', 'home_score', 'away_score']].copy().reset_index(drop=True)
    matchs_df = matchs_df.sort_values('date')
    # Ajouter les noms des équipes
    matchs_df = matchs_df.merge(teams_df[['idteam', 'name']], left_on='home_idteam', right_on='idteam', how='left')
    matchs_df = matchs_df.merge(teams_df[['idteam', 'name']], left_on='away_idteam', right_on='idteam', how='left', suffixes=('_home', '_away'))

    # Sélectionner et renommer les colonnes pour affichage
    matchs_df = matchs_df[['matchid', 'date', 'name_home', 'name_away', 'home_score', 'away_score']]
    matchs_df.columns = ['ID Match', 'Date', 'Équipe Domicile', 'Équipe Extérieur', 'Score Domicile', 'Score Extérieur']

    # Afficher dans Streamlit
    st.subheader("Liste des matchs :")
    st.dataframe(matchs_df, hide_index=True, use_container_width=True)

    # Filtrer les matchs d'Arsenal à domicile
    arsenal_home = matchs_df[matchs_df['Équipe Domicile'] == 'Arsenal']

    # Affichage
    st.subheader("Matchs où Arsenal joue à domicile")
    if not arsenal_home.empty:
        st.dataframe(arsenal_home[['ID Match', 'Date', 'Équipe Extérieur', 'Score Domicile', 'Score Extérieur']], hide_index=True, use_container_width=True)
        st.success(f"{len(arsenal_home)} match(s) trouvé(s).")
    else:
        st.warning("Aucun match trouvé où Arsenal joue à domicile.")

    # 4.3 Affichage des matchs du 11 août 2019
    st.subheader("Matchs du 11 août 2019")

    # Conversion de la colonne Date en datetime
    matchs_df['Date'] = pd.to_datetime(matchs_df['Date'])

    # Filtrage des matchs du 11 août 2019
    date_cible = pd.to_datetime("2019-08-11").date()
    matchs_11_08_2019 = matchs_df[matchs_df['Date'].dt.date == date_cible]

    if not matchs_11_08_2019.empty:
        st.write("Voici les matchs joués le **11 août 2019** :")
        st.dataframe(matchs_11_08_2019, use_container_width=True, hide_index=True)
    else:
        st.warning("Aucun match n'a été joué le 11 août 2019.")

    # 4.3 Affichage du nombre de matchs en 2019
    matchs_2019 = matchs_df[matchs_df['Date'].dt.year == 2019]
    nombre_matchs_2019 = len(matchs_2019)

    # Affichage avec st.metric qui donne un joli encadré
    st.subheader("Nombre de matchs en 2019")
    st.metric(label="Matchs joués", value=nombre_matchs_2019)

    # 4.3 Affichage du nombre de matchs de Liverpool
    # Filtrer tous les matchs où Liverpool a joué
    matchs_liverpool = matchs_df[
        (matchs_df['Équipe Domicile'] == 'Liverpool') |
        (matchs_df['Équipe Extérieur'] == 'Liverpool')
        ]

    # Calcul des stats
    nombre_matchs_liverpool = len(matchs_liverpool)
    matchs_domicile = len(matchs_liverpool[matchs_liverpool['Équipe Domicile'] == 'Liverpool'])
    matchs_exterieur = len(matchs_liverpool[matchs_liverpool['Équipe Extérieur'] == 'Liverpool'])

    # Affichage général
    st.subheader("Matchs joués par Liverpool")
    st.metric(label="Total", value=nombre_matchs_liverpool)

    # Deux colonnes côte à côte pour domicile / extérieur
    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="🏟️ À domicile", value=matchs_domicile)
    with col2:
        st.metric(label="🚌 À l'extérieur", value=matchs_exterieur)

with tabs[3]:
    # 5.1 Résultats en fonction du club (championnat 5)
    st.header("📈 5.1 - Résultats en fonction du club (championnat 5)")
    matches_df['date'] = pd.to_datetime(matches_df['date'])

    # Section 1 : Résultats par club – Serie A 2019-2020
    st.subheader("1️⃣ Résultats par club – Serie A 2019-2020")

    # Période de la saison
    start_sa = pd.Timestamp('2019-08-23', tz='UTC')
    end_sa = pd.Timestamp('2020-08-03', tz='UTC')

    # Filtrage Serie A (championship == 5)
    serie_a = matches_df[
        (matches_df['championship'] == 5.0) &
        (matches_df['date'] > start_sa) &
        (matches_df['date'] < end_sa)
        ]

    # Équipes participantes
    serie_a_ids = pd.unique(serie_a[['home_idteam', 'away_idteam']].values.ravel())
    teams_sa = teams_df[teams_df['idteam'].isin(serie_a_ids)]

    # Calcul des résultats par équipe
    results = {name: {'V': 0, 'N': 0, 'D': 0} for name in teams_sa['name']}
    for _, m in serie_a.iterrows():
        home = teams_sa.loc[teams_sa['idteam'] == m['home_idteam'], 'name'].values[0]
        away = teams_sa.loc[teams_sa['idteam'] == m['away_idteam'], 'name'].values[0]

        if m['home_score'] > m['away_score']:
            results[home]['V'] += 1
            results[away]['D'] += 1
        elif m['home_score'] < m['away_score']:
            results[home]['D'] += 1
            results[away]['V'] += 1
        else:
            results[home]['N'] += 1
            results[away]['N'] += 1

    # Création du DataFrame récapitulatif
    summary_sa = pd.DataFrame(results).T
    summary_sa['Total'] = summary_sa.sum(axis=1)
    summary_sa = summary_sa[['V', 'N', 'D', 'Total']].sort_index()

    # Tableau interactif
    st.subheader("📊 Tableau des résultats")
    st.dataframe(summary_sa)

    # Graphique interactif avec Plotly
    fig = go.Figure(data=[
        go.Bar(name='Victoires', x=summary_sa.index, y=summary_sa['V'], marker_color='green'),
        go.Bar(name='Nuls', x=summary_sa.index, y=summary_sa['N'], marker_color='gray'),
        go.Bar(name='Défaites', x=summary_sa.index, y=summary_sa['D'], marker_color='red')
    ])

    fig.update_layout(
        barmode='group',
        title='Résultats par club – Serie A 2019-2020',
        xaxis_title='Club',
        yaxis_title='Nombre de matchs',
        xaxis_tickangle=-45,
        legend_title_text='Résultat',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Section 2 : Top 10 ratio de victoires – Premier League 2020-2021
    st.subheader("2️⃣ Top 10 ratio de victoires – Premier League 2020-2021")

    # Période Premier League
    start_pl = pd.Timestamp('2020-09-11', tz='UTC')
    end_pl = pd.Timestamp('2021-05-24', tz='UTC')

    # Filtrage des matchs de Premier League
    pl = matches_df[
        (matches_df['championship'] == 2.0) &
        (matches_df['date'] > start_pl) &
        (matches_df['date'] < end_pl)
        ]

    # Mapping id -> nom d'équipe
    team_names = teams_df.set_index('idteam')['name'].to_dict()

    # Calcul victoires et totaux
    stats = {}
    for _, row in pl.iterrows():
        for side, team_col, opp_score, team_score in [
            ('home', 'home_idteam', 'away_score', 'home_score'),
            ('away', 'away_idteam', 'home_score', 'away_score')
        ]:
            tid = row[team_col]
            stats.setdefault(tid, {'V': 0, 'Total': 0})
            stats[tid]['Total'] += 1
            if row[team_score] > row[opp_score]:
                stats[tid]['V'] += 1

    # Création DataFrame
    df_pl = pd.DataFrame.from_dict(stats, orient='index')
    df_pl['team'] = df_pl.index.map(team_names)
    df_pl = df_pl.dropna(subset=['team'])  # supprimer ceux sans nom d'équipe
    df_pl['Ratio'] = df_pl['V'] / df_pl['Total']

    # Top 10 par ratio
    df_pl = df_pl.sort_values('Ratio', ascending=False).head(10)[['team', 'V', 'Total', 'Ratio']]

    # Affichage tableau
    st.subheader("📊 Classement des équipes")
    st.dataframe(df_pl)

    # Graphique interactif
    fig = px.bar(
        df_pl,
        x='team',
        y='Ratio',
        text='Ratio',
        title='Top 10 des équipes par ratio de victoires - Premier League 2020-2021',
        labels={'team': 'Équipe', 'Ratio': 'Ratio de victoires'},
        color='Ratio',
        color_continuous_scale='blues'
    )

    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)

with tabs[4]:
    # 5.2 ID de Messi
    st.header("⚡️ 5.2 - Analyse des performances du joueur Messi")
    st.subheader("ID du joueur Messi")
    st.write("🔍 Recherche de l'ID d'un joueur")

    # Champ de texte pour le nom de famille
    lastname = st.text_input("Entrez le nom de famille du joueur", value="Messi")

    # Fonction de recherche
    @st.cache_data
    def find_player_id(lastname):
        player = players_df[players_df['lastname'].str.lower() == lastname.lower()]  # insensible à la casse
        if not player.empty:
            return player['playerid'].values[0]
        else:
            return None

    # Affichage du résultat
    if lastname:
        player_id = find_player_id(lastname)
        if player_id:
            st.success(f"✅ L'identifiant du joueur **{lastname}** est : `{player_id}`")
        else:
            st.error("❌ Joueur non trouvé.")

    # 5.2 clubs de Messi
    st.subheader("Historique des clubs de Messi")

    # Chargement des transferts
    transfers = pd.read_csv('./csv_output/transfers.csv', parse_dates=['start_date','end_date'])

    # ID joueur (Messi ici)
    player_id = 19054

    # Extraction des clubs
    clubs = transfers.loc[transfers['playerid'] == player_id, 'team'].unique()

    if len(clubs) > 0:
        st.write(f"Le joueur avec l'ID `{player_id}` a porté les maillots des clubs suivants :")
        for club in clubs:
            st.markdown(f"- **{club}**")
    else:
        st.write("Aucun club trouvé pour ce joueur.")

    # 5.2 Messi notes finales 2015
    st.subheader("Évolution des notes finales 2015 de Messi (3 matchs aléatoires)")

    # === 1. Charger les données ===
    match_players = pd.read_csv('./csv_output/match_players.csv')
    matches = pd.read_csv('./csv_output/matches.csv', parse_dates=['date'])

    # === 2. ID de Messi ===
    player_id = 19054

    # === 3. Fusionner les dates des matchs ===
    df = match_players.merge(matches[['matchid', 'date']], on='matchid')

    # === 4. Filtrer les lignes de Messi avec des notes valides ===
    player_df = df[(df['playerid'] == player_id) & df['final_mark_2015'].notna()].sort_values('date').reset_index(
        drop=True)

    if len(player_df) < 3:
        st.error(f"Pas assez de matchs ({len(player_df)}) pour le joueur {player_id}.")
    else:
        # === 5. Sélectionner 3 matchs consécutifs aléatoires ===
        start_idx = random.randint(0, len(player_df) - 3)
        sample3 = player_df.iloc[start_idx:start_idx + 3]

        # === 6. Afficher graphique interactif ===
        fig = px.line(
            sample3,
            x='date',
            y='final_mark_2015',
            markers=True,
            title=f"Évolution des notes sur 3 matchs consécutifs - Messi",
            labels={'date': 'Date du match', 'final_mark_2015': 'Note finale 2015'}
        )

        # Ajouter les annotations (tooltip au survol déjà activé)
        fig.update_traces(text=sample3['final_mark_2015'].astype(str), textposition='top center')
        fig.update_layout(xaxis_tickformat='%Y-%m-%d')

        st.plotly_chart(fig, use_container_width=True)

        # === 7. Afficher les dates ===
        st.write("🗓️ Dates des 3 matchs sélectionnés :", sample3['date'].dt.strftime('%Y-%m-%d').tolist())

    # 5.2 Cartons jounes et rouges Messi
    st.subheader("Cartons jaunes et rouges de Messi")

    # Charger les données
    highlights = pd.read_csv('./csv_output/highlights.csv')

    # ID du joueur
    player_id = 19054

    # Filtrer événements du joueur
    player_events = highlights[highlights['playerid'] == player_id]

    # Compter cartons
    yellow_cards = (player_events['type'] == 'yellowcard').sum()
    red_cards = player_events['type'].isin(['secondyellow', 'straightred']).sum()

    # Affichage
    st.write(f"Cartons pour le joueur avec l'ID `{player_id}` :")
    st.markdown(f"- 🟨 Jaunes : **{yellow_cards}**")
    st.markdown(f"- 🟥 Rouges : **{red_cards}**")

    # 5.2 Messi est-il le meilleur scoreur
    st.subheader("Messi est-il le meilleur scoreur ?")

    # === Charger les données ===
    highlights = pd.read_csv('./csv_output/highlights.csv')
    match_players = pd.read_csv('./csv_output/match_players.csv')
    matches = pd.read_csv('./csv_output/matches.csv')
    players = pd.read_csv('./csv_output/players.csv')
    teams = pd.read_csv('./csv_output/teams.csv')

    # === Mapping des championnats ===
    champ_names_map = matches[['championship']].drop_duplicates().sort_values('championship')
    champ_names_map['champ_name'] = champ_names_map['championship'].map({
        1.0: "Ligue 1",
        2.0: "Premier League",
        3.0: "La Liga",
        4.0: "Bundesliga",
        5.0: "Serie A",
    }).fillna("Inconnu")
    champ_id_to_name = champ_names_map.set_index('championship')['champ_name'].to_dict()

    # === Filtrer les buts ===
    goals = highlights[highlights['type'] == 'goal']

    # === Jointure avec match_players pour obtenir playerid → match ===
    goals_with_champ = goals.merge(match_players[['matchid', 'playerid']], on=['matchid', 'playerid'])
    goals_with_champ = goals_with_champ.merge(matches[['matchid', 'championship']], on='matchid')

    # === Top scoreurs ===
    top_scorers = goals_with_champ.groupby(['championship', 'playerid']).size().reset_index(name='goals')

    # === ID de Messi ===
    target_id = 19054

    # === Championnats où Messi a marqué ===
    player_champs = goals_with_champ[goals_with_champ['playerid'] == target_id]['championship'].unique()

    if len(player_champs) == 0:
        st.warning("Aucun championnat trouvé pour ce joueur.")
    else:
        for champ in player_champs:
            champ_name = champ_id_to_name.get(champ, f"Championnat {champ}")
            st.subheader(f"🏆 Top 10 buteurs - {champ_name}")

            # Scoreurs de ce championnat
            scorers_in_champ = top_scorers[top_scorers['championship'] == champ].sort_values(by='goals',
                                                                                             ascending=False).reset_index(
                drop=True)

            # Ajout des noms
            scorers_in_champ['lastname'] = scorers_in_champ['playerid'].map(
                lambda pid: players.loc[players['playerid'] == pid, 'lastname'].values[0]
                if pid in players['playerid'].values else "Inconnu"
            )

            top_10 = scorers_in_champ.head(10)[['playerid', 'lastname', 'goals']]
            top_10.columns = ['ID Joueur', 'Nom', 'Buts']
            st.dataframe(top_10)

            # === Graphique interactif avec Plotly ===
            fig = px.bar(
                top_10,
                x='Nom',
                y='Buts',
                color='Nom',
                text='Buts',
                title=f"Top 10 des buteurs dans {champ_name}",
                labels={'Nom': 'Joueur', 'Buts': 'Nombre de buts'},
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            # === Classement de Messi ===
            if target_id in scorers_in_champ['playerid'].values:
                rank = scorers_in_champ[scorers_in_champ['playerid'] == target_id].index[0] + 1
                total = len(scorers_in_champ)
                st.success(
                    f"🎯 Messi est **{rank}ᵉ** meilleur buteur du championnat **{champ_name}** sur {total} buteurs.")
            else:
                st.info("Le joueur n’a pas marqué dans ce championnat.")

with tabs[5]:
    # 5.3 ID de Liverpool et Arsenal
    st.header("👕 5.3 - Analyse des statistiques des clubs Liverpool et Arsenal")
    teams = pd.read_csv('./csv_output/teams.csv')

    clubs = teams[teams['name'].isin(['Liverpool', 'Arsenal']).reset_index(drop=True)];

    st.write("### IDs des clubs")
    clubs_reset = clubs.reset_index(drop=True)
    st.dataframe(clubs_reset)

    # 5.3 Joueurs d'Arsenal
    st.subheader("Joueurs ayant joué pour Arsenal")

    # Charger les fichiers
    players = pd.read_csv('./csv_output/players.csv')
    teams = pd.read_csv('./csv_output/teams.csv')
    match_players = pd.read_csv('./csv_output/match_players.csv')

    # Trouver l'ID d'Arsenal
    arsenal_team = teams[teams['name'].str.contains('Arsenal', case=False)]

    if not arsenal_team.empty:
        arsenal_id = arsenal_team.iloc[0]['idteam']

        # Récupérer les IDs des joueurs ayant joué pour Arsenal
        arsenal_players_ids = match_players[match_players['team_id'] == arsenal_id]['playerid'].unique()

        # Filtrer les joueurs
        arsenal_players = players[players['playerid'].isin(arsenal_players_ids)]

        # Nettoyer et trier
        player_table = (
            arsenal_players[['playerid', 'lastname']]
            .drop_duplicates()
            .sort_values(by='lastname')
            .reset_index(drop=True)
        )

        st.markdown(f"#### {len(player_table)} joueurs ont été repérés pour Arsenal")
        st.dataframe(player_table)

    else:
        st.error("❌ Le club Arsenal n’a pas été trouvé dans les données.")

    # 5.3 Un match entre Liverpool et Arsenal existe-t-il ?
    st.subheader("Matchs entre Liverpool et Arsenal")

    # Chargement des fichiers
    teams = pd.read_csv('./csv_output/teams.csv')
    matches = pd.read_csv('./csv_output/matches.csv')
    match_players = pd.read_csv('./csv_output/match_players.csv')
    players = pd.read_csv('./csv_output/players.csv')

    # Récupération des IDs
    teams_filtered = teams[teams['name'].str.contains('Liverpool|Arsenal', case=False)]

    if len(teams_filtered) < 2:
        st.error("❌ Impossible de trouver Liverpool ou Arsenal dans les données.")
    else:
        liverpool_id = teams_filtered[teams_filtered['name'].str.contains('Liverpool', case=False)].iloc[0]['idteam']
        arsenal_id   = teams_filtered[teams_filtered['name'].str.contains('Arsenal', case=False)].iloc[0]['idteam']

        # Filtrer les matchs entre les deux clubs
        direct_matches = matches[
            ((matches['home_idteam'] == liverpool_id) & (matches['away_idteam'] == arsenal_id)) |
            ((matches['home_idteam'] == arsenal_id) & (matches['away_idteam'] == liverpool_id))
        ]

        if direct_matches.empty:
            st.warning("Aucun match trouvé entre Liverpool et Arsenal.")
        else:
            st.success(f"{len(direct_matches)} match(s) trouvé(s) entre Liverpool et Arsenal.")

            # Affichage des matchs
            match_data = []
            for _, row in direct_matches.iterrows():
                home = teams[teams['idteam'] == row['home_idteam']]['name'].values[0]
                away = teams[teams['idteam'] == row['away_idteam']]['name'].values[0]
                home_score = row['home_score']
                away_score = row['away_score']
                date = pd.to_datetime(row['date']).strftime('%Y-%m-%d') if 'date' in row else 'Date inconnue'
                match_data.append({
                    'Date': date,
                    'Match': f"{home} {home_score} - {away_score} {away}"
                })

            st.subheader("Résultats des confrontations")
            st.dataframe(pd.DataFrame(match_data))

            # Prendre le 1er match et afficher les joueurs de Liverpool
            match_id = direct_matches.iloc[0]['matchid']
            liverpool_players = match_players[
                (match_players['matchid'] == match_id) &
                (match_players['team_id'] == liverpool_id)
            ][['playerid', 'position']]

            # Ajouter noms des joueurs
            liverpool_players = liverpool_players.merge(players[['playerid', 'lastname']], on='playerid', how='left')
            liverpool_players = liverpool_players[['lastname', 'position']].drop_duplicates().sort_values('lastname').reset_index(drop=True)

            st.subheader(f"Joueurs de Liverpool lors du match ID {match_id}")
            st.dataframe(liverpool_players)

    # 5.3 Evolution des notes moyennes par position en fonction du temps du club de Liverpool
    st.subheader("Évolution interactive des notes moyennes par poste chez Liverpool")

    # === Charger les données ===
    match_players = pd.read_csv('./csv_output/match_players.csv')
    matches = pd.read_csv('./csv_output/matches.csv', parse_dates=['date'])
    teams = pd.read_csv('./csv_output/teams.csv')

    # === Trouver l'ID de Liverpool ===
    liverpool_id = teams[teams['name'].str.contains("Liverpool", case=False, na=False)]['idteam'].iloc[0]

    # === Filtrer les joueurs de Liverpool ===
    liverpool_players = match_players[match_players['team_id'] == liverpool_id].copy()

    # === Préparer les données ===
    liverpool_players['matchid'] = liverpool_players['matchid'].astype(str)
    matches['matchid'] = matches['matchid'].astype(str)

    # Fusion avec la date des matchs
    liverpool_players = liverpool_players.merge(matches[['matchid', 'date']], on='matchid', how='left')

    # Nettoyer les positions
    liverpool_players['position'] = (
        liverpool_players['position']
        .str.lower()
        .str.strip()
        .replace({'striker': 'forward'})
    )

    # Supprimer la timezone si elle existe
    liverpool_players['date'] = liverpool_players['date'].dt.tz_localize(None)

    # === Moyennes mensuelles par poste ===
    avg_notes = (
        liverpool_players
        .groupby([
            liverpool_players['date'].dt.to_period('M').dt.to_timestamp().rename('month'),
            'position'
        ])['final_mark_2015']
        .mean()
        .reset_index()
        .rename(columns={'final_mark_2015': 'avg_note'})
    )

    # === Tracer avec Plotly ===
    fig = px.line(
        avg_notes,
        x='month',
        y='avg_note',
        color='position',
        markers=True,
        title="Évolution des notes moyennes par poste - Liverpool",
        labels={
            'month': 'Mois',
            'avg_note': 'Note moyenne',
            'position': 'Poste'
        }
    )

    fig.update_traces(hovertemplate='<br>Mois: %{x|%B %Y}<br>Note: %{y:.2f}')
    fig.update_layout(hovermode='x unified', legend_title_text='Poste')

    st.plotly_chart(fig, use_container_width=True)

    # 5.3 Evolution des écarts de résultats des clubs Liverpool et Arsenal
    st.subheader("Évolution interactive des écarts de résultats : Liverpool vs Arsenal")

    # 1. Charger les données
    matches_df = pd.read_csv('./csv_output/matches.csv', parse_dates=['date'])
    teams_df = pd.read_csv('./csv_output/teams.csv')

    # 2. Trouver les IDs de Liverpool et Arsenal
    liverpool_id = teams_df[teams_df['name'].str.contains("Liverpool", case=False, na=False)]['idteam'].iloc[0]
    arsenal_id = teams_df[teams_df['name'].str.contains("Arsenal", case=False, na=False)]['idteam'].iloc[0]


    # 3. Filtrer les matchs de Liverpool et Arsenal
    def compute_goal_diff(df, team_id):
        df = df.copy()
        df['goal_diff'] = df.apply(
            lambda row: row['home_score'] - row['away_score'] if row['home_idteam'] == team_id
            else row['away_score'] - row['home_score'], axis=1
        )
        df['club'] = teams_df[teams_df['idteam'] == team_id]['name'].values[0]
        return df[['date', 'goal_diff', 'club']]


    liverpool_matches = matches_df[
        (matches_df['home_idteam'] == liverpool_id) | (matches_df['away_idteam'] == liverpool_id)
        ]
    arsenal_matches = matches_df[
        (matches_df['home_idteam'] == arsenal_id) | (matches_df['away_idteam'] == arsenal_id)
        ]

    # 4. Calculer les écarts
    liverpool_data = compute_goal_diff(liverpool_matches, liverpool_id)
    arsenal_data = compute_goal_diff(arsenal_matches, arsenal_id)

    # 5. Fusionner les deux
    df_combined = pd.concat([liverpool_data, arsenal_data])

    # 6. Tracer avec Plotly
    fig = px.line(
        df_combined,
        x='date',
        y='goal_diff',
        color='club',
        markers=True,
        title="Évolution interactive des écarts de résultats",
        labels={'goal_diff': 'Écart de buts', 'date': 'Date'}
    )

    fig.update_traces(mode='lines+markers', hovertemplate='<br>Date: %{x|%d %B %Y}<br>Écart: %{y}',
                      text=df_combined['club'])
    fig.update_layout(legend_title_text='Club', hovermode='x unified')

    st.plotly_chart(fig, use_container_width=True)

    # 5.3 Nombre moyen de changement par match d'Arsenal
    st.subheader("Nombre moyen de changements par match d'Arsenal")

    # === 1. Charger les données ===
    matches_df = pd.read_csv('./csv_output/matches.csv', parse_dates=['date'])
    substitutions_df = pd.read_csv('./csv_output/substitutions.csv')
    teams_df = pd.read_csv('./csv_output/teams.csv')

    # === 2. Trouver l'ID d'Arsenal ===
    arsenal_id = teams_df[
        teams_df['name'].str.contains("Arsenal", case=False, na=False)
    ]['idteam'].iloc[0]

    # === 3. Filtrer les matchs d'Arsenal ===
    arsenal_matches = matches_df[
        (matches_df['home_idteam'] == arsenal_id) |
        (matches_df['away_idteam'] == arsenal_id)
        ].copy()

    # === 4. Compter les substitutions par match ===
    subs_per_match = (
        substitutions_df
        .query('matchid in @arsenal_matches.matchid')
        .groupby('matchid')
        .size()
        .reset_index(name='substitution_count')
    )

    # === 5. Fusionner et préparer ===
    arsenal_matches = (
        arsenal_matches
        .merge(subs_per_match, on='matchid', how='left')
    )
    arsenal_matches['substitution_count'] = arsenal_matches['substitution_count'].fillna(0)
    avg_subs = arsenal_matches['substitution_count'].mean()

    # Affichage du metric
    st.metric(label="Moyenne substitutions", value=f"{avg_subs:.2f}")

    # Affichage de l'histogramme avec Plotly
    st.subheader("Distribution des substitutions par match")
    fig = px.histogram(
        arsenal_matches,
        x='substitution_count',
        nbins=int(arsenal_matches['substitution_count'].max()) + 1,
        title="Histogramme des substitutions - Arsenal",
        labels={'substitution_count': 'Nombre de substitutions', 'count': 'Nombre de matchs'}
    )
    fig.update_layout(xaxis_tickmode='linear')
    st.plotly_chart(fig, use_container_width=True)

with tabs[6]:
    # 5.4 Corrélation entre match à domicile et victoire
    st.header("🏠📊 5.4 - Corrélation entre match à domicile et victoire")

    # Charger les données
    matches = pd.read_csv('./csv_output/matches.csv')

    # Préparer le résultat pour home et away
    matches['result_home'] = matches.apply(lambda row: 'Victoire' if row['home_score'] > row['away_score'] else (
        'Défaite' if row['home_score'] < row['away_score'] else 'Nul'), axis=1)
    matches['result_away'] = matches.apply(lambda row: 'Victoire' if row['away_score'] > row['home_score'] else (
        'Défaite' if row['away_score'] < row['home_score'] else 'Nul'), axis=1)

    # Créer enregistrements par équipe
    home = matches[['home_idteam', 'result_home']].rename(columns={'home_idteam': 'idteam', 'result_home': 'result'})
    home['lieu'] = 'Domicile'
    away = matches[['away_idteam', 'result_away']].rename(columns={'away_idteam': 'idteam', 'result_away': 'result'})
    away['lieu'] = 'Extérieur'
    all_results = pd.concat([home, away], ignore_index=True)

    # Tableau de contingence effectifs
    cont = all_results.groupby(['lieu', 'result']).size().unstack(fill_value=0)

    # Afficher les effectifs
    st.subheader("Tableau de contingence : effectifs")
    cont = cont[['Victoire', 'Nul', 'Défaite']]
    st.table(cont)

    # Pourcentages ligne à ligne
    pct = cont.div(cont.sum(axis=1), axis=0) * 100
    pct = pct.round(1)
    pct = pct[['Victoire', 'Nul', 'Défaite']]
    pct_formatted = pct.applymap(lambda x: f"{x:.1f}%")

    st.subheader("Tableau de contingence : pourcentages (%) par lieu")
    st.table(pct_formatted)

    # Test du chi2 sur 2x3
    chi2, p, _, _ = chi2_contingency(cont.values)
    st.markdown(f"**Chi2** = {chi2:.2f}, **p-value** = {p:.1f}")
    if p < 0.05:
        st.success(
            "✅ **Corrélation significative détectée.** On remarque que les résultats (victoire, défaite, nul) "
            "varient en fonction du lieu du match. Le test du Chi² confirme que cette différence n’est probablement "
            "pas due au hasard (p < 0.05)."
        )
    else:
        st.info(
            "ℹ️ **Pas de corrélation significative détectée.** On ne constate pas de réelle différence entre les résultats "
            "à domicile ou à l’extérieur. D’après le test du Chi², ces variations semblent être dues au hasard (p ≥ 0.05)."
        )

    # Visualisation interactive avec Plotly
    summary = cont.reset_index().melt(id_vars='lieu', value_vars=['Victoire', 'Nul', 'Défaite'],
                                      var_name='Résultat', value_name='Count')
    fig = px.bar(
        summary,
        x='lieu',
        y='Count',
        color='Résultat',
        barmode='group',
        text='Count',
        category_orders={'lieu': ['Domicile', 'Extérieur'], 'Résultat': ['Victoire', 'Nul', 'Défaite']},
        color_discrete_map={'Victoire': 'green', 'Nul': 'gray', 'Défaite': 'red'},
        title="Répartition des victoires, nuls et défaites selon le lieu"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis_title='Nombre de matchs')
    st.plotly_chart(fig, use_container_width=True)

# 5.5 Paris sportif
# === Charger les données ===
with tabs[7]:
    matches_df = pd.read_csv('./csv_output/matches.csv')
    teams_df = pd.read_csv('./csv_output/teams.csv')

    # === Fusionner les données ===
    matches_df = matches_df.merge(teams_df, left_on='home_idteam', right_on='idteam', how='left')
    matches_df = matches_df.rename(columns={'name': 'home_team_name'})

    matches_df = matches_df.merge(teams_df, left_on='away_idteam', right_on='idteam', how='left')
    matches_df = matches_df.rename(columns={'name': 'away_team_name'})

    # === Fonction pour calculer le gain pour un club donné ===
    def get_total_gain_for_club(club_name):
        club_matches = matches_df[
            (matches_df['home_team_name'] == club_name) | (matches_df['away_team_name'] == club_name)
        ]

        total_gain = 0
        for _, row in club_matches.iterrows():
            if row['home_team_name'] == club_name:
                if row['home_score'] > row['away_score']:
                    gain = row['quotation_home'] - 1
                else:
                    gain = -1
            elif row['away_team_name'] == club_name:
                if row['away_score'] > row['home_score']:
                    gain = row['quotation_away'] - 1
                else:
                    gain = -1
            total_gain += gain

        return total_gain

    # === Calcul des gains pour tous les clubs ===
    club_names = pd.unique(pd.concat([matches_df['home_team_name'], matches_df['away_team_name']]))
    club_gains = [{'club': name, 'gain': get_total_gain_for_club(name)} for name in club_names]
    club_gains_df = pd.DataFrame(club_gains).sort_values(by='gain', ascending=False).reset_index(drop=True)

    # === Interface Streamlit ===
    st.header("💸 5.5 Classement des clubs selon les gains de paris sportifs")
    st.write("Gain net si on avait misé 1€ sur chaque victoire d'un club.")

    # Tableau
    st.dataframe(club_gains_df)

    # Graphique
    top10 = club_gains_df.head(10).copy()
    top10['gain_fmt'] = top10['gain'].apply(lambda x: f"{x:.2f}€")

    fig = px.bar(
        top10,
        x='gain',
        y='club',
        orientation='h',
        color='gain',
        color_continuous_scale='greens',
        text='gain_fmt',
        title='📊 Top 10 des clubs les plus rentables',
        labels={'gain': 'Gain en €', 'club': 'Club'},
        hover_data=[]  # Ne pas afficher toutes les colonnes
    )

    fig.update_layout(yaxis=dict(autorange="reversed"))
    fig.update_traces(
        textposition='outside',
        hovertemplate='%{y}<br>Gain : %{x:.2f}€<extra></extra>'  # Contrôle du tooltip
    )

    st.plotly_chart(fig, use_container_width=True)

    # Club le plus rentable
    best_club = top10.iloc[0]['club']
    best_gain = top10.iloc[0]['gain']

    st.success(
        f"💰 **Le club le plus rentable est {best_club}** avec un gain net de **{best_gain:.2f}€** "
        "si on avait misé 1€ sur chacune de ses victoires."
    )

with tabs[8]:
    # 5.6 Corrélation entre formation et victoire
    st.header("🧠 5.6 - Corrélation entre formation et victoire")
    # 1. Charger les données
    matches = pd.read_csv('./csv_output/matches.csv', parse_dates=['date'])
    teams   = pd.read_csv('./csv_output/teams.csv')

    # 2. Mettre en « long » les deux équipes par match
    home = matches[[
        'matchid', 'date',
        'home_idteam', 'home_formation',
        'home_score', 'away_score'
    ]].copy()
    home.columns = [
        'matchid', 'date',
        'team_id', 'formation',
        'score_for', 'score_against'
    ]

    away = matches[[
        'matchid', 'date',
        'away_idteam', 'away_formation',
        'away_score', 'home_score'
    ]].copy()
    away.columns = [
        'matchid', 'date',
        'team_id', 'formation',
        'score_for', 'score_against'
    ]

    # 3. Calculer le résultat pour chaque ligne (1=victoire, 0=nul, -1=défaite)
    home['result'] = home['score_for'].gt(home['score_against']).astype(int)
    home.loc[ home['score_for'] < home['score_against'], 'result'] = -1

    away['result'] = away['score_for'].gt(away['score_against']).astype(int)
    away.loc[ away['score_for'] < away['score_against'], 'result'] = -1

    # 4. Concaténer les deux DataFrames
    all_teams = pd.concat([home, away], ignore_index=True)

    def clean_formation(f):
        f = str(f).lower()
        # Supprimer les lettres si c'est une forme comme "343d"
        f = re.sub(r'[^\d]', '', f)
        return "-".join(f)

    all_teams['formation'] = all_teams['formation'].apply(clean_formation)

    # 5. Calculer le taux de victoire par formation
    stats = (
        all_teams
          .groupby('formation')
          .agg(
             win_rate=('result', lambda x: (x == 1).mean()),
             count   =('result', 'size')
          )
        .reset_index()
        .sort_values(
            by=['win_rate', 'count'],
            ascending=[False, False]
        )
    )

    # Reprendre le DataFrame filtré
    stats_filtered = stats.copy()
    stats_filtered['win_rate_pct'] = stats_filtered['win_rate'] * 100  # Pour affichage en %

    # Affichage du tableau (optionnel)
    st.subheader("📋 Taux de victoire par formation")
    df_display = stats_filtered[['formation', 'win_rate_pct', 'count']].rename(columns={
        'formation': 'Formation',
        'win_rate_pct': 'Taux de victoire (%)',
        'count': 'Nb matchs'
    }).reset_index(drop=True)
    st.dataframe(df_display)

    # Graphique Plotly
    fig = px.bar(
        stats_filtered,
        x='formation',
        y='win_rate_pct',
        text='count',
        labels={'formation': 'Formation', 'win_rate_pct': 'Taux de victoire (%)'},
        title='📊 Taux de victoire par formation',
        color='win_rate_pct',
        color_continuous_scale='Blues'
    )

    fig.update_traces(
        textposition='outside',
        hovertemplate='<b>Formation</b>: %{x}<br>'
                      '<b>Taux de victoire</b>: %{y:.1f}%<br>'
                      '<b>Nombre de matchs</b>: %{text}<extra></extra>'
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis=dict(title='Taux de victoire (%)'),
        margin=dict(t=60, b=100),
        uniformtext_minsize=8,
        uniformtext_mode='hide'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "ℹ️ Globalement, on remarque que même si certaines formations ont un taux de victoire élevé, "
        "leur faible nombre de matchs limite la fiabilité de ces observations. \n"
        "Pour les formations les plus jouées, les taux de victoire varient sans qu’un pattern clair n’émerge vraiment, "
        "ce qui suggère qu’il n’y a pas de corrélation forte et robuste entre la formation utilisée et la victoire."
    )

