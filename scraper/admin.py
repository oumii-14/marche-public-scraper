from django.contrib import admin
from .models import Consultation, ResultatAvisAchat, Organisme, Categorie, MotCle, Alerte, Configuration, HistoriqueScraping

admin.site.register(Consultation)
admin.site.register(ResultatAvisAchat)
admin.site.register(Organisme)
admin.site.register(Categorie)
admin.site.register(MotCle)
admin.site.register(Alerte)
admin.site.register(Configuration)
admin.site.register(HistoriqueScraping)