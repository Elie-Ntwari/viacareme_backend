# auth_module/services/jwt_service.py
from typing import Dict
from django.conf import settings
from django.core.exceptions import ValidationError

from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from auth_module.models.user import User

class JWTService:
    @staticmethod
    def generate_tokens_for_user(user: User) -> Dict[str, str]:
        """
        Génère un couple (access, refresh) via simplejwt.
        """
        try:
            refresh = RefreshToken.for_user(user)
        except Exception as e:
            raise ValidationError(f"Impossible de générer les tokens: {str(e)}")

        access = refresh.access_token
        return {
            "access_token": str(access),
            "refresh_token": str(refresh),
            "access_expires_at": access.payload.get("exp"),
            "refresh_expires_at": refresh.payload.get("exp"),
        }

    @staticmethod
    def refresh_tokens(refresh_token_str: str) -> Dict[str, str]:
        """
        Utilise un refresh token pour obtenir de nouveaux tokens.
        Si la rotation/blacklist est activée dans SIMPLE_JWT, simplejwt gère la rotation.
        Ici on essaye d'instancier RefreshToken et on renvoie de nouveaux tokens.
        """
        try:
            refresh = RefreshToken(refresh_token_str)
        except TokenError as e:
            raise ValidationError("Refresh token invalide ou expiré.")

        # Si blacklist app est installée et rotation activée, blacklist() va invalider l'ancien.
        try:
            refresh.blacklist()
        except Exception:
            # blacklist() peut échouer si l'app de blacklist n'est pas activée,
            # on ignore cet échec volontairement (mais on peut logger).
            pass

        # Générer de nouveaux tokens pour le même user
        try:
            user_id = refresh.payload.get("user_id") or refresh.payload.get("user") or refresh["user_id"]
            user = User.objects.get(id=user_id)
        except Exception:
            raise ValidationError("Utilisateur lié au token introuvable.")

        return JWTService.generate_tokens_for_user(user)

    @staticmethod
    def revoke_all(user: User) -> None:
        """
        Blackliste tous les outstanding tokens d'un utilisateur (revocation globale).
        """
        tokens = OutstandingToken.objects.filter(user=user)
        for t in tokens:
            BlacklistedToken.objects.get_or_create(token=t)
