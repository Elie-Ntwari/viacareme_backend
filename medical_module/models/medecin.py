# models/medecin.py
# ==============================
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
from auth_module.models.user import User
from hospital_module.models import Hopital





class Medecin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil_medecin")
    specialite = models.CharField(max_length=150, blank=True, null=True)
    hopitaux = models.ManyToManyField(
        "hospital_module.Hopital",
        through="MedecinHopital",
        related_name="hopitaux_medecins"
    )

    class Meta:
        db_table = "medecin"

    def __str__(self):
        return f"Medecin<{self.user_id}> {self.user.prenom} {self.user.nom}"



class MedecinHopital(models.Model):
    medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE, related_name="affectations")
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE, related_name="medecins")
    date_affectation = models.DateTimeField(default=timezone.now)


    class Meta:
       db_table = "medecin_hopital"
       constraints = [
           models.UniqueConstraint(fields=["medecin", "hopital"], name="uniq_medecin_hopital")
      ]


       def __str__(self):
           return f"MedecinHopital<{self.medecin_id}@{self.hopital_id}>"