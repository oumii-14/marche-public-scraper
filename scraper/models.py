from django.db import models

class Consultation(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    objet = models.TextField()
    acheteur = models.CharField(max_length=200)
    date_limite = models.DateTimeField()
    lieu_execution = models.CharField(max_length=100)
    budget_estime = models.CharField(max_length=50, blank=True, null=True)
    est_annule = models.BooleanField(default=False)
    est_informatique = models.BooleanField(default=False)
    date_publication = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference

class ResultatAvisAchat(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    objet = models.TextField()
    acheteur = models.CharField(max_length=200)
    date_limite = models.DateTimeField()
    lieu_execution = models.CharField(max_length=100)
    nombre_devis = models.IntegerField()
    entreprise_attributaire = models.CharField(max_length=200, blank=True, null=True)
    montant_ttc = models.CharField(max_length=50, blank=True, null=True)
    est_infructueux = models.BooleanField(default=False)
    date_publication_resultat = models.DateTimeField()

    def __str__(self):
        return self.reference

class Organisme(models.Model):
    nom = models.CharField(max_length=200)
    ville = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class MotCle(models.Model):
    mot = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.mot

class Alerte(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    date_envoi = models.DateTimeField(auto_now_add=True)
    destinataire = models.EmailField()
    email_envoye = models.BooleanField(default=False)

    def __str__(self):
        return f"Alerte {self.consultation.reference}"

class Configuration(models.Model):
    nom_parametre = models.CharField(max_length=100, unique=True)
    valeur = models.TextField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nom_parametre} = {self.valeur}"

class HistoriqueScraping(models.Model):
    date_scraping = models.DateTimeField(auto_now_add=True)
    nb_consultations = models.IntegerField(default=0)
    nb_resultats = models.IntegerField(default=0)
    nb_offres_it = models.IntegerField(default=0)
    statut = models.CharField(max_length=50, default="Succès")

    def __str__(self):
        return f"Scraping du {self.date_scraping}"
