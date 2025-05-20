# 📊 Football Data Explorer

Bienvenue dans **Football Data Explorer**, une application interactive développée avec **Streamlit**, qui permet d'explorer, visualiser et analyser des données de matchs de football professionnels (résultats, formations, substitutions, paris, etc.).

## 🚀 Fonctionnalités

L'application est organisée par onglets et propose les analyses suivantes :

### ⚽️ 4.1 - Clubs
Explore les informations clés des clubs présents dans la base.

### 🧍‍♂️ 4.2 - Joueurs
Analyse les caractéristiques des joueurs (âge, taille, poste...).

### 📅 4.3 - Matchs
Affiche les détails de chaque match : date, score, clubs, etc.

### 📈 5.1 - Résultats en fonction du club
Permet d’analyser les performances globales d’un club sélectionné.

### 📊 5.2 - Répartition des scores
Histogramme interactif de la répartition des scores (victoires, nuls, défaites).

### 📉 5.3 - Évolution des écarts de résultats : Liverpool vs Arsenal
Graphique dynamique comparant l’évolution des écarts de buts pour ces deux clubs.

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
streamlit run app.py
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