from django.db import models
from django.utils import timezone
from auth_module.models.user import User


class Patiente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil_patiente")
    date_naissance = models.DateField(null=True, blank=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    numero_identification = models.CharField(max_length=100, unique=True, null=True, blank=True)
    date_inscription = models.DateTimeField(default=timezone.now)
    has_carte = models.BooleanField(default=False)
  
    class Meta:
        db_table = "patiente"

    def __str__(self):
        return f"Patiente<{self.user_id}> {self.user.prenom} {self.user.nom}"
