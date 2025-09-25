
# cards_module/models.py
from django.db import models, transaction
from django.utils import timezone
import uuid
from auth_module.models.user import User
from hospital_module.models import Hopital
from patiente__module.models.patiente import Patiente  

class Device(models.Model):
    nom = models.CharField(max_length=255,null=True, blank=True)
    numero_serie = models.CharField(max_length=255, unique=True, null=True, blank=True  )
    cle_authentification = models.CharField(max_length=255, blank=True, null=True)
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE, related_name="devices",null=True, blank=True )
    actif = models.BooleanField(default=True)
    date_installation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.nom} ({self.numero_serie})"


class RegistreCarte(models.Model):
    UID_STATUS = (
        ("ENREGISTREE", "Enregistrée"),
        ("LIVREE", "Livrée"),
        ("AFFECTEE", "Affectée"),
        ("PERDUE", "Perdue"),
        ("ENDOMMAGEE", "Endommagée"),
    )
    numero_serie = models.CharField(max_length=255, unique=True)  # interne
    uid_rfid = models.CharField(max_length=255, unique=True)      # UID physique
    est_viacareme = models.BooleanField(default=False)
    statut = models.CharField(max_length=20, choices=UID_STATUS, default="ENREGISTREE")
    date_enregistrement = models.DateTimeField(default=timezone.now)
    enregistre_par_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="cartes_enregistrees")

    def __str__(self):
        return f"{self.uid_rfid} - {self.statut}"


class LotCarte(models.Model):
    numero_lot = models.CharField(max_length=255, unique=True)
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE, related_name="lots")
    date_livraison = models.DateTimeField(default=timezone.now)
    livre_par_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="lots_livres")

    def compter_cartes(self):
        return self.details.count()

    def __str__(self):
        return self.numero_lot


class LotCarteDetail(models.Model):
    lot = models.ForeignKey(LotCarte, on_delete=models.CASCADE, related_name="details")
    registre = models.ForeignKey(RegistreCarte, on_delete=models.CASCADE, related_name="lot_details")

    class Meta:
        unique_together = ("lot", "registre")




class SessionScan(models.Model):
    ACTION_CHOICES = (
        ("ENREGISTREMENT", "Enregistrement"),
        ("ATTRIBUTION", "Attribution"),
    )
    STATUS = (
        ("PENDING", "En attente"),
        ("COMPLETED", "Terminée"),
        ("CANCELLED", "Annulée"),
        ("EXPIRED", "Expirée"),
    )

    type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUS, default="PENDING")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    cible_id = models.IntegerField(null=True, blank=True)        # patient id si ATTRIBUTION
    # hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE, related_name="sessions")
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, related_name="sessions")
    lance_par_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sessions_lancees")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        return self.statut == "PENDING" and timezone.now() < self.expires_at

    def mark_completed(self):
        self.statut = "COMPLETED"
        self.closed_at = timezone.now()
        self.save()





class CarteAttribuee(models.Model):
    carte = models.OneToOneField(
        RegistreCarte,
        on_delete=models.CASCADE,
        related_name="attribution"
    )
    patiente = models.OneToOneField(
        Patiente,
        on_delete=models.CASCADE,
        related_name="attribution"
    )
    hopital = models.ForeignKey(
        Hopital,
        on_delete=models.CASCADE,
        related_name="attributions"
    )
    attribuee_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="cartes_attribuees"
    )
    date_attribution = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "carte_attribuee"
        unique_together = ("carte", "patiente")

    def __str__(self):
        return f"Carte {self.carte.uid_rfid} → {self.patiente.user.nom}"
