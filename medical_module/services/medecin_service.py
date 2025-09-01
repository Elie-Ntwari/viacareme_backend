
# ==============================
# services/medecin_service.py
# ==============================
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.hashers import make_password
from rest_framework.pagination import PageNumberPagination
from hospital_module.models import Gestionnaire
from medical_module.models.medecin import Medecin
from medical_module.repositories.medecin_repository import MedecinRepository
from auth_module.models.user import User


DEFAULT_MEDECIN_PASSWORD = "1234567890"


class MedecinService:
    @staticmethod
    def _assert_user_can_manage_hopital(user: User, hopital_id: int):
        # SuperAdmin peut tout
        if user.role == "SUPERADMIN":
            return
        # Gestionnaire doit appartenir à cet hôpital
        try:
            gest = Gestionnaire.objects.get(user=user)
        except Gestionnaire.DoesNotExist:
            raise PermissionDenied("Vous n'êtes pas autorisé à gérer cet hôpital.")
        if gest.hopital_id != hopital_id:
            raise PermissionDenied("Action non autorisée pour cet hôpital.")

    @staticmethod
    def create_or_assign_medecin(request_user: User, payload: dict):
        hopital_id = int(payload.get("hopital_id"))
        MedecinService._assert_user_can_manage_hopital(request_user, hopital_id)

        hopital = MedecinRepository.get_hopital_by_id(hopital_id)
        if not hopital:
            raise ValidationError("Hôpital introuvable.")

        existing_email = payload.get("existing_user_email")
        if existing_email:
            # Rattacher un compte existant
            user = MedecinRepository.get_user_by_email(existing_email)
            if not user:
                raise ValidationError("Aucun utilisateur avec cet email.")
            if user.role != "MEDECIN":
                raise ValidationError("L'utilisateur trouvé n'a pas le rôle MEDECIN.")
            med = MedecinRepository.get_medecin_by_user(user)
            if not med:
                med = Medecin.objects.create(user=user, specialite=None)
        else:
            # Création d'un nouveau compte médecin
            email = payload.get("email")
            if MedecinRepository.get_user_by_email(email):
                raise ValidationError("Un utilisateur avec cet email existe déjà.")

            default_hash = make_password(DEFAULT_MEDECIN_PASSWORD)
            med = MedecinRepository.create_user_medecin(
                nom=payload.get("nom"),
                postnom=payload.get("postnom", ""),
                prenom=payload.get("prenom"),
                email=email,
                telephone=payload.get("telephone"),
                specialite=payload.get("specialite"),
                default_password_hash=default_hash,
            )

        # ✅ Vérifier si déjà assigné
        if MedecinRepository.is_already_assigned(med, hopital):
            raise ValidationError(f"Ce médecin est déjà assigné à l'hôpital {hopital.nom}.")

        # Assurer l'affectation
        mh = MedecinRepository.ensure_affectation(med, hopital)
        return med


    @staticmethod
    def list_medecins_by_hopital(hopital_id: int):
        hopital = MedecinRepository.get_hopital_by_id(hopital_id)
        if not hopital:
            raise ValidationError("Hôpital introuvable.")
        return MedecinRepository.list_medecins_by_hopital(hopital)

    @staticmethod
    def list_medecins_paginated(request):
        queryset = MedecinRepository.list_all_medecins()
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get("page_size", 10))
        page = paginator.paginate_queryset(queryset, request)
        from medical_module.serializers.medecin_serializers import MedecinBaseSerializer
        ser = MedecinBaseSerializer(page, many=True)
        return paginator.get_paginated_response(ser.data)

    @staticmethod
    def remove_affectation(request_user: User, medecin_id: int, hopital_id: int) -> bool:
        MedecinService._assert_user_can_manage_hopital(request_user, hopital_id)
        hopital = MedecinRepository.get_hopital_by_id(hopital_id)
        if not hopital:
            raise ValidationError("Hôpital introuvable.")
        med = MedecinRepository.get_medecin_by_id(medecin_id)
        if not med:
            raise ValidationError("Médecin introuvable.")
        return MedecinRepository.remove_affectation(med, hopital)