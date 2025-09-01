from rest_framework.permissions import BasePermission


class IsAuthenticatedAndManagerOrSuperAdmin(BasePermission):
    message = "Accès refusé."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ("SUPERADMIN", "GESTIONNAIRE")
