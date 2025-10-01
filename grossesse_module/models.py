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
        unique_together = ("patiente", "statut")  # 1 grossesse EN_COURS par patiente

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
        ("CREATE_DOSSIER_OBS", "Création dossier obstétrical"),
        ("UPDATE_DOSSIER_OBS", "Modification dossier obstétrical"),
        ("ACCESS_DOSSIER", "Accès dossier obstétrical"),
        
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    patiente = models.ForeignKey(Patiente, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50, choices=ACTIONS)
    timestamp = models.DateTimeField(default=timezone.now)
