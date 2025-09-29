# ==============================
# repositories/patiente_repository.py
# ==============================
from typing import Optional
from django.db import transaction
from auth_module.models.user import User
from patiente__module.models.patiente import Patiente
from hospital_module.models import Hopital
from django.contrib.auth.hashers import make_password


class PatienteRepository:
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        return User.objects.filter(email=email).first()

    @staticmethod
    def get_patiente_by_user(user: User) -> Optional[Patiente]:
        return Patiente.objects.filter(user=user).first()

    @staticmethod
    @transaction.atomic
    def create_user_patiente(
        nom, postnom, prenom, email, telephone,
        date_naissance=None, adresse=None, ville=None, province=None, creer_a_hopital=None
    ) -> Patiente:
        user = User.objects.create(
            nom=nom,
            postnom=postnom or "",
            prenom=prenom,
            email=email,
            password= make_password("1234567890"),
            telephone=telephone,
            role="PATIENTE",
            est_actif=True,
            est_verifie=True,
        )
        pat = Patiente.objects.create(
            user=user,
            date_naissance=date_naissance,
            adresse=adresse or "",
            ville=ville or "",
            province=province or "",
            creer_a_hopital=creer_a_hopital
        )
      
        return pat

    @staticmethod
    def list_patientes_by_hopital(hopital: Hopital):
        return Patiente.objects.filter(user__profil_patiente__isnull=False, user__profil_patiente__id__isnull=False).filter(
            # si tu as un M2M hopital <-> patiente
            creer_a_hopital=hopital
        ).select_related("user")
        
    @staticmethod
    def get_all_patientes():
        return Patiente.objects.all().select_related("user").order_by("-date_inscription")
