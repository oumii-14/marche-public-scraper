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

```

### 1. Fonctions principales

## 🤖 Fonctions du scraper (scrape.py)

Le scraper est composé de **11 fonctions** qui travaillent ensemble pour automatiser l'extraction des offres.

---

### Tableau des fonctions

11 fonctions organisées en 5 catégories :

1. INITIALISATION
   creer_mots_cles() → Crée les 18 mots-clés IT en base

2. EXTRACTION
   extraire_toutes_offres() → Découpe le texte en offres
   extraire_donnees_offre() → Extrait Référence, Objet, Acheteur, Lieu, Budget
   extraire_liens_offres() → Trouve les liens de détail
   extraire_budget_simple() → Cherche le budget dans le texte
   extraire_budget_depuis_detail() → Budget depuis la page de détail

3. CLASSIFICATION
   detecter_categorie_simple() → Classe l'offre (Travaux, Fournitures, Services)
   get_ou_creer_categorie() → Gère les catégories en base

4. GESTION DES DONNÉES
   get_ou_creer_organisme() → Gère les organismes acheteurs
   enregistrer_offre() → 	Sauvegarde en base avec vérification des doublons

5. ORCHESTRATION
   scraper_consultations() → Fonction principale qui pilote tout

ORDRE D'EXÉCUTION :
scraper_consultations() → Navigation → Extraction → Classification → Enregistrement → Pagination → Fin

---
   # remplissage des tables (TEST)
Table        	Rôle              	Nombre	
Consultation	Offres scrapées	    563	
Organisme	   Acheteurs publics   	 545	
Categorie    	Catégories	           3	(Service\Fournitures\travaux)
MotCle	      Mots-clés IT           18	

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
      admin / mdp: admin123

# 6. Lancer le scraper
python scraper/scrape.py


```
## Technologies

| Technologie | Version | Rôle |
|-------------|---------|------|
| Python | 3.12 | Langage principal |
| Django | 6.0.6 | Framework web / ORM |
| PostgreSQL | 17 | Base de données |
| Selenium | 4.45.0 | Scraping navigateur | (POUR PLAWRIGHT J AVAIT UN PROB D INSTALLATION)
| ChromeDriver | — | Pilote Chrome |


## 📧 Module d'Analyse et Alerte (Semaine 3)

### 🔍 Filtrage par mots-clés

Le système détecte automatiquement les offres IT à l'aide de **18 mots-clés** :

```python
'informatique', 'logiciel', 'pc', 'développement', 'numérique',
'digitalisation', 'serveur', 'cloud', 'réseau', 'télécom',
'cybersécurité', 'données', 'site web', 'application', 'erp',
'infrastructure', 'sécurité informatique', 'programmation'

Mots-clés associés aux offres via la table Consultation.mots_cles

📧 Alertes emails
Le script scraper/alertes.py vérifie quotidiennement les nouvelles offres IT et envoie un email récapitulatif au décideur.

Fonctionnement :

Vérifie les offres IT sans alerte

Construit un email récapitulatif

Envoie l'email via SMTP (Gmail)

Enregistre l'alerte dans la table Alerte

Configuration SMTP :

python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tonemail@gmail.com'
EMAIL_HOST_PASSWORD = 'motdepasse'
DEFAULT_FROM_EMAIL = 'tonemail@gmail.com'
Exemple d'email reçu :

text
📋 RÉCAPITULATIF DES OFFRES IT

🔹 Référence : TEST-IT-002
   Objet : Développement d'une application mobile...
   Acheteur : Commune IZEMMOUREN
   Date limite : 31/12/2026 14:00
   Lieu : Casablanca
   Budget : 250 000 MAD
   Mots-clés : développement, application, digitalisation

🔗 Consultez le dashboard pour plus d'informations.




