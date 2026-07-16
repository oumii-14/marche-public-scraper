"""
Module de Visualisation - Dashboard Streamlit amélioré
"""
import os, sys, django, pandas as pd, streamlit as st
from datetime import datetime, date, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marche_public.settings')
django.setup()

from scraper.models import Consultation, HistoriqueScraping, Alerte

st.set_page_config(page_title="Marchés Publics - Dashboard", layout="wide")
st.title("- Tableau de bord - Veille des marchés publics")

# ─── Cache data ───
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

# ─── Santé système ───
with st.expander("🗼 Système", expanded=False):
    cols = st.columns(3)
    dernier_hist = HistoriqueScraping.objects.order_by('-date_scraping').first()
    if dernier_hist:
        cols[0].success(f"Scraper actif (dernier: {dernier_hist.date_scraping.strftime('%d/%m/%Y %H:%M')})")
    else:
        cols[0].warning("Aucun scraping effectué")
    alertes_ajd = Alerte.objects.filter(date_envoi__date=date.today()).count()
    cols[1].success(f"Email opérationnel ({alertes_ajd} alertes aujourd'hui)")
    proch = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    if datetime.now() >= proch:
        proch += timedelta(days=1)
    cols[2].warning(f"Prochaine exécution: {proch.strftime('%d/%m/%Y %H:%M')}")

# ─── KPIs ───
total = len(df)
it = df[df['est_informatique'] == True].shape[0]
annulees = df[df['est_annule'] == True].shape[0]
urgentes = df[df['date_limite'].notna() & (df['date_limite'] < pd.Timestamp.now(tz='UTC'))].shape[0]
it_pct = round(it/total*100, 1) if total else 0

hier = df[df['date_publication'].dt.date == (datetime.now() - timedelta(1)).date()]
total_hier = len(hier)
it_hier = hier[hier['est_informatique'] == True].shape[0] if not hier.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("📄 Total offres", total, delta=f"+{total_hier} vs hier")
col2.metric(" Offres IT", f"{it} ({it_pct}%)", delta=f"+{it_hier} vs hier")
col3.metric(" Annulées", annulees)
col4.metric(" Urgentes", urgentes, delta=f"{round(urgentes/total*100)}% des offres")

# ─── Offres du jour ───
ajd = df[df['date_limite'].dt.date == date.today()]
it_ajd = ajd[ajd['est_informatique'] == True].shape[0]
if not ajd.empty:
    st.info(f" Nouvelles offres aujourd'hui : {len(ajd)} offres dont {it_ajd} IT")

# ─── Filtres ───
st.subheader(" Filtres")
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
    recherche = st.text_input(" Recherche", placeholder="Réf, objet, acheteur...")
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
df_filtre = df_filtre.sort_values('id', ascending=True)
st.markdown(f"**{len(df_filtre)} offre(s) affichée(s)**")

# ─── Graphiques ───
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.subheader("  Offres par mois")
    if not df_filtre.empty:
        offres_par_mois = df_filtre.groupby(df_filtre['date_limite'].dt.to_period('M')).size()
        offres_par_mois.index = offres_par_mois.index.astype(str)
        st.bar_chart(offres_par_mois, use_container_width=True)
with col_g2:
    st.subheader(" Top 10 régions")
    if not df_filtre.empty:
        top_reg = df_filtre.groupby('lieu').size().reset_index(name='count')
        top_reg = top_reg.sort_values('count', ascending=False).head(10)
        st.bar_chart(top_reg.set_index('lieu'))

col_g3, col_g4 = st.columns(2)
with col_g3:
    st.subheader(" Par catégorie")
    if not df_filtre.empty:
        cats = df_filtre.groupby('categorie').size().reset_index(name='count')
        st.bar_chart(cats.set_index('categorie'))
with col_g4:
    st.subheader(" IT vs Non-IT")
    if not df_filtre.empty:
        it_vs = df_filtre['est_informatique'].value_counts().reset_index()
        it_vs.columns = ['type', 'count']
        it_vs['type'] = it_vs['type'].map({True: 'IT', False: 'Non-IT'})
        st.bar_chart(it_vs.set_index('type'))

# Mots-clés les plus utilisés
st.subheader(" Mots-cles les plus utilises (offres IT)")
if not df_filtre.empty:
    IT_df = df_filtre[df_filtre['est_informatique'] == True].copy()
    mots_series = IT_df['mots_cles'].str.split(',\s*').explode().str.strip()
    mots_series = mots_series[mots_series != '']
    if not mots_series.empty:
        top_mots = mots_series.value_counts().head(10)
        top_mots = top_mots.sort_values(ascending=True)
        st.bar_chart(top_mots, use_container_width=True, height=400)
        st.caption(", ".join([f"**{m}**: {c}" for m, c in top_mots.items()]))
    else:
        st.info("Aucun mot-clé associé aux offres IT filtrées")
else:
    st.info("Aucune offre IT dans la sélection")

# Historique scrapings
st.subheader(" Histoire des scrapings")
historique = HistoriqueScraping.objects.all().order_by('-date_scraping')[:10]
if historique:
    h_data = []
    for h in historique:
        h_data.append({'Date': h.date_scraping, 'Consultations': h.nb_consultations, 'IT': h.nb_offres_it, 'Statut': h.statut})
    h_df = pd.DataFrame(h_data)
    h_df["Date"] = h_df["Date"].dt.strftime("%d/%m %H:%M")
    st.dataframe(h_df, use_container_width=True, height=250)
else:
    st.warning("Aucun historique de scraping")

col_g5, col_g6 = st.columns(2)
with col_g5:
    st.subheader(" Top 10 acheteurs")
    if not df_filtre.empty:
        acheteurs = df_filtre.groupby('acheteur').size().reset_index(name='count')
        acheteurs = acheteurs.sort_values('count', ascending=False).head(10)
        st.bar_chart(acheteurs.set_index('acheteur'))
with col_g6:
    st.subheader(" Urgentes (dépassées)")
    if not df_filtre.empty:
        maintenant = pd.Timestamp.now(tz='UTC')
        u = df_filtre[df_filtre['date_limite'].notna() & (df_filtre['date_limite'] < maintenant)]
        if not u.empty:
            urg_par_jour = u.groupby(u['date_limite'].dt.date).size()
            st.line_chart(urg_par_jour)
        else:
            st.info("Aucune offre urgente")

# ─── Tableau avec couleurs ───
st.subheader(" Liste des offres")
cols_aff = ['id', 'reference', 'objet', 'acheteur', 'lieu', 'date_limite', 'budget', 'est_informatique', 'est_annule', 'categorie', 'mots_cles']
df_aff = df_filtre[cols_aff].copy()
df_aff.columns = ['ID', 'Référence', 'Objet', 'Acheteur', 'Lieu', 'Date limite', 'Budget', 'IT', 'Annulé', 'Catégorie', 'Mots-clés']

def color_row(row):
    if row['Annulé'] == True:
        return ['background-color: #fde8e8'] * len(row)
    elif row['IT'] == True:
        return ['background-color: #e8f4e8'] * len(row)
    return [''] * len(row)

df_aff_val = df_aff.copy()
df_aff_val['IT'] = df_aff_val['IT'].map({True: ' IT', False: ' '})
df_aff_val['Annulé'] = df_aff_val['Annulé'].map({True: ' Oui', False: ' Non'})
df_aff_val['Date limite'] = df_aff_val['Date limite'].dt.strftime('%d/%m/%Y %H:%M')

st.dataframe(df_aff_val.style.apply(color_row, axis=1), use_container_width=True, height=500)

# Export Excel
try:
    import io
    buffer = io.BytesIO()
    df_excel = df_filtre[cols_aff].copy()
    for col in df_excel.select_dtypes(include=['datetimetz']).columns:
        df_excel[col] = df_excel[col].dt.tz_localize(None)
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_excel.to_excel(writer, index=False, sheet_name='Offres')
    st.download_button(label=" Télécharger (Excel)", data=buffer.getvalue(), file_name='offres_marches_publics.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
except ImportError:
    csv = df_filtre.to_csv(index=False, sep=';', encoding='utf-8-sig')
    st.download_button(label=" Télécharger (CSV)", data=csv.encode('utf-8-sig'), file_name='offres_marches_publics.csv', mime='text/csv', use_container_width=True)

st.caption(f"Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}")