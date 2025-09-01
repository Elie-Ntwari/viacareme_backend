from django.core.exceptions import ValidationError, PermissionDenied
from patiente__module.models.patiente import Patiente
from patiente__module.repositories.patiente_repository import PatienteRepository
from auth_module.models.user import User


class PatienteService:
    @staticmethod
    def _assert_user_is_manager_or_admin(user: User):
        if user.role not in ("SUPERADMIN", "GESTIONNAIRE"):
            raise PermissionDenied("Action réservée aux gestionnaires ou superadmin.")

    @staticmethod
    def create_or_assign_patiente(request_user: User, payload: dict):
        PatienteService._assert_user_is_manager_or_admin(request_user)

        existing_email = payload.get("existing_user_email")
        if existing_email:
            # rattacher un user existant
            user = PatienteRepository.get_user_by_email(existing_email)
            if not user:
                raise ValidationError("Utilisateur inexistant.")
            if user.role != "PATIENTE":
                raise ValidationError("Cet utilisateur n'est pas une patiente.")

            # récupère la patiente existante
            pat = PatienteRepository.get_patiente_by_user(user)
            if pat:
                # si tu veux mettre à jour les champs facultatifs
                pat.date_naissance = payload.get("date_naissance", pat.date_naissance)
                pat.adresse = payload.get("adresse", pat.adresse)
                pat.ville = payload.get("ville", pat.ville)
                pat.province = payload.get("province", pat.province)
                pat.save()
            else:
                # crée une nouvelle patiente avec les infos fournies
                pat = Patiente.objects.create(
                    user=user,
                    date_naissance=payload.get("date_naissance"),
                    adresse=payload.get("adresse"),
                    ville=payload.get("ville"),
                    province=payload.get("province"),
                )
        else:
            # création nouvelle patiente + user
            email = payload.get("email")
            if PatienteRepository.get_user_by_email(email):
                raise ValidationError("Un utilisateur avec cet email existe déjà.")
            pat = PatienteRepository.create_user_patiente(
                nom=payload.get("nom"),
                postnom=payload.get("postnom", ""),
                prenom=payload.get("prenom"),
                email=email,
                telephone=payload.get("telephone"),
                date_naissance=payload.get("date_naissance"),
                adresse=payload.get("adresse"),
                ville=payload.get("ville"),
                province=payload.get("province"),
            )

        return pat

    @staticmethod
    def list_patientes():
        return Patiente.objects.select_related("user").all()
