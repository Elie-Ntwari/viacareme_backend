from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from auth_module.models.user import User

class Hopital(models.Model):
    nom = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)
    ville = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    zone_de_sante = models.CharField(max_length=100, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    actif = models.BooleanField(default=True)
    contrat_valide = models.BooleanField(default=False)
    cree_par_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="hopitaux_crees")
    date_creation = models.DateTimeField(default=timezone.now)

class Gestionnaire(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE, related_name="gestionnaires")
    is_admin_local = models.BooleanField(default=False)
