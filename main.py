import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Chargement du fichier CSV
df = pd.read_csv('all_matches.csv', sep=",")
# Logique pour déterminer l'équipe gagnante
conditions = [
    (df['home_score'] > df['away_score']),  # Home team wins
    (df['home_score'] < df['away_score'])  # Away team wins
]
choices = [df['home_team'], df['away_team']]
df['winning_team'] = np.select(conditions, choices, default='Draw')

# Exclure les matchs nuls si désiré
df_winners = df[df['winning_team'] != 'Draw']

# Compter le nombre de victoires par équipe
winning_teams_count = df_winners['winning_team'].value_counts()

# Titre de votre application Streamlit
st.title('Analyse des Victoires des Équipes')

# Affichage des équipes avec le plus de victoires dans Streamlit
st.subheader('Top 5 des Équipes avec le Plus de Victoires')
st.write(winning_teams_count.head())

# Vous pouvez également utiliser un graphique pour rendre les données plus digestes
st.bar_chart(winning_teams_count.head())

# Calcul de la somme des scores pour chaque match
df['total_score'] = df['home_score'] + df['away_score']

# Trouver le match avec le score le plus élevé
highest_scoring_match = df[df['total_score'] == df['total_score'].max()]

# Afficher le résultat dans Streamlit
st.title('Match avec le Score le Plus Élevé')
st.write('Voici le(s) match(s) avec le score le plus élevé dans l\'ensemble des données :')
st.write(highest_scoring_match)

# Ajouter une colonne indiquant si l'équipe à domicile a gagné
df['home_win'] = df['home_score'] > df['away_score']

# Calculer le pourcentage de victoires à domicile
home_win_percentage = df['home_win'].mean() * 100

# Afficher le résultat dans Streamlit
st.title('Analyse de la Performance des Équipes à Domicile')
st.write(f"Le pourcentage de victoires à domicile est de {home_win_percentage:.2f}%.")

#############
# Conversion de la colonne 'date' en datetime
df['date'] = pd.to_datetime(df['date'])

# Création de la liste des pays/équipes
countries_list = pd.concat([df['home_team'], df['away_team']]).unique()
countries_list.sort()

# Liste déroulante pour sélectionner une équipe
selected_country = st.selectbox('Choisir une équipe:', countries_list)

# Filtrer les matchs pour l'équipe sélectionnée
team_matches = df[(df['home_team'] == selected_country) | (df['away_team'] == selected_country)]


# Déterminer le résultat de chaque match pour l'équipe sélectionnée
def match_result(row):
    if (row['home_team'] == selected_country and row['home_score'] > row['away_score']) or \
            (row['away_team'] == selected_country and row['away_score'] > row['home_score']):
        return 'Win'
    elif (row['home_team'] == selected_country and row['home_score'] < row['away_score']) or \
            (row['away_team'] == selected_country and row['away_score'] < row['home_score']):
        return 'Loss'
    else:
        return 'Draw'


team_matches['result'] = team_matches.apply(match_result, axis=1)

# Grouper les résultats par année et compter les occurrences
performance_over_time = team_matches.groupby([team_matches['date'].dt.year, 'result']).size().unstack(fill_value=0)

# Utiliser Matplotlib pour tracer le graphique
fig, ax = plt.subplots()
performance_over_time.plot(kind='line', ax=ax, marker='o', figsize=(10, 6))
plt.title(f'Performance de {selected_country} au Fil du Temps')
plt.ylabel('Nombre de Matchs')
plt.xlabel('Année')
st.pyplot(fig)

# Assurez-vous que la date est au format datetime
df['date'] = pd.to_datetime(df['date'])


# Fonction pour déterminer la saison en fonction de la date
def determine_season(date):
    year = date.year
    if date.month >= 8:  # Saison commence en août et se termine l'année suivante
        return f'{year}/{year + 1}'
    else:
        return f'{year - 1}/{year}'


# Appliquer la fonction pour créer une colonne saison
df['season'] = df['date'].apply(determine_season)

# Calculer le score moyen par saison
average_scores_per_season = df.groupby('season')[['home_score', 'away_score']].mean()

# Visualisation avec Streamlit
st.line_chart(average_scores_per_season)

# Création de la figure pour la boîte à moustaches
plt.figure(figsize=(10, 6))
sns.boxplot(data=df[['home_score', 'away_score']])
plt.title('Boxplot des Scores à Domicile et à l\'Extérieur')

# Affichage de la figure dans Streamlit
st.pyplot(plt)

def get_last_10_matches_stats(team, df):
    # Séparation des matchs à domicile et à l'extérieur
    home_matches = df[df['home_team'] == team].tail(10)
    away_matches = df[df['away_team'] == team].tail(10)

    # Calculs des moyennes séparées
    avg_home_goals_scored = home_matches['home_score'].mean()
    avg_away_goals_scored = away_matches['away_score'].mean()
    avg_home_goals_conceded = home_matches['away_score'].mean()
    avg_away_goals_conceded = away_matches['home_score'].mean()

    return (avg_home_goals_scored, avg_away_goals_scored,
            avg_home_goals_conceded, avg_away_goals_conceded)


def predict_match_result(home_team, away_team, df):
    # Récupération des statistiques des 10 derniers matchs pour chaque équipe
    home_stats = get_last_10_matches_stats(home_team, df)
    away_stats = get_last_10_matches_stats(away_team, df)

    # Logique de prédiction (simplifiée pour cet exemple)
    # Ici, vous pourriez ajouter votre logique personnalisée basée sur les statistiques
    if home_stats[0] - away_stats[3] > away_stats[1] - home_stats[2]:
        return f"Victoire de {home_team}"
    elif home_stats[0] - away_stats[3] < away_stats[1] - home_stats[2]:
        return f"Victoire de {away_team}"
    else:
        return "Match nul"


# Interface Streamlit
st.title('Prédiction de Résultat de Match')

# Génération de la liste des pays
countries_list = pd.concat([df['home_team'], df['away_team']]).unique()
countries_list.sort()

col1, col2 = st.columns(2)

with col1:
    selected_home_team = st.selectbox('Choisir une équipe à domicile:', countries_list, key='home_team')

with col2:
    selected_away_team = st.selectbox('Choisir une équipe à l\'extérieur:', countries_list, key='away_team')

if st.button('Prédire le Résultat'):
    if selected_home_team == selected_away_team:
        st.error('Veuillez sélectionner deux équipes différentes.')
    else:
        home_stats = get_last_10_matches_stats(selected_home_team, df)
        away_stats = get_last_10_matches_stats(selected_away_team, df)

        with col1:
            # Affichage des statistiques
            st.write(f"Moyenne de buts marqués à domicile par {selected_home_team}: {home_stats[0]:.2f}")
            st.write(f"Moyenne de buts concédés à domicile par {selected_home_team}: {home_stats[2]:.2f}")
        with col2:
            st.write(f"Moyenne de buts marqués à l'extérieur par {selected_away_team}: {away_stats[1]:.2f}")
            st.write(f"Moyenne de buts concédés à l'extérieur par {selected_away_team}: {away_stats[3]:.2f}")

        # Prédiction du résultat
        result = predict_match_result(selected_home_team, selected_away_team, df)
        st.success(f'Prédiction du résultat du match : {result}')