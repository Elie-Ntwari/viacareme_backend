# consultation_module/models.py
from django.db import models, transaction
from django.utils import timezone
import uuid
import random
from datetime import timedelta

from auth_module.models.user import User
from patiente__module.models.patiente import Patiente
from cards_module.models import RegistreCarte, CarteAttribuee
from hospital_module.models import Hopital
from grossesse_module.models import Grossesse, DossierObstetrical  # adapte le path
from medical_module.models.medecin import Medecin  # adapte le path


class Consultation(models.Model):
    grossesse = models.ForeignKey(Grossesse, on_delete=models.CASCADE, related_name="consultations")
    medecin = models.ForeignKey(Medecin, on_delete=models.SET_NULL, null=True, related_name="consultations")
    date_consultation = models.DateTimeField(default=timezone.now)

    # Examens cliniques
    poids = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # kg
    SystolicBP = models.IntegerField(null=True, blank=True)  # Pression systolique
    DiastolicBP = models.IntegerField(null=True, blank=True)  # Pression diastolique
    BS = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Glycémie ?
    BodyTemp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Température corporelle
    HeartRate = models.IntegerField(null=True, blank=True)  # Fréquence cardiaque
    hauteur_uterine = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # cm
    mouvements_foetaux = models.BooleanField(default=False)
    oedemes = models.BooleanField(default=False)
    presentation = models.CharField(max_length=50, null=True, blank=True)  # ex: CEPHALIQUE, SIEGE

    # Examens complémentaires et prescriptions
    examens_prescrits = models.TextField(blank=True, null=True)
    examens_resultats = models.TextField(blank=True, null=True)
    medicaments_prescrits = models.TextField(blank=True, null=True)

    observations = models.TextField(blank=True, null=True)
    prochaine_consultation = models.DateField(null=True, blank=True)

    otp_verifie = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_consultation"]


class RendezVous(models.Model):
    STATUTS = (
        ("PLANIFIE", "Planifié"),
        ("TERMINE", "Terminé"),
        ("ANNULE", "Annulé"),
    )
    grossesse = models.ForeignKey(Grossesse, on_delete=models.CASCADE, related_name="rendezvous")
    medecin = models.ForeignKey(Medecin, on_delete=models.SET_NULL, null=True, related_name="rendezvous")
    date_rdv = models.DateTimeField()
    motif = models.CharField(max_length=255, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default="PLANIFIE")
    otp_verifie = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)


class Vaccination(models.Model):
    DESTINE_A = (("MERE", "Mère"), ("ENFANT", "Enfant"))
    grossesse = models.ForeignKey(Grossesse, on_delete=models.CASCADE, related_name="vaccinations")
    medecin = models.ForeignKey(Medecin, on_delete=models.SET_NULL, null=True, related_name="vaccinations")
    vaccin_nom = models.CharField(max_length=100)
    date_administration = models.DateField(default=timezone.now)
    destine_a = models.CharField(max_length=10, choices=DESTINE_A, default="MERE")
    remarque = models.TextField(blank=True, null=True)
    otp_verifie = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)


class ActionOTP(models.Model):
    ACTIONS = (
        ("CONSULTATION", "Consultation"),
        ("RENDEZVOUS", "Rendez-vous"),
        ("VACCINATION", "Vaccination"),
        ("LECTURE", "Lecture"),  # accès lecture/visualisation
    )
    patiente = models.ForeignKey(Patiente, on_delete=models.CASCADE, related_name="action_otps")
    action = models.CharField(max_length=50, choices=ACTIONS)
    code_otp = models.CharField(max_length=6)  # si tu veux hasher, remplace par hash
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    expire_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    uid_rfid = models.CharField(max_length=255, null=True, blank=True)  # provenance scan
    attempts = models.IntegerField(default=0)  # tentative de vérification

    def is_valid(self):
        return (not self.is_used) and (timezone.now() < self.expire_at) and self.attempts < 6

    @classmethod
    def generate_code(cls):
        return f"{random.randint(0, 999999):06d}"

    def mark_used(self):
        self.is_used = True
        self.save(update_fields=["is_used"])
