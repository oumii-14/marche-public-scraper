import os,sys,django
sys.path.insert(0,'.')
os.environ['DJANGO_SETTINGS_MODULE']='marche_public.settings'
django.setup()
from scraper.models import Consultation, Alerte

o = Consultation.objects.get(reference='10/2026CNSSDRANFA')
print(f'Reference: {o.reference}')
print(f'Date pub: {o.date_publication}')
print(f'IT: {o.est_informatique}')
alertes = Alerte.objects.filter(consultation=o).order_by('date_envoi')
print(f'Alertes totales: {alertes.count()}')
for a in alertes:
    print(f'  {a.date_envoi}')
