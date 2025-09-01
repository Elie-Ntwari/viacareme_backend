# ==============================
# repositories/medecin_repository.py
# ==============================
from typing import Optional
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from auth_module.models.user import User
from hospital_module.models import Hopital
from medical_module.models.medecin import Medecin, MedecinHopital


class MedecinRepository:
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_medecin_by_user(user: User) -> Optional[Medecin]:
        try:
            return Medecin.objects.get(user=user)
        except Medecin.DoesNotExist:
            return None

    @staticmethod
    def get_medecin_by_id(medecin_id: int) -> Optional[Medecin]:
        try:
            return Medecin.objects.get(id=medecin_id)
        except Medecin.DoesNotExist:
            return None

    @staticmethod
    def get_hopital_by_id(hopital_id: int) -> Optional[Hopital]:
        try:
            return Hopital.objects.get(id=hopital_id)
        except Hopital.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create_user_medecin(nom: str, postnom: str, prenom: str, email: str, telephone: Optional[str], specialite: Optional[str], default_password_hash: str) -> Medecin:
        user = User.objects.create(
            nom=nom,
            postnom=postnom or "",
            prenom=prenom,
            email=email,
            telephone=telephone,
            password=default_password_hash,  # hash déjà préparé par le service
            role="MEDECIN",
            est_actif=True,
            est_verifie=True,
            deux_facteurs_active=False,
        )
        med = Medecin.objects.create(user=user, specialite=specialite or None)
        return med

    @staticmethod
    @transaction.atomic
    def ensure_affectation(medecin: Medecin, hopital: Hopital) -> MedecinHopital:
        try:
            mh, created = MedecinHopital.objects.get_or_create(medecin=medecin, hopital=hopital)
            return mh
        except IntegrityError:
            # en cas de course condition, on relit
            return MedecinHopital.objects.get(medecin=medecin, hopital=hopital)

    @staticmethod
    def list_medecins_by_hopital(hopital: Hopital):
        return Medecin.objects.filter(affectations__hopital=hopital).select_related("user").prefetch_related("affectations")

    @staticmethod
    def list_all_medecins():
        return Medecin.objects.select_related("user").all()

    @staticmethod
    @transaction.atomic
    def remove_affectation(medecin: Medecin, hopital: Hopital) -> bool:
        deleted, _ = MedecinHopital.objects.filter(medecin=medecin, hopital=hopital).delete()
        return deleted > 0
    
    @staticmethod
    def is_already_assigned(medecin, hopital) -> bool:
        return medecin.hopitaux.filter(id=hopital.id).exists()

