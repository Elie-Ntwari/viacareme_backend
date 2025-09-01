
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
