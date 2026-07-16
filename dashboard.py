"""
Module de Visualisation - Semaine 4
Dashboard Streamlit pour la plateforme de veille
"""

import os
import sys
import django
import pandas as pd
import streamlit as st
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marche_public.settings')
django.setup()

from scraper.models import Consultation

st.set_page_config(page_title="Marchés Publics - Dashboard", layout="wide")
st.title("📊 Tableau de bord - Veille des marchés publics")
st.markdown("---")

@st.cache_data
def charger_donnees():
    offres = Consultation.objects.select_related('acheteur', 'categorie').all()
    data = []
    for offre in offres:
        data.append({
            'id': offre.id,
            'reference': offre.reference,
            'objet': offre.objet[:100],
            'acheteur': offre.acheteur.nom if offre.acheteur else '',
            'date_limite': offre.date_limite,
            'lieu': offre.lieu_execution or 'Non spécifié',
            'budget': offre.budget_estime or 'N/A',
            'est_informatique': offre.est_informatique,
            'est_annule': offre.est_annule,
            'categorie': offre.categorie.nom if offre.categorie else '',
            'date_publication': offre.date_publication,
            'mots_cles': ', '.join(offre.mots_cles.values_list('mot', flat=True))
        })
    return pd.DataFrame(data)

df = charger_donnees()

# --- KPIs ---
total = len(df)
it = df[df['est_informatique'] == True].shape[0]
annulees = df[df['est_annule'] == True].shape[0]
urgentes = df[df['date_limite'].notna() & (df['date_limite'] < pd.Timestamp.now(tz='UTC'))].shape[0]
it_pct = round(it / total * 100, 1) if total else 0

# Âge des données
derniere_maj = df['date_publication'].max()
age_jours = (datetime.now().date() - derniere_maj.date()).days if pd.notna(derniere_maj) else 'N/A'

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("📄 Total offres", total)
col2.metric("💻 Offres IT", f"{it} ({it_pct}%)")
col3.metric("❌ Annulées", annulees)
col4.metric("⏰ Urgentes", urgentes)
col5.metric("🏷️ Catégories", df['categorie'].nunique())
col6.metric("🔄 Âge données", f"{age_jours}j" if age_jours != 'N/A' else 'N/A')
st.markdown("---")

# --- Filtres ---
st.subheader("🔍 Filtres")
col_f1, col_f2 = st.columns(2)
col_f3, col_f4 = st.columns(2)

with col_f1:
    filtre_it = st.selectbox("Secteur", ["Tous", "IT", "Non-IT"])
with col_f2:
    regions = ["Toutes"] + sorted(df['lieu'].unique().tolist())
    filtre_region = st.selectbox("Région", regions)
with col_f3:
    categories = ["Toutes"] + sorted(df['categorie'].unique().tolist())
    filtre_categorie = st.selectbox("Catégorie", categories)
with col_f4:
    recherche = st.text_input("🔎 Recherche", placeholder="Réf, objet, acheteur...")

col_f5, col_f6 = st.columns(2)
with col_f5:
    date_min = df['date_limite'].min().date() if pd.notna(df['date_limite'].min()) else date.today()
    date_max = df['date_limite'].max().date() if pd.notna(df['date_limite'].max()) else date.today()
    date_debut = st.date_input("Date début", value=date_min, min_value=date_min, max_value=date_max)
with col_f6:
    date_fin = st.date_input("Date fin", value=date_max, min_value=date_min, max_value=date_max)

df_filtre = df.copy()
if filtre_it == "IT":
    df_filtre = df_filtre[df_filtre['est_informatique'] == True]
elif filtre_it == "Non-IT":
    df_filtre = df_filtre[df_filtre['est_informatique'] == False]
if filtre_region != "Toutes":
    df_filtre = df_filtre[df_filtre['lieu'] == filtre_region]
if filtre_categorie != "Toutes":
    df_filtre = df_filtre[df_filtre['categorie'] == filtre_categorie]
if recherche:
    df_filtre = df_filtre[
        df_filtre['reference'].str.contains(recherche, case=False, na=False) |
        df_filtre['objet'].str.contains(recherche, case=False, na=False) |
        df_filtre['acheteur'].str.contains(recherche, case=False, na=False)
    ]
df_filtre = df_filtre[
    df_filtre['date_limite'].notna() &
    (df_filtre['date_limite'].dt.date >= date_debut) &
    (df_filtre['date_limite'].dt.date <= date_fin)
]

st.markdown(f"**{len(df_filtre)} offre(s) affichée(s)**")
st.markdown("---")

# --- Graphiques ligne 1 ---
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("📈 Offres par jour (date limite)")
    if not df_filtre.empty:
        offres_par_jour = df_filtre.groupby(df_filtre['date_limite'].dt.date).size()
        st.line_chart(offres_par_jour)

with col_g2:
    st.subheader("📍 Top 10 régions")
    if not df_filtre.empty:
        regions = df_filtre.groupby('lieu').size().reset_index(name='count')
        regions = regions.sort_values('count', ascending=False).head(10)
        st.bar_chart(regions.set_index('lieu'))

st.markdown("---")

# --- Graphiques ligne 2 ---
col_g3, col_g4 = st.columns(2)

with col_g3:
    st.subheader("🏷️ Par catégorie")
    if not df_filtre.empty:
        cats = df_filtre.groupby('categorie').size().reset_index(name='count')
        st.bar_chart(cats.set_index('categorie'))

with col_g4:
    st.subheader("💻 IT vs Non-IT")
    if not df_filtre.empty:
        it_vs = df_filtre['est_informatique'].value_counts().reset_index()
        it_vs.columns = ['type', 'count']
        it_vs['type'] = it_vs['type'].map({True: 'IT', False: 'Non-IT'})
        st.bar_chart(it_vs.set_index('type'))

st.markdown("---")

# --- Graphiques ligne 3 ---
col_g5, col_g6 = st.columns(2)

with col_g5:
    st.subheader("🏢 Top 10 acheteurs")
    if not df_filtre.empty:
        acheteurs = df_filtre.groupby('acheteur').size().reset_index(name='count')
        acheteurs = acheteurs.sort_values('count', ascending=False).head(10)
        st.bar_chart(acheteurs.set_index('acheteur'))

with col_g6:
    st.subheader("⏰ Offres urgentes (dépassées)")
    if not df_filtre.empty:
        maintenant = pd.Timestamp.now(tz='UTC')
        urgentes_df = df_filtre[df_filtre['date_limite'].notna() & (df_filtre['date_limite'] < maintenant)]
        if not urgentes_df.empty:
            urgentes_par_jour = urgentes_df.groupby(urgentes_df['date_limite'].dt.date).size()
            st.line_chart(urgentes_par_jour)
        else:
            st.info("Aucune offre urgente")

st.markdown("---")

# --- Tableau ---
st.subheader("📋 Liste des offres")
colonnes = ['reference', 'objet', 'acheteur', 'lieu', 'date_limite', 'budget', 'est_informatique', 'est_annule', 'categorie', 'mots_cles']
df_affichage = df_filtre[colonnes].copy()
df_affichage.columns = ['Référence', 'Objet', 'Acheteur', 'Lieu', 'Date limite', 'Budget', 'IT', 'Annulé', 'Catégorie', 'Mots-clés']
df_affichage['IT'] = df_affichage['IT'].map({True: '✅', False: '❌'})
df_affichage['Annulé'] = df_affichage['Annulé'].map({True: '❌ Oui', False: '✅ Non'})

col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.dataframe(df_affichage, use_container_width=True, height=500)
with col_t2:
    csv_data = df_filtre.to_csv(index=False, sep=';', encoding='utf-8-sig')
    st.download_button(
        label="📥 Télécharger (CSV)",
        data=csv_data.encode('utf-8-sig'),
        file_name='offres_marches_publics.csv',
        mime='text/csv',
        use_container_width=True
    )

st.markdown("---")
st.caption(f"Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
