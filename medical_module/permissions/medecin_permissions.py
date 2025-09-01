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

