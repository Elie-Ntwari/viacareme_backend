import secrets
from typing import Optional
from django.db import transaction
from django.utils import timezone
from auth_module.models.user import User
from auth_module.models.verification_code import VerificationCode


class VerificationRepository:

    @staticmethod
    @transaction.atomic
    def create_code(
        user: User,
        code: str,
        canal: str,
        expiration_minutes: int
    ) -> VerificationCode:
        """
        Crée un code de vérification avec date d'expiration.
        Transaction atomique pour garantir la cohérence si l'envoi échoue.
        """
        expiration = timezone.now() + timezone.timedelta(minutes=expiration_minutes)
        return VerificationCode.objects.create(
            user=user,
            code=code,
            canal=canal,
            date_envoi=timezone.now(),
            utilise=False,
            expiration=expiration,
        )

    @staticmethod
    def get_valid_code(
        user: User,
        code: str,
        canal: str
    ) -> Optional[VerificationCode]:
        """
        Retourne un code valide (non utilisé et non expiré) ou None.
        """
        try:
            return VerificationCode.objects.get(
                user=user,
                code=code,
                canal=canal,
                utilise=False,
                expiration__gt=timezone.now()
            )
        except VerificationCode.DoesNotExist:
            return None

    @staticmethod
    def mark_code_as_used(code_instance: VerificationCode) -> None:
        """
        Marque le code comme utilisé.
        """
        code_instance.utilise = True
        code_instance.save()

    @staticmethod
    def resend_code(user, canal: str, expiration_minutes: int = 15) -> VerificationCode:
        """
        Génère un nouveau code de vérification pour l'utilisateur et le canal spécifié.
        Marque tous les anciens codes non utilisés comme expirés.
        """
        # Marquer les anciens codes comme utilisés pour éviter doublons
        VerificationCode.objects.filter(user=user, canal=canal, utilise=False, expiration__gt=timezone.now()) \
                                .update(utilise=True)

        # Générer un nouveau code
        code = str(secrets.randbelow(900000) + 100000)

        expiration = timezone.now() + timezone.timedelta(minutes=expiration_minutes)
        new_code = VerificationCode.objects.create(
            user=user,
            code=code,
            canal=canal,
            date_envoi=timezone.now(),
            utilise=False,
            expiration=expiration
        )

        return new_code
