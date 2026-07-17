"""
Module d'Alertes - Semaine 3
Envoi automatique d'emails pour les nouvelles offres IT
"""

import os, sys, django
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marche_public.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
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
    deja_alertees = Alerte.objects.values_list('consultation_id', flat=True)
    nouvelles = offres_it.exclude(id__in=deja_alertees)

    print(f"   Total offres IT: {offres_it.count()}")
    print(f"   Deja alertees: {len(deja_alertees)}")
    print(f"   Nouvelles a alerter: {nouvelles.count()}")

    if not nouvelles:
        print("   [OK] Aucune nouvelle offre IT")
        return

    # Enregistrer les alertes
    for offre in nouvelles:
        Alerte.objects.create(
            consultation=offre,
            destinataire=destinataire,
            email_envoye=False,
            configuration=conf,
        )
        print(f"   [ALERTE] {offre.reference} - {offre.objet[:50]}")

    # Corps HTML
    corps = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; padding: 20px;">
    <div style="max-width: 800px; margin: auto;">
        <h2 style="color: #2c3e50;">📋 Recaptulatif des offres IT</h2>
        <p style="color: #7f8c8d;">Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        <p style="color: #7f8c8d;">Total : <strong>{len(nouvelles)}</strong> nouvelle(s) offre(s) IT detectee(s)</p>

        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <thead>
                <tr style="background-color: #2c3e50; color: white;">
                    <th style="padding: 10px; text-align: left;">Reference</th>
                    <th style="padding: 10px; text-align: left;">Objet</th>
                    <th style="padding: 10px; text-align: left;">Acheteur</th>
                    <th style="padding: 10px; text-align: left;">Date limite</th>
                </tr>
            </thead>
            <tbody>
    """

    for i, offre in enumerate(nouvelles):
        date_lim = offre.date_limite.strftime('%d/%m/%Y') if offre.date_limite else "Non specifiee"
        bg = "#f8f9fa" if i % 2 == 0 else "#ffffff"
        corps += f"""
                <tr style="background-color: {bg};">
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{offre.reference}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{offre.objet[:80]}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{offre.acheteur.nom[:40]}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{date_lim}</td>
                </tr>
        """

    corps += """
            </tbody>
        </table>

        <p style="color: #7f8c8d; font-size: 12px;">
            Consultez le dashboard : <a href="http://localhost:8501" style="color: #3498db;">http://localhost:8501</a><br>
            (Lancez d'abord : <code>streamlit run dashboard_app.py</code>)
        </p>
        <hr style="border: none; border-top: 1px solid #eee;">
        <p style="color: #95a5a6; font-size: 11px;">
            Cet email est genere automatiquement par la Plateforme de veille des marches publics.
        </p>
    </div>
    </body>
    </html>
    """

    sujet = f"[Marches Publics] {len(nouvelles)} nouvelle(s) offre(s) IT detectee(s)"

    try:
        msg = EmailMultiAlternatives(
            subject=sujet,
            body="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destinataire],
        )
        msg.attach_alternative(corps, "text/html")
        msg.send(fail_silently=False)

        Alerte.objects.filter(email_envoye=False).update(email_envoye=True)
        print(f"\n   [EMAIL] Envoye a {destinataire}")
    except Exception as e:
        print(f"\n   [EMAIL] Erreur envoi: {e}")

    print(f"\n   [OK] {len(nouvelles)} alerte(s) traitee(s)")


if __name__ == "__main__":
    envoyer_alertes()