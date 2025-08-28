from rest_framework.permissions import BasePermission

from hospital_module.models import Gestionnaire

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == "SUPERADMIN"

class IsGestionnaireAdminLocal(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role != "GESTIONNAIRE":
            return False
        
        try:
            gestionnaire = request.user.gestionnaire
        except Gestionnaire.DoesNotExist:
            return False

        # Vérifie qu'il est bien admin local ET lié à l'hôpital de l'URL
        hopital_id = view.kwargs.get("pk")
        return gestionnaire.is_admin_local and str(gestionnaire.hopital_id) == str(hopital_id)
