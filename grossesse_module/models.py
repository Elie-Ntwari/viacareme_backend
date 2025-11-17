from django.db import models
from django.utils import timezone
from auth_module.models.user import User
from patiente__module.models.patiente import Patiente

class Grossesse(models.Model):
    STATUTS = (
        ("EN_COURS", "En cours"),
        ("TERMINEE", "Terminée"),
        ("PERDUE", "Perdue"),
    )
    patiente = models.ForeignKey(Patiente, on_delete=models.CASCADE, related_name="grossesses")
    date_debut = models.DateField()
    dpa = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUTS, default="EN_COURS")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        pass  # Constraint handled in service logic

    def __str__(self):
        return f"Grossesse {self.id} - {self.patiente.user.nom}"


class DossierObstetrical(models.Model):
    grossesse = models.OneToOneField(Grossesse, on_delete=models.CASCADE, related_name="dossier")
    geste = models.IntegerField(default=0)
    parite = models.IntegerField(default=0)
    date_ddr = models.DateField(null=True, blank=True)
    groupage_sanguin = models.CharField(max_length=10, blank=True, null=True)
    rhesus = models.CharField(max_length=5, blank=True, null=True)
    antecedents_medicaux = models.TextField(blank=True, null=True)
    antecedents_obstetricaux = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    prise_medicaments = models.TextField(blank=True, null=True)
    autres_infos = models.TextField(blank=True, null=True)
    risque_grossesse = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Dossier obstétrical Grossesse {self.grossesse.id}"


class ClotureGrossesse(models.Model):
    GENRES_ENFANT = (
        ("MASCULIN", "Masculin"),
        ("FEMININ", "Féminin"),
        ("INDETERMINE", "Indéterminé"),
    )
    
    TYPES_ACCOUCHEMENT = (
        ("VAGINAL", "Accouchement vaginal"),
        ("CESARIENNE", "Césarienne"),
        ("FORCEPS", "Forceps"),
        ("VENTOUSE", "Ventouse"),
    )
    
    ISSUES_GROSSESSE = (
        ("VIVANT", "Enfant vivant"),
        ("MORT_NE", "Mort-né"),
        ("FAUSSE_COUCHE", "Fausse couche"),
        ("INTERRUPTION", "Interruption médicale"),
    )
    
    grossesse = models.OneToOneField(Grossesse, on_delete=models.CASCADE, related_name="cloture")
    date_accouchement = models.DateField()
    nombre_enfants = models.IntegerField(default=1)
    genre_enfant = models.CharField(max_length=20, choices=GENRES_ENFANT, null=True, blank=True)
    poids_naissance = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="Poids en kg")
    taille_naissance = models.IntegerField(null=True, blank=True, help_text="Taille en cm")
    type_accouchement = models.CharField(max_length=20, choices=TYPES_ACCOUCHEMENT)
    issue_grossesse = models.CharField(max_length=20, choices=ISSUES_GROSSESSE)
    complications = models.TextField(blank=True, null=True)
    observations = models.TextField(blank=True, null=True)
    duree_travail = models.DurationField(null=True, blank=True, help_text="Durée du travail")
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Clôture grossesse {self.grossesse.id} - {self.date_accouchement}"


class DossierAccess(models.Model):
    patiente = models.ForeignKey(Patiente, on_delete=models.CASCADE, related_name="acces_dossier")
    code_otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    expire_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expire_at


class AuditAction(models.Model):
    ACTIONS = (
        ("CREATE_GROSSESSE", "Création grossesse"),
        ("UPDATE_GROSSESSE", "Modification grossesse"),
        ("CLOTURE_GROSSESSE", "Clôture grossesse"),
        ("CREATE_DOSSIER_OBS", "Création dossier obstétrical"),
        ("UPDATE_DOSSIER_OBS", "Modification dossier obstétrical"),
        ("ACCESS_DOSSIER", "Accès dossier obstétrical"),
        
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    patiente = models.ForeignKey(Patiente, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50, choices=ACTIONS)
    timestamp = models.DateTimeField(default=timezone.now)
