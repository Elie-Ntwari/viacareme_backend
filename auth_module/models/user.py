# auth_module/models/user.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from auth_module.utils.crypto import encrypt_str, decrypt_str  # à créer

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, nom=None, postnom=None, prenom=None, **extra_fields):
        if not email:
            raise ValueError("Email requis")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            nom=nom,
            postnom=postnom,
            prenom=prenom,
            **extra_fields
        )
        if password:
            user.set_password(password)
        else:
            raise ValueError("Le mot de passe est requis")
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('est_actif', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('SUPERADMIN', 'Super Admin'),
        ('GESTIONNAIRE', 'Gestionnaire'),
        ('MEDECIN', 'Médecin'),
        ('PATIENTE', 'Patiente'),
    )

    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=150)
    postnom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    photo_url = models.URLField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    est_actif = models.BooleanField(default=False)
    est_verifie = models.BooleanField(default=False)
    deux_facteurs_active = models.BooleanField(default=False)
    totp_secret_encrypted = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(default=timezone.now)

    # Champs requis pour Django
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'postnom', 'prenom']

    def set_totp_secret(self, raw_secret: str):
        self.totp_secret_encrypted = encrypt_str(raw_secret)

    def get_totp_secret(self):
        if not self.totp_secret_encrypted:
            return None
        return decrypt_str(self.totp_secret_encrypted)

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"
