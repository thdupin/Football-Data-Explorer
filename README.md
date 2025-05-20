# 📊 Football Data Explorer

Bienvenue dans **Football Data Explorer**, une application interactive développée avec **Streamlit**, qui permet d'explorer, visualiser et analyser des données de matchs de football professionnels (résultats, formations, substitutions, paris, etc.).

## 🚀 Fonctionnalités

L'application est organisée par onglets et propose les analyses suivantes :

### ⚽️ 4.1 - Clubs
Explore les informations clés des clubs présents dans la base :
- Afficher la liste complète des clubs (idteam et nom)
- Quel est le nom du club avec l’ID 43 ?
- Nombre total de clubs présents dans la base

### 🧍🧍‍♂️ 4.2 - Joueurs
Analyse des caractéristiques des joueurs :
- Afficher la liste complète des joueurs
- Nombre total de joueurs dans la base

### 📅 4.3 - Matchs
Détails des matchs joués :
- Afficher la liste des matchs
- Afficher tous les ID des matchs où Arsenal est le club à domicile
- Afficher les informations des matchs joués le 11-08-2019
- Nombre total de matchs joués en 2019
- Nombre de matchs joués par le club Liverpool

### 📈 5.1 - Résultats en fonction du club
- Afficher le nombre de matchs par club pour le championnat 5 (Série A) saison 2019-2020 (victoires, défaites, matchs nuls).
- Dates du championnat 5 (Série A) : 24 août 2019 - 2 août 2020.
- Afficher les 10 meilleures équipes du championnat 2 (Premier League) saison 2020-2021 (meilleur ratio victoires/matchs joués).
- Dates du championnat 2 (Premier League) : 12 septembre 2020 - 23 mai 2021.
- Visualisations incluses.

### 📊 5.2 - Analyse des performances du joueur Messi
- Quel est l’ID du joueur Messi ? (requête)
- À quel(s) club(s) appartient-il ? (requête)
- Calcul des performances (note_final_2015) sur 3 matchs consécutifs, avec évolution dans le temps (visualisation).
- Nombre de cartons jaunes et rouges reçus.
- Est-il dans le top 10 des buteurs de son championnat ? (afficher id, nom, nombre de buts) (requête).

### 📉 5.3 - Évolution des écarts de résultats : Liverpool vs Arsenal
- Trouver les team_id de Liverpool et Arsenal.
- Liste des joueurs d’Arsenal (id, nom).
- Existence de match(s) Liverpool vs Arsenal ? Score(s) et liste des joueurs Liverpool (id, position) pour un de ces matchs.
- Évolution des notes moyennes (note_final_2015) par position (défenseur, milieu, attaquant — forward/striker regroupés) pour Liverpool (visualisation).
- Graphique d’évolution des écarts de résultats Liverpool vs Arsenal (victoire=+1, défaite=score négatif, nul=0).

### 🔄 5.3 bis - Nombre moyen de substitutions d’Arsenal
Analyse quantitative des changements effectués par match.

### 🏠📊 5.4 - Corrélation entre lieu (domicile/extérieur) et victoire
Test du **Chi2** pour analyser s’il existe un lien entre le lieu du match et le résultat.

### 💸 5.5 - Paris sportifs
Classement des clubs selon leur rentabilité si on avait misé 1€ sur chacune de leurs victoires.

### 🧠 5.6 - Corrélation entre formation et victoire
Analyse du taux de victoire par système de jeu (ex : 4-3-3, 3-5-2...).

---

## 📦 Installation

1. **Cloner le projet** :

```bash
git clone https://github.com/thdupin/Football-Data-Explorer.git
cd Football-Data-Explorer
```

2. **Créer un environnement virtuel (recommandé)** :
```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
```

3. **Installer les dépendance** :
```bash
pip install -r requirements.txt
```

# ▶️ Lancer l'application
```bash
cd /scripts
streamlit run all_scripts.py
```

# 🧠 Données utilisées
L’application repose sur des données CSV préalablement extraites ou préparées :

- **matches.csv** : données de match (scores, formations, cotes)
- **teams.csv** : noms et identifiants des clubs
- **players.csv** : informations individuelles sur les joueurs
- **substitutions.csv** : détails des remplacements par match
- **highlights.csv** : temps forts par match
- **match_players.csv** : perfomances individuelles des joueurs pas match
- **transfers.csv** : historique des transferts

Ces fichiers sont dans le dossier ```csv_output/```.

# 🧪 Exemples d’analyses réalisées
- Statistiques interactives par club
- Analyse de rentabilité par paris sportifs
- Impact du lieu ou du système de jeu sur les victoires
- Visualisation des substitutions

# 📌 Dépendances techniques
Voici les principales librairies utilisées :

- streamlit
- pandas
- plotly
- scipy

Voir ```requirements.txt``` pour plus de détails.

# 👨‍💻 Auteur
Développé par Théo DUPIN.