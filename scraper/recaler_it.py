"""
Recalcule est_informatique et mots_cles pour toutes les offres en base
Utilise des regex avec word boundaries pour eviter les faux positifs
"""
import os, sys, re, django

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marche_public.settings')
django.setup()

from scraper.models import Consultation, MotCle

def recaler_it():
    mots = [m.mot.lower() for m in MotCle.objects.all()]
    print(f"   {len(mots)} mots-cles en base : {mots}")

    offres = Consultation.objects.all()
    corrige = 0
    for offre in offres:
        objet = (offre.objet or '').lower()
        mots_trouves = [m for m in mots if re.search(r'\b' + re.escape(m) + r'\b', objet)]
        est_it = len(mots_trouves) > 0

        if offre.est_informatique != est_it:
            offre.est_informatique = est_it
            offre.save(update_fields=['est_informatique'])
            corrige += 1
            print(f"   [FIX] {offre.reference} -> IT={est_it} (mots: {mots_trouves})")

        offre.mots_cles.set(MotCle.objects.filter(mot__in=mots_trouves))

    total_it = Consultation.objects.filter(est_informatique=True).count()
    print(f"\n   Termine : {corrige} offres corrigees")
    print(f"   Total IT en base : {total_it}")

if __name__ == '__main__':
    recaler_it()
