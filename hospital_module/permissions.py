from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == "SUPERADMIN"

class IsGestionnaireAdminLocal(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role != "GESTIONNAIRE":
            return False
        gestionnaire = getattr(request.user, "gestionnaire", None)
        return gestionnaire and gestionnaire.is_admin_local
