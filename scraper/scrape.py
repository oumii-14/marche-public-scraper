"""
Module de Collecte - Scraper (Version finale Semaine 2)
Extraction automatique, pagination complète
"""

import os
import sys
import django
import re
import time
import unicodedata
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marche_public.settings')
django.setup()

from scraper.models import Consultation, Organisme, Categorie, MotCle, HistoriqueScraping, Configuration
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_mots_cles():
    """Récupère la liste dynamique des mots-clés depuis la base de données"""
    return [m.mot.lower() for m in MotCle.objects.all()]


# ============================================================
# FONCTIONS D'EXTRACTION
# ============================================================
def extraire_budget_simple(texte):
    """Extrait le budget du texte"""
    if not texte:
        return None
    patterns = [
        r'Budget\s*:?\s*([\d\s.,]+)\s*(?:MAD|DH)',
        r'Estimation\s*:?\s*([\d\s.,]+)\s*(?:MAD|DH)',
        r'Montant\s*:?\s*([\d\s.,]+)\s*(?:MAD|DH)',
        r'([\d\s.,]+)\s*(?:MAD|DH)',
    ]
    for pattern in patterns:
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            val = match.group(1).strip()
            if val.count(',') > 1 or val.count(' ') > 2:
                continue
            return val
    return None


def extraire_categorie_depuis_detail(driver, url_offre):
    """Va sur la page de détail, récupère la catégorie et le budget"""
    if not url_offre:
        return None, None
    try:
        driver.execute_script("window.open(arguments[0]);", url_offre)
        time.sleep(0.5)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(1)
        body = driver.find_element(By.TAG_NAME, "body").text

        # Extraire la catégorie depuis le body
        cat_match = re.search(r'Catégorie\s*principale\s*:?\s*([^\n]+)', body)
        categorie = cat_match.group(1).strip() if cat_match else None

        # Extraire le budget
        budget = extraire_budget_simple(body)

        if budget or categorie:
            print(f"      [DÉTAIL] catégorie={categorie}, budget={budget}")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return categorie, budget
    except Exception as e:
        print(f"      [DÉTAIL] Erreur: {e}")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return None, None


def extraire_liens_offres(driver):
    """Extrait les liens vers les pages de détail des offres"""
    url_courante = driver.current_url
    liens = []
    try:
        tous = driver.find_elements(By.TAG_NAME, "a")
        for elem in tous:
            href = (elem.get_attribute("href") or "").strip()
            if not href or href == url_courante or href.startswith("#"):
                continue
            href_lower = href.lower()
            if "/afficher/" in href_lower or "/show/" in href_lower:
                if href not in liens:
                    liens.append(href)
        if not liens:
            for elem in tous:
                href = (elem.get_attribute("href") or "").strip()
                if not href or href == url_courante or href.startswith("#"):
                    continue
                href_lower = href.lower()
                if "/consultation/" in href_lower and href_lower != url_courante.lower():
                    if href not in liens:
                        liens.append(href)
    except Exception as e:
        print(f"   [LIENS] Erreur: {e}")
    return liens


def get_ou_creer_categorie(nom_categorie):
    """Récupère ou crée une catégorie"""
    if not nom_categorie:
        return None
    # Normalise le nom : "Services" -> "SERVICES", "Travaux" -> "TRAVAUX", "Fournitures" -> "FOURNITURES"
    for key, label in Categorie.NOM_CHOICES:
        if label.lower() == nom_categorie.lower():
            nom_categorie = key
            break
    cat, _ = Categorie.objects.get_or_create(
        nom=nom_categorie,
        defaults={'description': nom_categorie}
    )
    return cat


def get_ou_creer_organisme(nom, ville=None):
    """Récupère ou crée un organisme"""
    if not nom:
        return None
    nom = nom.strip()[:200]
    defaults = {'nom': nom, 'type': 'ACHETEUR'}
    if ville:
        defaults['ville'] = ville.strip()[:100]
    org, _ = Organisme.objects.get_or_create(
        nom__iexact=nom,
        defaults=defaults
    )
    if ville and not org.ville:
        org.ville = ville.strip()[:100]
        org.save()
    return org


def extraire_donnees_offre(texte_offre):
    """Extrait les données d'une offre depuis le texte"""
    try:
        texte_offre = unicodedata.normalize('NFC', texte_offre)
        ref = re.search(r'[Rr][ée]f[ée]rence\s*:\s*([^\n]+)', texte_offre)
        reference = ref.group(1).strip() if ref else None

        obj = re.search(r'Objet\s*:\s*([^\n]+)', texte_offre)
        objet = obj.group(1).strip() if obj else None

        ach = re.search(r'Acheteur\s*:\s*([^\n]+)', texte_offre)
        acheteur = ach.group(1).strip() if ach else None

        lieu = re.search(r"Lieu\s*d[ei']\s*ex[ée]cution\s*\n\s*([^\n]+)", texte_offre)
        lieu_exec = lieu.group(1).strip() if lieu else None

        budget = extraire_budget_simple(texte_offre)

        date_limite = datetime.now()
        date_match = re.search(r'Date\s*limite\s*de\s*remise\s*des\s*devis\s*\n\s*(\d{2}/\d{2}/\d{4})\s*\n\s*(\d{2}:\d{2})', texte_offre)
        if date_match:
            try:
                from django.utils import timezone
                date_limite = datetime.strptime(f"{date_match.group(1)} {date_match.group(2)}", '%d/%m/%Y %H:%M')
                date_limite = timezone.make_aware(date_limite) if timezone.is_naive(date_limite) else date_limite
            except:
                pass

        est_it = False
        if objet:
            mots = get_mots_cles()
            est_it = any(mot in objet.lower() for mot in mots) if mots else False

        est_annule = 'annul' in texte_offre.lower()

        return {
            'reference': reference,
            'objet': objet,
            'acheteur': acheteur,
            'lieu_execution': lieu_exec,
            'budget_estime': budget,
            'date_limite': date_limite,
            'est_informatique': est_it,
            'est_annule': est_annule
        }
    except Exception:
        return None


def extraire_toutes_offres(texte):
    """Extrait toutes les offres du texte"""
    texte = unicodedata.normalize('NFC', texte)
    lignes = texte.split('\n')
    offres = []
    courant = []
    for ligne in lignes:
        ligne = ligne.strip()
        if re.match(r'[Rr][ée]f[ée]rence\s*:', ligne):
            if courant:
                offres.append('\n'.join(courant))
            courant = [ligne]
        elif courant:
            courant.append(ligne)
    if courant:
        offres.append('\n'.join(courant))
    return [o for o in offres if 'Objet' in o and 'Acheteur' in o]


def enregistrer_offre(donnees, driver=None, url_detail=None):
    """Enregistre une offre dans la base"""
    try:
        if not donnees or not donnees['reference'] or not donnees['objet']:
            return False

        ref = donnees['reference'][:100]
        if Consultation.objects.filter(reference=ref).exists():
            print(f"   [SKIP] {ref} existe déjà")
            return False

        acheteur = get_ou_creer_organisme(donnees['acheteur'], donnees.get('lieu_execution'))
        if not acheteur:
            return False

        # Par défaut : catégorie et budget depuis les données de la liste
        categorie_nom = None
        budget = donnees['budget_estime']

        # Si on a l'url de détail, on va chercher catégorie et budget sur la page
        if driver and url_detail:
            cat_from_detail, bud_from_detail = extraire_categorie_depuis_detail(driver, url_detail)
            if cat_from_detail:
                categorie_nom = cat_from_detail
            if bud_from_detail:
                budget = bud_from_detail

        # Fallback si on n'a pas pu récupérer la catégorie depuis le détail
        if not categorie_nom:
            # extraire depuis l'objet du listing
            if "Travaux" in donnees.get('objet', '') or "travaux" in donnees.get('objet', '').lower():
                categorie_nom = "TRAVAUX"
            elif "Fourniture" in donnees.get('objet', ''):
                categorie_nom = "FOURNITURES"
            else:
                categorie_nom = "SERVICES"

        categorie = get_ou_creer_categorie(categorie_nom)

        if budget and len(str(budget)) > 50:
            budget = str(budget)[:50]

        consultation = Consultation.objects.create(
            reference=ref,
            objet=donnees['objet'][:500],
            acheteur=acheteur,
            date_limite=donnees.get('date_limite', datetime.now()),
            lieu_execution=(donnees['lieu_execution'] or "Non spécifié")[:100],
            budget_estime=budget,
            est_informatique=donnees['est_informatique'],
            est_annule=donnees.get('est_annule', False),
            categorie=categorie,
        )

        if donnees.get('est_informatique') and donnees.get('objet'):
            mots = get_mots_cles()
            mots_trouves = [m for m in mots if m in donnees['objet'].lower()]
            if mots_trouves:
                mots_qs = MotCle.objects.filter(mot__in=mots_trouves)
                consultation.mots_cles.add(*mots_qs)

        print(f"   [OK] {ref} ajoutée (Cat: {categorie_nom}, IT: {donnees['est_informatique']}, Budget: {budget or 'N/A'})")
        return True
    except Exception as e:
        print(f"   [ERREUR] Insertion: {e}")
        return False


# ============================================================
# SCRAPER PRINCIPAL (AVEC PAGES DE DÉTAIL ET PAGINATION ROBUSTE)
# ============================================================
def scraper_consultations():
    print("=" * 60)
    print("  SCRAPER - MARCHÉS PUBLICS")
    print("=" * 60)

    MOTS_CLES_IT = get_mots_cles()  # dynamique depuis la base
    print(f"   [OK] {len(MOTS_CLES_IT)} mots-clés en base")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    total = 0
    total_offres = 0
    page_num = 1
    erreur = None

    try:
        driver.get("https://www.marchespublics.gov.ma/bdc/entreprise/consultation/")
        time.sleep(3)

        while True:
            print(f"\n--- Page {page_num} ---")

            body = driver.find_element(By.TAG_NAME, "body").text
            offres = extraire_toutes_offres(body)
            total_offres += len(offres)
            print(f"   {len(offres)} offre(s) détectée(s)")

            liens_detail = extraire_liens_offres(driver)
            print(f"   {len(liens_detail)} lien(s) de détail trouvé(s)")

            for idx, offre in enumerate(offres):
                donnees = extraire_donnees_offre(offre)
                if donnees:
                    url_detail = None
                    if idx < len(liens_detail):
                        url_detail = liens_detail[idx]
                    
                    if enregistrer_offre(donnees, driver, url_detail):
                        total += 1

            # ============================================
            # PAGINATION ROBUSTE (4 méthodes)
            # ============================================
            suivant = None
            
            # Méthode 1 : XPATH "Suivant"
            try:
                suivant = driver.find_element(By.XPATH, "//a[contains(text(), 'Suivant')]")
            except:
                pass
            
            # Méthode 2 : CSS pagination-next
            if not suivant:
                try:
                    suivant = driver.find_element(By.CSS_SELECTOR, ".pagination-next a, .next a, .page-item.next a")
                except:
                    pass
            
            # Méthode 3 : Tous les liens
            if not suivant:
                try:
                    tous_liens = driver.find_elements(By.TAG_NAME, "a")
                    for lien in tous_liens:
                        if 'Suivant' in lien.text or 'suivant' in lien.text.lower():
                            suivant = lien
                            break
                except:
                    pass
            
            # Méthode 4 : icône chevron/flèche droite
            if not suivant:
                try:
                    suivant = driver.find_element(By.CSS_SELECTOR, "a[rel='next'], .fa-chevron-right, .glyphicon-chevron-right, i.fa-angle-right")
                except:
                    pass
            
            if suivant:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true); window.scrollBy(0, -200);", suivant)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", suivant)
                    time.sleep(2)
                    page_num += 1
                    print(f"   [PAGINATION] Page {page_num}")
                except Exception as e:
                    print(f"   [PAGINATION] Erreur clic: {e}")
                    break
            else:
                print("   [INFO] Fin de pagination")
                break
            
            # Sécurité : ne pas dépasser 150 pages
            if page_num > 150:
                print("   [INFO] Limite de 150 pages atteinte")
                break

    except Exception as e:
        erreur = str(e)
        print(f"   [ERREUR] {e}")

    finally:
        driver.quit()

    # Enregistrer l'historique du scraping
    nb_it = Consultation.objects.filter(est_informatique=True).count()
    config = Configuration.objects.first()
    HistoriqueScraping.objects.create(
        nb_consultations=total_offres,
        nb_resultats=0,
        nb_offres_it=nb_it,
        statut=erreur or "Succès",
        configuration=config,
    )

    print("\n" + "=" * 60)
    print(f"  TERMINÉ : {total} nouvelle(s) offre(s) ajoutée(s)")
    print(f"  Total en base : {Consultation.objects.count()} offres")
    print(f"  Offres IT : {Consultation.objects.filter(est_informatique=True).count()}")
    print("=" * 60)


if __name__ == "__main__":
    scraper_consultations()