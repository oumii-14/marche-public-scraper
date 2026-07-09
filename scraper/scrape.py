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

from scraper.models import Consultation, Organisme, Categorie, MotCle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ============================================================
# CONSTANTES
# ============================================================
MOTS_CLES_IT = ['informatique', 'logiciel', 'pc', 'développement', 'numérique',
                'digitalisation', 'serveur', 'cloud', 'réseau', 'télécom',
                'cybersécurité', 'données', 'site web', 'application', 'erp',
                'infrastructure', 'sécurité informatique', 'programmation']


def creer_mots_cles():
    """Crée les mots-clés IT en base s'ils n'existent pas"""
    for mot in MOTS_CLES_IT:
        MotCle.objects.get_or_create(mot=mot)
    print(f"   [OK] {MotCle.objects.count()} mots-clés en base")


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


def extraire_budget_depuis_detail(driver, url_offre):
    """Va sur la page de détail d'une offre et récupère le budget, puis revient"""
    if not url_offre:
        return None
    try:
        print(f"      [DÉTAIL] Récupération du budget...")
        driver.execute_script("window.open(arguments[0]);", url_offre)
        time.sleep(0.5)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(1)
        body = driver.find_element(By.TAG_NAME, "body").text
        budget = extraire_budget_simple(body)
        if budget:
            print(f"      [DÉTAIL] Budget trouvé: {budget}")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return budget
    except Exception as e:
        print(f"      [DÉTAIL] Erreur: {e}")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return None


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


def detecter_categorie_simple(objet):
    """Détecte la catégorie à partir de l'objet"""
    if not objet:
        return "SERVICES"
    t = objet.lower()
    if any(mot in t for mot in ['travaux', 'construction', 'bâtiment', 'route', 'installation', 'chantier']):
        return "TRAVAUX"
    if any(mot in t for mot in ['fourniture', 'matériel', 'achat', 'pc', 'consommable', 'équipement']):
        return "FOURNITURES"
    if any(mot in t for mot in ['service', 'prestation', 'étude', 'conseil', 'informatique', 'maintenance', 'formation']):
        return "SERVICES"
    return "SERVICES"


def get_ou_creer_categorie(nom_categorie):
    """Récupère ou crée une catégorie"""
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
            est_it = any(mot in objet.lower() for mot in MOTS_CLES_IT)

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

        categorie_nom = detecter_categorie_simple(donnees['objet'])
        categorie = get_ou_creer_categorie(categorie_nom)

        budget = donnees['budget_estime']
        if driver and url_detail and not budget:
            budget = extraire_budget_depuis_detail(driver, url_detail)

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
            mots_trouves = [m.lower() for m in MOTS_CLES_IT if m.lower() in donnees['objet'].lower()]
            if mots_trouves:
                mots_qs = MotCle.objects.filter(mot__in=mots_trouves)
                consultation.mots_cles.add(*mots_qs)

        print(f"   [OK] {ref} ajoutée (IT: {donnees['est_informatique']}, Budget: {budget or 'N/A'})")
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

    creer_mots_cles()

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    total = 0
    page_num = 1

    try:
        driver.get("https://www.marchespublics.gov.ma/bdc/entreprise/consultation/")
        time.sleep(3)

        while True:
            print(f"\n--- Page {page_num} ---")

            body = driver.find_element(By.TAG_NAME, "body").text
            offres = extraire_toutes_offres(body)
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
        print(f"   [ERREUR] {e}")

    finally:
        driver.quit()

    print("\n" + "=" * 60)
    print(f"  TERMINÉ : {total} nouvelle(s) offre(s) ajoutée(s)")
    print(f"  Total en base : {Consultation.objects.count()} offres")
    print(f"  Offres IT : {Consultation.objects.filter(est_informatique=True).count()}")
    print("=" * 60)


if __name__ == "__main__":
    scraper_consultations()