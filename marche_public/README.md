# Plateforme de veille des marchés publics

## Semaine 1 - Conception et base de données

**Auteur :** Oumaima Inejjarn 
**Date :** 1 Juillet 2026  

---

## Description du projet

Ce projet consiste à développer un outil automatisé pour surveiller les appels d'offres publiés sur le portail marocain des marchés publics.

**Objectif :** Identifier les opportunités dans le secteur IT et alerter les décideurs en temps réel.

---

## Diagrammes UML

### 1. Use Case

![Use Case](images/use_case.png)
### 2. Diagramme de Classe

![Diagramme de Classe](images/diagramme_classe.png)

---

### 3. Diagramme de Séquence
#### Scénario 1 : Scraping complet

![Scénario 1 - Scraping](images/sequence_scenario1.png)

---

#### Scénario 2 : Consultation du dashboard

![Scénario 2 - Dashboard](images/sequence_scenario2.png)

---

#### Scénario 3 : Envoi d'alerte

![Scénario 3 - Alerte](images/sequence_scenario3.png)

---

## Structure de la base de données

**Total : 17 tables**
 **SGBD :** PostgreSQL
- **7 tables** pour l'application (Consultation, ResultatAvisAchat, Organisme, MotCle, Alerte, Configuration, HistoriqueScraping)
- **10 tables** pour Django (auth_user, auth_group, etc.)

---

## Technologies utilisées

| Technologie | Version | Utilité |
|-------------|---------|---------|
| Python | 3.12 | Langage principal |
| Django | 5.0.6 | Framework web |
| PostgreSQL | 17 | Base de données |






