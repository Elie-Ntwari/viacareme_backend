from typing import Optional
from django.db import transaction
from auth_module.models.user import User
from patiente__module.models.patiente import Patiente



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
    date_naissance=None, adresse=None, ville=None, province=None
      ) -> Patiente:
        user = User.objects.create(
        nom=nom,
        postnom=postnom or "",
        prenom=prenom,
        email=email,
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
    )
        return pat
