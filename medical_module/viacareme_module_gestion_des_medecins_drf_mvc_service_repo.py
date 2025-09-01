# ==============================
# FOLDER: medical_module/
# ==============================
# ├─ models/
# │   └─ medecin.py
# ├─ serializers/
# │   ├─ medecin_serializers.py
# ├─ repositories/
# │   └─ medecin_repository.py
# ├─ services/
# │   └─ medecin_service.py
# ├─ permissions/
# │   └─ medecin_permissions.py
# ├─ views/
# │   └─ medecin_views.py
# └─ urls.py
#
# Notes générales sécurité / cohérence
# - Toutes les écritures sont sous transaction.atomic
# - Vérification stricte des rôles et du droit d’un gestionnaire à agir dans son hôpital
# - Unicité et déduplication :
#   * User.email unique (déjà dans votre modèle User)
#   * Contrainte unique (user) dans Medecin (OneToOne logique)
#   * Contrainte unique (medecin, hopital) dans MedecinHopital
# - Par défaut, création de compte MEDECIN avec mot de passe « 1234567890 » HASHÉ via make_password
# - Endpoints testables via Postman : exemples JSON en fin de document


# ==============================
# models/medecin.py
# ==============================
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
from auth_module.models.user import User
from hopital_module.models import Hopital  # suppose que vos modèles Hopital/Gestionnaire sont dans hopital_module


class Medecin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil_medecin")
    specialite = models.CharField(max_length=150, blank=True, null=True)

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


# ==============================
# serializers/medecin_serializers.py
# ==============================
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from auth_module.models.user import User
from medical_module.models.medecin import Medecin, MedecinHopital
from hopital_module.models import Hopital, Gestionnaire


DEFAULT_MEDECIN_PASSWORD = "1234567890"


class MedecinBaseSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    nom = serializers.CharField(source="user.nom", read_only=True)
    postnom = serializers.CharField(source="user.postnom", read_only=True)
    prenom = serializers.CharField(source="user.prenom", read_only=True)
    telephone = serializers.CharField(source="user.telephone", read_only=True)

    class Meta:
        model = Medecin
        fields = [
            "id", "email", "nom", "postnom", "prenom", "telephone", "specialite"
        ]


class MedecinCreateOrAssignSerializer(serializers.Serializer):
    # Cas 1: rattacher un compte existant
    existing_user_email = serializers.EmailField(required=False)

    # Cas 2: créer un nouveau compte médecin
    nom = serializers.CharField(required=False)
    postnom = serializers.CharField(required=False, allow_blank=True)
    prenom = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    telephone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    specialite = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # ciblage hôpital obligatoire
    hopital_id = serializers.IntegerField()

    def validate(self, attrs):
        has_existing = bool(attrs.get("existing_user_email"))
        has_new = bool(attrs.get("email") and attrs.get("nom") and attrs.get("prenom"))
        if not (has_existing or has_new):
            raise serializers.ValidationError(
                "Fournir soit existing_user_email, soit les champs de création (nom, prenom, email)."
            )
        return attrs


class MedecinDetailSerializer(MedecinBaseSerializer):
    hopitaux = serializers.SerializerMethodField()

    def get_hopitaux(self, obj: Medecin):
        return [
            {
                "id": mh.hopital.id,
                "nom": mh.hopital.nom,
                "ville": mh.hopital.ville,
                "province": mh.hopital.province,
                "date_affectation": mh.date_affectation.isoformat(),
            }
            for mh in obj.affectations.select_related("hopital").all()
        ]

    class Meta(MedecinBaseSerializer.Meta):
        fields = MedecinBaseSerializer.Meta.fields + ["hopitaux"]


class MedecinHopitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedecinHopital
        fields = ["id", "medecin", "hopital", "date_affectation"]


# ==============================
# repositories/medecin_repository.py
# ==============================
from typing import Optional
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from auth_module.models.user import User
from medical_module.models.medecin import Medecin, MedecinHopital
from hopital_module.models import Hopital


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


# ==============================
# services/medecin_service.py
# ==============================
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.hashers import make_password
from rest_framework.pagination import PageNumberPagination
from medical_module.repositories.medecin_repository import MedecinRepository
from auth_module.models.user import User
from hopital_module.models import Gestionnaire

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
                # si pour une raison le profil n'existe pas (données anciennes), on le crée
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

        # Assurer l'affectation N-N (idempotent)
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


# ==============================
# permissions/medecin_permissions.py
# ==============================
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedAndManagerOrSuperAdmin(BasePermission):
    message = "Accès refusé."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ("SUPERADMIN", "GESTIONNAIRE")


# ==============================
# views/medecin_views.py
# ==============================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError, PermissionDenied
from medical_module.permissions.medecin_permissions import IsAuthenticatedAndManagerOrSuperAdmin
from medical_module.services.medecin_service import MedecinService
from medical_module.serializers.medecin_serializers import (
    MedecinCreateOrAssignSerializer,
    MedecinBaseSerializer,
    MedecinDetailSerializer,
)


class MedecinCreateOrAssignView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedAndManagerOrSuperAdmin]

    def post(self, request):
        serializer = MedecinCreateOrAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            med = MedecinService.create_or_assign_medecin(request.user, serializer.validated_data)
            return Response(MedecinDetailSerializer(med).data, status=status.HTTP_201_CREATED)
        except (ValidationError, PermissionDenied) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MedecinsByHopitalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, hopital_id: int):
        try:
            meds = MedecinService.list_medecins_by_hopital(hopital_id)
            return Response(MedecinBaseSerializer(meds, many=True).data)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MedecinListPaginatedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # renvoie directement une Response paginée
        return MedecinService.list_medecins_paginated(request)


class RemoveAffectationView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedAndManagerOrSuperAdmin]

    def delete(self, request, medecin_id: int, hopital_id: int):
        try:
            removed = MedecinService.remove_affectation(request.user, medecin_id, hopital_id)
            if removed:
                return Response({"message": "Affectation supprimée."}, status=status.HTTP_200_OK)
            return Response({"detail": "Affectation introuvable."}, status=status.HTTP_404_NOT_FOUND)
        except (ValidationError, PermissionDenied) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==============================
# urls.py (medical_module/urls.py)
# ==============================
from django.urls import path
from medical_module.views.medecin_views import (
    MedecinCreateOrAssignView,
    MedecinsByHopitalView,
    MedecinListPaginatedView,
    RemoveAffectationView,
)

urlpatterns = [
    path("medecins/create-or-assign", MedecinCreateOrAssignView.as_view(), name="medecin-create-assign"),
    path("medecins/by-hopital/<int:hopital_id>", MedecinsByHopitalView.as_view(), name="medecins-by-hopital"),
    path("medecins", MedecinListPaginatedView.as_view(), name="medecins-list-paginated"),
    path("medecins/<int:medecin_id>/remove-affectation/<int:hopital_id>", RemoveAffectationView.as_view(), name="medecin-remove-affectation"),
]


# ==============================
# EXEMPLES POSTMAN / JSON
# ==============================
# 1) Créer un NOUVEAU compte médecin + l’affecter à un hôpital (par un Gestionnaire de cet hôpital ou SuperAdmin)
# POST /api/medical/medecins/create-or-assign
# Authorization: Bearer <token>
# Body (JSON):
# {
#   "nom": "Kabasele",
#   "postnom": "M.",
#   "prenom": "Jean",
#   "email": "jean.kabasele@exemple.cd",
#   "telephone": "+243999000111",
#   "specialite": "Gynécologie",
#   "hopital_id": 3
# }
# Réponse 201:
# {
#   "id": 12,
#   "email": "jean.kabasele@exemple.cd",
#   "nom": "Kabasele",
#   "postnom": "M.",
#   "prenom": "Jean",
#   "telephone": "+243999000111",
#   "specialite": "Gynécologie",
#   "hopitaux": [
#     {"id": 3, "nom": "HGR Matete", "ville": "Kinshasa", "province": "Kinshasa", "date_affectation": "2025-09-01T10:00:00+01:00"}
#   ]
# }
#
# NB: le mot de passe par défaut est 1234567890 (hashé côté serveur); le médecin devra le changer via l’endpoint de changement de mot de passe déjà présent dans votre module d’auth.
#
# 2) Rattacher un médecin EXISTANT (user déjà MEDECIN) à un nouvel hôpital
# POST /api/medical/medecins/create-or-assign
# {
#   "existing_user_email": "jean.kabasele@exemple.cd",
#   "hopital_id": 5
# }
# Réponse 201: (même structure que ci-dessus, avec hopitaux incluant les 2 affectations)
#
# 3) Lister les médecins d’un hôpital (tout utilisateur connecté)
# GET /api/medical/medecins/by-hopital/3
# Réponse 200:
# [
#   {"id": 12, "email": "jean.kabasele@exemple.cd", "nom": "Kabasele", "postnom": "M.", "prenom": "Jean", "telephone": "+243999000111", "specialite": "Gynécologie"},
#   {"id": 18, "email": "aisha.ndolo@exemple.cd", "nom": "Ndolo", "postnom": "", "prenom": "Aisha", "telephone": null, "specialite": null}
# ]
#
# 4) Pagination globale des médecins
# GET /api/medical/medecins?page=1&page_size=10
# Réponse 200: objet paginé DRF (count, next, previous, results[])
#
# 5) Retirer l’affectation d’un médecin d’un hôpital (Gestionnaire de cet hôpital ou SuperAdmin)
# DELETE /api/medical/medecins/12/remove-affectation/3
# Réponse 200: {"message": "Affectation supprimée."}
# ou 404 si déjà inexistante


# ==============================
# POINTS D’INTEGRATION & CONSEILS
# ==============================
# - Ajoutez medical_module.urls dans votre urls.py principal, p.ex. path("api/medical/", include("medical_module.urls"))
# - Assurez-vous d’avoir les apps auth_module, hopital_module, medical_module dans INSTALLED_APPS
# - Migrations: python manage.py makemigrations medical_module && python manage.py migrate
# - Vérifiez que l’auth JWT (SimpleJWT) est en place pour les endpoints protégés
# - Pour changer le mot de passe par défaut, réutilisez votre UserService existant (endpoint de reset / change password)
# - Les validations supplémentaires (format téléphone RDC, etc.) peuvent être ajoutées dans le serializer
