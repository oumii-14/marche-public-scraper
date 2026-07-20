# Plateforme de veille des marchés publics

Outil automatisé de surveillance des appels d'offres publiés sur `marchespublics.gov.ma`, avec détection des opportunités IT et alertes en temps réel.

---

## Semaine 1 — Conception et base de données ✅

### 1. Use Case

![Use Case](images/use_case.png)

### 2. Diagramme de Classe

![Diagramme de Classe](images/dclasse.png)

### 3. Diagrammes de Séquence

**Scénario 1 — Scraping automatique**

![Scénario 1](images/sequence_scenario1.png)

**Scénario 2 — Analyse et Alerte des offres IT**

![Scénario 2](images/sequence_scenario2.png)

**Scénario 3 — Visualisation et Dashboard**

![Scénario 3](images/sequence_scenario3.png)

### 4. Base de données

| Élément | Valeur |
|---------|--------|
| SGBD | PostgreSQL 17 |
| Base | `marche_public` |
| Tables applicatives | 7 (Consultation, Organisme, Categorie, MotCle, Alerte, Configuration, HistoriqueScraping) |
| Tables Django | 10 |

---

## Semaine 2 — Développement du scraper

### 1. Fonctions principales

## 🤖 Fonctions du scraper (scrape.py)

Le scraper est composé de **11 fonctions** qui travaillent ensemble pour automatiser l'extraction des offres.

---

### Tableau des fonctions

11 fonctions organisées en 5 catégories :

1. INITIALISATION
   get_mots_cles() → Récupère les mots-clés dynamiquement depuis la base MotCle

2. EXTRACTION
   extraire_toutes_offres() → Découpe le texte en offres
   extraire_donnees_offre() → Extrait Référence, Objet, Acheteur, Lieu, Budget
   extraire_liens_offres() → Trouve les liens de détail
   extraire_budget_simple() → Cherche le budget dans le texte
   extraire_categorie_depuis_detail() → Budget + Catégorie depuis la page de détail

3. CLASSIFICATION
   get_ou_creer_categorie() → Gère les catégories en base (normalise Travaux/Fournitures/Services)

4. GESTION DES DONNÉES
   get_ou_creer_organisme() → Gère les organismes acheteurs
   enregistrer_offre() → Sauvegarde en base avec vérification des doublons

5. ORCHESTRATION
   scraper_consultations() → Fonction principale qui pilote tout

ORDRE D'EXÉCUTION :
scraper_consultations() → Navigation → Extraction → Classification via page détail → Enregistrement → Pagination → Fin

---

| Table         | Rôle                  | Nombre  |
|---------------|-----------------------|---------|
| Consultation  | Offres scrapées       | 563     |
| Organisme     | Acheteurs publics     | 545     |
| Categorie     | Catégories            | 3       |
| MotCle        | Mots-clés IT          | 19      |

---

## Démarrage rapide

```bash
# 1. Cloner
git clone https://github.com/oumii-14/marche-public-scraper.git
cd marche-public-scraper

# 2. Environnement virtuel
python -m venv venv
venv\Scripts\activate

# 3. Dépendances
pip install -r requirements.txt

# 4. Base de données
psql -U postgres -c "CREATE DATABASE marche_public;"
python manage.py migrate

# 5. Admin
python manage.py createsuperuser
# admin / mdp: admin123

# 6. Lancer le scraper
python scraper/scrape.py
```

## Technologies

| Technologie | Version | Rôle |
|-------------|---------|------|
| Python | 3.12 | Langage principal |
| Django | 6.0.6 | Framework web / ORM |
| PostgreSQL | 17 | Base de données |
| Selenium | 4.45.0 | Scraping navigateur |
| ChromeDriver | — | Pilote Chrome |
| Streamlit | — | Dashboard interactif |
| streamlit-autorefresh | — | Auto-refresh du dashboard |

---

## Semaine 3 — Module d'Analyse et Alerte

### 📧 Alertes emails

Le script `scraper/alertes.py` vérifie quotidiennement les nouvelles offres IT et envoie un email récapitulatif au décideur.

Fonctionnement :

1. Vérifie les offres IT sans alerte
2. Construit un email récapitulatif (tableau HTML)
3. Envoie l'email via SMTP (Gmail)
4. Enregistre l'alerte dans la table Alerte
5. Lien direct vers le dashboard : `http://192.168.1.8:8501`

Configuration SMTP :

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tonemail@gmail.com'
EMAIL_HOST_PASSWORD = 'motdepasse'
DEFAULT_FROM_EMAIL = 'tonemail@gmail.com'
```

---

## Semaine 4 — Dashboard & Automatisation

### Mots-clés dynamiques

Les mots-clés ne sont plus écrits en dur dans le code. Le décideur peut les ajouter/supprimer/modifier via `/admin/scraper/motcle/`. Le scraper lit automatiquement la liste mise à jour à chaque lancement via `get_mots_cles()`.

### Catégorie extraite depuis la page de détail

La catégorie (Travaux/Fournitures/Services) est lue directement depuis le champ `Catégorie principale` de la page de détail de chaque offre sur le site.

### Dashboard Streamlit

Visualisation interactive des offres avec graphiques et filtres. **Temps réel** — se rafraîchit automatiquement toutes les 5 minutes.

**Démarrage automatique au boot Windows :**

```bash
# Le dashboard démarre automatiquement au démarrage du PC
# via : shell:startup\start_dashboard.bat
```

**Accès :** `http://192.168.1.8:8501`

### Authentification

Le dashboard est protégé par un mot de passe. Le login s'affiche avec un style épuré inspiré du site marchespublics.gov.ma (bleu marine + orange).

```python
MOT_DE_PASSE = "marche2026"
```

### Navigation Sidebar

Le dashboard propose **3 vues** navigables depuis la sidebar :

| Vue | Description |
|-----|-------------|
| 📊 Dashboard | KPIs, banner offres IT du jour, résumé rapide |
| 📈 Graphiques | Offres par mois, régions, catégories, IT vs Non-IT, mots-clés, offres dépassées, top acheteurs |
| 📋 Liste des offres | Tableau interactif avec badges (IT/Annulé), export Excel |

Chaque vue a un bouton **⬅️ Retour au Dashboard** pour naviguer facilement.

### Filtres complets (dans les 3 vues)

| Filtre | Options |
|--------|---------|
| 🏢 Secteur | Tous / IT / Non-IT |
| 📍 Région | Liste dynamique |
| 🏷️ Catégorie | Liste dynamique |
| 🔎 Recherche | Par référence, objet, acheteur |
| 📅 Dates | Plage Du / Au |

### SQL brut pour les mots-clés

Le champ ManyToMany Django (`mots_cles`) contient un bug (`FieldDoesNotExist`). Les mots-clés sont chargés via une requête SQL brute contournant l'ORM :

```python
cursor.execute("""
    SELECT scm.consultation_id, mk.mot
    FROM scraper_consultation_mots_cles scm
    JOIN scraper_motcle mk ON scm.motcle_id = mk.id
""")
```

### Historique de scraping

Chaque exécution du scraper enregistre un historique dans la table `HistoriqueScraping` : date, nombre d'offres trouvées, nombre d'offres IT, statut (Succès/Erreur). Visible dans `/admin/scraper/historiquescraping/`. L'heure affichée est en heure Maroc (UTC+1).

### Détection IT avec word boundaries

La détection des offres IT utilise des **expressions régulières avec word boundaries** (`\b`) pour éviter les faux positifs. Par exemple, "informatique" ne matche pas "fournitures" mais matche "ACHAT DE MATÉRIEL INFORMATIQUE".

```python
est_it = any(re.search(r'\b' + re.escape(mot) + r'\b', objet_lower) for mot in mots)
```

### Script de recalcul IT

Un script `scraper/recaler_it.py` permet de recalculer `est_informatique` et `mots_cles` pour toutes les offres en base :

```bash
python scraper/recaler_it.py
```

### Banner offres IT du jour (Dashboard)

Le dashboard affiche un banner en haut avec :
- Nombre d'offres IT trouvées aujourd'hui
- Nombre total d'offres IT en base
- Heure de la dernière alerte email
- Bouton pour voir la liste des offres IT du jour

### Détection des annulations

Après chaque scraping, le script vérifie les offres existantes en base. Si le texte de l'offre contient "annul", le champ `est_annule` est mis à jour automatiquement. Ainsi les offres annulées sur le site sont reflétées dans le dashboard.

### Automatisation (Task Scheduler)

| Tâche | Heure | Fichier |
|-------|-------|---------|
| Scraper + Alertes | 10:00 | `scraper/run_all.bat` |

```bash
taskschd.msc  # Planificateur de tâches Windows
```

### Démarrage manuel du dashboard

```bash
streamlit run dashboard_app.py --server.address 0.0.0.0 --server.port 8501
```

Ou via le script :

```bash
scraper/start_dashboard.bat
```

---

### ✅ Résultats

- Dashboard opérationnel avec authentification (auto-démarrage au boot)
- 3 vues navigables : Dashboard, Graphiques, Liste des offres
- Accès via `http://192.168.1.8:8501` (PC et téléphone)
- Graphiques interactifs
- Filtres complets dans toutes les vues
- Mots-clés dynamiques (modifiables via admin)
- Catégorie extraite depuis le site
- Historique de scraping automatique
- Automatisation configurée (une seule tâche à 10h00)
- Emails HTML avec lien direct vers le dashboard
- Projet prêt pour la production
