"""
Module de Visualisation - Dashboard Streamlit
"""
import os, sys, django, pandas as pd, streamlit as st
from datetime import datetime, date, timedelta
from streamlit_autorefresh import st_autorefresh

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marche_public.settings')
django.setup()

from scraper.models import Consultation, HistoriqueScraping, Alerte

st.set_page_config(page_title="Marches Publics - Dashboard", layout="wide")

MOT_DE_PASSE = "marche2026"

# ─── CSS Global ───
st.markdown("""
<style>
.stApp {background: #f5f7fa;}
.stButton > button[kind="primary"] {
    background-color: #f7941e !important;
    color: #003366 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    padding: 10px 0 !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #e67e22 !important;
    color: white !important;
}
.section-title {
    color: #003366;
    font-size: 16px;
    font-weight: 700;
    margin: 24px 0 12px 0;
    padding-bottom: 6px;
    border-bottom: 2px solid #f7941e;
}
</style>
""", unsafe_allow_html=True)

# ─── Auth ───
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    st.markdown("""
    <style>
    h2 {margin-top: 0 !important;}
    .stTextInput > div > div > input {
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 18px 22px;
        font-size: 18px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #f7941e;
        box-shadow: 0 0 0 3px rgba(247,148,30,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='color:#003366;margin:0;'>Dashboard Marches Publics</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#666666;margin-top:6px;font-size:16px;'>Connectez-vous pour acceder au tableau de bord</p>", unsafe_allow_html=True)

    mot_passe = st.text_input("", type="password", placeholder="Entrez votre mot de passe", label_visibility="collapsed")

    if st.button("Se connecter", use_container_width=True, type="primary", key="btn_login"):
        if mot_passe == MOT_DE_PASSE:
            st.session_state.authentifie = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")

    st.markdown("<p style='color:#999999;font-size:14px;margin-top:20px;'>Acces reserve aux decideurs</p>", unsafe_allow_html=True)
    st.stop()

# ─── Auto-refresh ───
st_autorefresh(interval=300000, key="auto_refresh")

# ─── Header ───
st.markdown(f"""
<div style="background:linear-gradient(135deg,#003366,#002244);padding:20px 28px;border-radius:0 0 12px 12px;margin:-10px -10px 20px -10px;">
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
            <span style="color:#ffffff;font-size:22px;font-weight:700;">🇲🇦 MARCHES PUBLICS MAROC</span>
            <span style="color:#f7941e;font-size:18px;font-weight:600;margin-left:12px;">Tableau de bord</span>
            <div style="height:3px;background:#f7941e;width:80px;margin:6px 0;border-radius:2px;"></div>
            <span style="color:#99c2ff;font-size:13px;">Ne ratez plus aucune opportunite IT</span>
        </div>
        <div style="text-align:right;">
            <span style="color:#ffffff;font-size:13px;">👤 Decideur</span><br>
            <span style="color:#99c2ff;font-size:11px;">📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar deconnexion ───
with st.sidebar:
    st.markdown("""
    <style>
    .sidebar-user {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 14px;
        background: linear-gradient(135deg, #003366, #002244);
        border-radius: 10px;
        margin-bottom: 16px;
        color: white;
    }
    .sidebar-user .user-icon {
        font-size: 28px;
    }
    .sidebar-user .user-info {
        flex: 1;
    }
    .sidebar-user .user-name {
        font-size: 14px;
        font-weight: 700;
        color: white;
        margin: 0;
    }
    .sidebar-user .user-role {
        font-size: 11px;
        color: #99c2ff;
        margin: 0;
    }
    .sidebar-divider {
        height: 1px;
        background: #e9ecef;
        margin: 12px 0;
    }
    .sidebar-label {
        font-size: 11px;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-user">
        <span class="user-icon">👤</span>
        <div class="user-info">
            <p class="user-name">Decideur</p>
            <p class="user-role">Connecte</p>
        </div>
        <span style="color:#28a745;font-size:10px;">●</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">Navigation</div>', unsafe_allow_html=True)

    if st.button("📊 Dashboard", use_container_width=True):
        st.markdown('<script>document.getElementById("stats").scrollIntoView({behavior:"smooth"});</script>', unsafe_allow_html=True)
    if st.button("📋 Historique", use_container_width=True):
        st.markdown('<script>document.getElementById("historique").scrollIntoView({behavior:"smooth"});</script>', unsafe_allow_html=True)
    if st.button("📋 Liste offres", use_container_width=True):
        st.markdown('<script>document.getElementById("offres").scrollIntoView({behavior:"smooth"});</script>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">Compte</div>', unsafe_allow_html=True)

    if st.button("🚪 Deconnexion", use_container_width=True):
        st.session_state.authentifie = False
        st.rerun()

# ─── Charge data ───
def charger_donnees():
    offres = Consultation.objects.select_related('acheteur', 'categorie').all()
    data = []
    for offre in offres:
        try:
            mots = ', '.join(offre.mots_cles.values_list('mot', flat=True))
        except Exception:
            mots = ''
        data.append({
            'id': offre.id,
            'reference': offre.reference,
            'objet': offre.objet[:100],
            'acheteur': offre.acheteur.nom if offre.acheteur else '',
            'date_limite': offre.date_limite,
            'lieu': offre.lieu_execution or 'Non specifie',
            'budget': offre.budget_estime or 'N/A',
            'est_informatique': offre.est_informatique,
            'est_annule': offre.est_annule,
            'categorie': offre.categorie.nom if offre.categorie else '',
            'date_publication': offre.date_publication,
            'mots_cles': mots
        })
    return pd.DataFrame(data)

df = charger_donnees()

# ─── KPIs ───
total = len(df)
it = df[df['est_informatique'] == True].shape[0]
annulees = df[df['est_annule'] == True].shape[0]
urgentes = df[df['date_limite'].notna() & (df['date_limite'] < pd.Timestamp.now(tz='UTC'))].shape[0]
it_pct = round(it/total*100, 1) if total else 0

hier = df[df['date_publication'].dt.date == (datetime.now() - timedelta(1)).date()]
total_hier = len(hier)
it_hier = hier[hier['est_informatique'] == True].shape[0] if not hier.empty else 0

st.markdown('<div id="stats" class="section-title">Statistiques generales</div>', unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div style="background:#fff;border-radius:12px;padding:20px;border-left:4px solid #003366;box-shadow:0 2px 10px rgba(0,0,0,0.06);">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div><span style="color:#666;font-size:13px;">📄 Total offres</span><br>
            <span style="color:#003366;font-size:28px;font-weight:700;">{total}</span></div>
        </div>
        <span style="color:#28a745;font-size:12px;">🟢 +{total_hier} vs hier</span>
    </div>""", unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div style="background:#fff;border-radius:12px;padding:20px;border-left:4px solid #28a745;box-shadow:0 2px 10px rgba(0,0,0,0.06);">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div><span style="color:#666;font-size:13px;">💻 Offres IT</span><br>
            <span style="color:#003366;font-size:28px;font-weight:700;">{it}</span>
            <span style="color:#28a745;font-size:13px;margin-left:6px;">({it_pct}%)</span></div>
        </div>
        <span style="color:#28a745;font-size:12px;">🟢 +{it_hier} vs hier</span>
    </div>""", unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div style="background:#fff;border-radius:12px;padding:20px;border-left:4px solid #dc3545;box-shadow:0 2px 10px rgba(0,0,0,0.06);">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div><span style="color:#666;font-size:13px;">❌ Annulees</span><br>
            <span style="color:#003366;font-size:28px;font-weight:700;">{annulees}</span></div>
        </div>
    </div>""", unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div style="background:#fff;border-radius:12px;padding:20px;border-left:4px solid #f7941e;box-shadow:0 2px 10px rgba(0,0,0,0.06);">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div><span style="color:#666;font-size:13px;">⏰ Urgentes</span><br>
            <span style="color:#003366;font-size:28px;font-weight:700;">{urgentes}</span></div>
        </div>
        <span style="color:#f7941e;font-size:12px;">🟠 {round(urgentes/total*100) if total else 0}% des offres</span>
    </div>""", unsafe_allow_html=True)

# ─── Banner alerte ───
ajd = df[df['date_limite'].dt.date == date.today()]
it_ajd = ajd[ajd['est_informatique'] == True].shape[0]
if not ajd.empty:
    taux_ajd = round(it_ajd/len(ajd)*100) if len(ajd) > 0 else 0
    st.markdown(f"""
    <div style="background:#fff5e6;border:1px solid #f7941e;border-radius:10px;padding:16px 20px;margin:16px 0;">
        <span style="color:#003366;font-weight:700;">Nouvelles offres aujourd'hui :</span>
        <span style="color:#003366;">{len(ajd)} offres</span> |
        <span style="color:#f7941e;font-weight:700;">{it_ajd} offres IT</span> |
        <span style="color:#28a745;font-weight:700;">{taux_ajd}% de taux IT</span>
        <br><span style="color:#999;font-size:12px;">Derniere mise a jour : {datetime.now().strftime('%d/%m/%Y a %H:%M')}</span>
    </div>""", unsafe_allow_html=True)

# ─── Filtres ───
st.markdown('<div class="section-title">🔍 Filtres</div>', unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    filtre_it = st.selectbox("🏢 Secteur", ["Tous", "IT", "Non-IT"])
with col_f2:
    regions = ["Toutes"] + sorted(df['lieu'].unique().tolist())
    filtre_region = st.selectbox("📍 Region", regions)
with col_f3:
    categories = ["Toutes"] + sorted(df['categorie'].unique().tolist())
    filtre_categorie = st.selectbox("🏷️ Categorie", categories)

col_f4, col_f5, col_f6 = st.columns([2, 1, 1])
with col_f4:
    recherche = st.text_input("", placeholder="🔎 Rechercher par reference, objet, acheteur...", label_visibility="collapsed")
with col_f5:
    date_min = df['date_limite'].min().date() if pd.notna(df['date_limite'].min()) else date.today()
    date_max = df['date_limite'].max().date() if pd.notna(df['date_limite'].max()) else date.today()
    date_debut = st.date_input("Du", value=date_min, min_value=date_min, max_value=date_max)
with col_f6:
    date_fin = st.date_input("Au", value=date_max, min_value=date_min, max_value=date_max)

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

# ─── Graphiques ───
st.markdown('<div class="section-title">Graphiques</div>', unsafe_allow_html=True)

col_g1, col_g2 = st.columns(2)
with col_g1:
    st.markdown("**Offres par mois**")
    if not df_filtre.empty:
        offres_par_mois = df_filtre.groupby(df_filtre['date_limite'].dt.to_period('M')).size()
        offres_par_mois.index = offres_par_mois.index.astype(str)
        st.bar_chart(offres_par_mois, use_container_width=True)
with col_g2:
    st.markdown("**Top 10 regions**")
    if not df_filtre.empty:
        top_reg = df_filtre.groupby('lieu').size().reset_index(name='count')
        top_reg = top_reg.sort_values('count', ascending=False).head(10)
        st.bar_chart(top_reg.set_index('lieu'))

col_g3, col_g4 = st.columns(2)
with col_g3:
    st.markdown("**Par categorie**")
    if not df_filtre.empty:
        cats = df_filtre.groupby('categorie').size().reset_index(name='count')
        st.bar_chart(cats.set_index('categorie'))
with col_g4:
    st.markdown("**IT vs Non-IT**")
    if not df_filtre.empty:
        it_vs = df_filtre['est_informatique'].value_counts().reset_index()
        it_vs.columns = ['type', 'count']
        it_vs['type'] = it_vs['type'].map({True: 'IT', False: 'Non-IT'})
        st.bar_chart(it_vs.set_index('type'))

st.markdown('<div class="section-title">Mots-cles les plus utilises (offres IT)</div>', unsafe_allow_html=True)
if not df_filtre.empty:
    IT_df = df_filtre[df_filtre['est_informatique'] == True].copy()
    mots_series = IT_df['mots_cles'].str.split(',\s*').explode().str.strip()
    mots_series = mots_series[mots_series != '']
    if not mots_series.empty:
        top_mots = mots_series.value_counts().head(10)
        top_mots = top_mots.sort_values(ascending=True)
        st.bar_chart(top_mots, use_container_width=True, height=350)
        st.caption(", ".join([f"**{m}**: {c}" for m, c in top_mots.items()]))
    else:
        st.info("Aucun mot-cle associe aux offres IT filtrees")
else:
    st.info("Aucune offre IT dans la selection")

# ─── Historique + acheteurs ───
col_h1, col_h2 = st.columns(2)
with col_h1:
    st.markdown('<div id="historique" class="section-title">Historique des scrapings</div>', unsafe_allow_html=True)
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
with col_h2:
    st.markdown('<div class="section-title">Top 10 acheteurs</div>', unsafe_allow_html=True)
    if not df_filtre.empty:
        acheteurs = df_filtre.groupby('acheteur').size().reset_index(name='count')
        acheteurs = acheteurs.sort_values('count', ascending=False).head(10)
        st.bar_chart(acheteurs.set_index('acheteur'))

# ─── Urgentes ───
if not df_filtre.empty:
    maintenant = pd.Timestamp.now(tz='UTC')
    u = df_filtre[df_filtre['date_limite'].notna() & (df_filtre['date_limite'] < maintenant)]
    if not u.empty:
        st.markdown('<div class="section-title">⏰ Offres depassees</div>', unsafe_allow_html=True)

        u_par_jour = u.groupby(u['date_limite'].dt.date).size().reset_index(name='nombre')
        u_par_jour.columns = ['Date', 'Nombre']
        u_par_jour = u_par_jour.sort_values('Date', ascending=False).head(15)

        st.bar_chart(u_par_jour.set_index('Date'), use_container_width=True, height=300)

        col_u1, col_u2, col_u3 = st.columns(3)
        col_u1.metric("Total depassees", len(u))
        col_u2.metric("IT depassees", u[u['est_informatique']==True].shape[0])
        col_u3.metric("Derniere depassee", u['date_limite'].max().strftime('%d/%m/%Y') if not u.empty else "N/A")
        st.caption(f"Mise a jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Auto-refresh 5 min")

# ─── Tableau ───
st.markdown('<div id="offres" class="section-title">📋 Liste des offres</div>', unsafe_allow_html=True)
cols_aff = ['id', 'reference', 'objet', 'acheteur', 'lieu', 'date_limite', 'budget', 'est_informatique', 'est_annule', 'categorie', 'mots_cles']
df_aff = df_filtre[cols_aff].copy()
df_aff.columns = ['ID', 'Reference', 'Objet', 'Acheteur', 'Lieu', 'Date limite', 'Budget', 'IT', 'Annule', 'Categorie', 'Mots-cles']

def color_row(row):
    if row['Annule'] == ' Oui':
        return ['background-color: #fce4ec'] * len(row)
    elif row['IT'] == ' IT':
        return ['background-color: #e8f5e9'] * len(row)
    return [''] * len(row)

df_aff_val = df_aff.copy()
df_aff_val['IT'] = df_aff_val['IT'].map({True: '🟢 IT', False: ''})
df_aff_val['Annule'] = df_aff_val['Annule'].map({True: '🔴 Annule', False: ''})
df_aff_val['Date limite'] = df_aff_val['Date limite'].dt.strftime('%d/%m/%Y %H:%M')

st.dataframe(df_aff_val.style.apply(color_row, axis=1), use_container_width=True, height=500)

st.markdown(f"<p style='color:#666;font-size:13px;'>📊 {len(df_filtre)} resultat(s)</p>", unsafe_allow_html=True)

# Export
try:
    import io
    buffer = io.BytesIO()
    df_excel = df_filtre[cols_aff].copy()
    for col in df_excel.select_dtypes(include=['datetimetz']).columns:
        df_excel[col] = df_excel[col].dt.tz_localize(None)
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_excel.to_excel(writer, index=False, sheet_name='Offres')
    st.download_button(label="Telecharger (Excel)", data=buffer.getvalue(), file_name='offres_marches_publics.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
except ImportError:
    csv = df_filtre.to_csv(index=False, sep=';', encoding='utf-8-sig')
    st.download_button(label="Telecharger (CSV)", data=csv.encode('utf-8-sig'), file_name='offres_marches_publics.csv', mime='text/csv', use_container_width=True)

# ─── Footer ───
st.markdown("""
<div style="background:#003366;padding:16px 28px;border-radius:12px 12px 0 0;margin:24px -10px -10px -10px;text-align:center;">
    <span style="color:#99c2ff;font-size:12px;">© 2026 - Plateforme de veille des marches publics</span><br>
    <span style="color:#f7941e;font-size:11px;">🔒 Donnees securisees - Mise a jour automatique</span>
</div>
""", unsafe_allow_html=True)
