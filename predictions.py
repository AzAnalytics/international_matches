import streamlit as st
import pandas as pd
import numpy as np

# Chargement du DataFrame
df = pd.read_csv('all_matches.csv', sep=',')


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
