from django.db import models


class Organisme(models.Model):
    TYPE_CHOICES = [
        ('ACHETEUR', 'Acheteur'),
        ('PRESTATAIRE', 'Prestataire'),
    ]

    nom = models.CharField(max_length=200, verbose_name="Nom")
    ville = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ville")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='ACHETEUR', verbose_name="Type")

    def __str__(self):
        return f"{self.nom} ({self.get_type_display()})"

    class Meta:
        verbose_name = "Organisme"
        verbose_name_plural = "Organismes"


class Categorie(models.Model):
    NOM_CHOICES = [
        ('TRAVAUX', 'Travaux'),
        ('FOURNITURES', 'Fournitures'),
        ('SERVICES', 'Services'),
    ]

    nom = models.CharField(max_length=20, choices=NOM_CHOICES, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")

    def __str__(self):
        return self.get_nom_display()

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"


class MotCle(models.Model):
    mot = models.CharField(max_length=50, unique=True, verbose_name="Mot-clé")

    def __str__(self):
        return self.mot

    class Meta:
        verbose_name = "Mot-clé"
        verbose_name_plural = "Mots-clés"


class Consultation(models.Model):
    reference = models.CharField(max_length=100, unique=True, verbose_name="Référence")
    objet = models.TextField(verbose_name="Objet")
    date_limite = models.DateTimeField(verbose_name="Date limite")
    lieu_execution = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lieu d'exécution")
    budget_estime = models.CharField(max_length=50, blank=True, null=True, verbose_name="Budget estimé")
    est_annule = models.BooleanField(default=False, verbose_name="Annulé")
    est_informatique = models.BooleanField(default=False, verbose_name="Offre IT")
    date_publication = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    acheteur = models.ForeignKey(
        Organisme,
        on_delete=models.CASCADE,
        related_name='consultations_acheteur',
        limit_choices_to={'type': 'ACHETEUR'},
        verbose_name="Acheteur"
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        related_name='consultations',
        verbose_name="Catégorie"
    )
    mots_cles = models.ManyToManyField(MotCle, blank=True, related_name='consultations', verbose_name="Mots-clés")

    def __str__(self):
        return f"{self.reference} - {self.objet[:50]}"

    class Meta:
        verbose_name = "Consultation"
        verbose_name_plural = "Consultations"


class ResultatAvisAchat(models.Model):
    reference = models.CharField(max_length=100, unique=True, verbose_name="Référence")
    objet = models.TextField(verbose_name="Objet")
    date_publication_resultat = models.DateTimeField(verbose_name="Date de publication du résultat")
    nombre_devis = models.IntegerField(blank=True, null=True, verbose_name="Nombre de devis")
    montant_ttc = models.CharField(max_length=50, blank=True, null=True, verbose_name="Montant TTC")
    est_infructueux = models.BooleanField(default=False, verbose_name="Infructueux")

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='resultats',
        verbose_name="Consultation concernée"
    )
    prestataire = models.ForeignKey(
        Organisme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resultats_prestataire',
        limit_choices_to={'type': 'PRESTATAIRE'},
        verbose_name="Prestataire (entreprise gagnante)"
    )

    def __str__(self):
        return f"{self.reference} - {self.objet[:50]}"

    class Meta:
        verbose_name = "Résultat d'avis d'achat"
        verbose_name_plural = "Résultats des avis d'achat"


class Alerte(models.Model):
    date_envoi = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    destinataire = models.EmailField(verbose_name="Destinataire")
    email_envoye = models.BooleanField(default=False, verbose_name="Email envoyé")

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='alertes',
        verbose_name="Consultation"
    )
    configuration = models.ForeignKey(
        'Configuration',
        on_delete=models.CASCADE,
        related_name='alertes',
        verbose_name="Configuration"
    )

    def __str__(self):
        return f"Alerte pour {self.consultation.reference} - {self.destinataire}"

    class Meta:
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"


class Configuration(models.Model):
    nom_parametre = models.CharField(max_length=100, unique=True, verbose_name="Nom du paramètre")
    valeur = models.TextField(verbose_name="Valeur")
    description = models.TextField(blank=True, verbose_name="Description")

    mots_cles = models.ManyToManyField(MotCle, blank=True, related_name='configurations', verbose_name="Mots-clés")

    def __str__(self):
        return f"{self.nom_parametre} = {self.valeur}"

    class Meta:
        verbose_name = "Configuration"
        verbose_name_plural = "Configurations"


class HistoriqueScraping(models.Model):
    date_scraping = models.DateTimeField(auto_now_add=True, verbose_name="Date du scraping")
    nb_consultations = models.IntegerField(default=0, verbose_name="Nombre de consultations")
    nb_resultats = models.IntegerField(default=0, verbose_name="Nombre de résultats")
    nb_offres_it = models.IntegerField(default=0, verbose_name="Nombre d'offres IT")
    statut = models.CharField(max_length=50, default="Succès", verbose_name="Statut")

    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historiques',
        verbose_name="Configuration"
    )

    def __str__(self):
        return f"Scraping du {self.date_scraping}"

    class Meta:
        verbose_name = "Historique de scraping"
        verbose_name_plural = "Historiques de scraping"
