"""
Module d'Alertes - Semaine 3
Envoi automatique d'emails pour les nouvelles offres IT
"""

import os, sys, django
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marche_public.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from scraper.models import Consultation, Alerte, Configuration


def envoyer_alertes():
    print("=" * 60)
    print("  SYSTEME D'ALERTES")
    print("=" * 60)

    conf = Configuration.objects.filter(nom_parametre='EMAIL_DESTINATAIRE').first()
    if not conf:
        print("   [ERREUR] Aucun destinataire configure")
        return

    destinataire = conf.valeur

    offres_it = Consultation.objects.filter(est_informatique=True)
    total_it = offres_it.count()
    deja_alertees = Alerte.objects.values_list('consultation_id', flat=True)
    nouvelles = offres_it.exclude(id__in=deja_alertees)

    print(f"   Total offres IT: {total_it}")
    print(f"   Deja alertees: {len(deja_alertees)}")
    print(f"   Nouvelles a alerter: {nouvelles.count()}")

    if not nouvelles:
        print("   [OK] Aucune nouvelle offre IT")
        return

    lignes_email = []
    for offre in nouvelles:
        budget = offre.budget_estime or "Non specifie"
        mots = ", ".join(offre.mots_cles.values_list('mot', flat=True))
        date_lim = offre.date_limite.strftime('%d/%m/%Y') if offre.date_limite else "Non specifiee"

        lignes_email.append(
            f"{offre.reference:<20} {offre.objet[:60]:<62} {offre.acheteur.nom:<30} {date_lim:<12}"
        )

        Alerte.objects.create(
            consultation=offre,
            destinataire=destinataire,
            email_envoye=False,
            configuration=conf,
        )
        print(f"   [ALERTE] {offre.reference} - {offre.objet[:50]}")

    sujet = f"[Marches Publics] {len(nouvelles)} nouvelle(s) offre(s) IT detectee(s)"

    corps = "=" * 130 + "\n"
    corps += "RECAPITULATIF DES OFFRES IT\n"
    corps += f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    corps += f"Total : {len(nouvelles)} nouvelle(s) offre(s) IT\n"
    corps += "=" * 130 + "\n\n"
    corps += f"{'Reference':<20} {'Objet':<62} {'Acheteur':<30} {'Date limite':<12}\n"
    corps += "-" * 130 + "\n"
    for ligne in lignes_email:
        corps += ligne + "\n"
    corps += "-" * 130 + "\n\n"
    corps += "Consultez le dashboard : http://localhost:8501\n"
    corps += "---\n"
    corps += "Cet email est genere automatiquement par la Plateforme de veille des marches publics."

    try:
        send_mail(
            subject=sujet,
            message=corps,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinataire],
            fail_silently=False,
        )
        Alerte.objects.filter(email_envoye=False).update(email_envoye=True)
        print(f"\n   [EMAIL] Envoye a {destinataire}")
    except Exception as e:
        print(f"\n   [EMAIL] Erreur envoi: {e}")

    print(f"\n   [OK] {len(nouvelles)} alerte(s) traitee(s)")


if __name__ == "__main__":
    envoyer_alertes()