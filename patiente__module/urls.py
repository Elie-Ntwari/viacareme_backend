from django.urls import path
from patiente__module.views.patiente_views import PatienteCreateOrAssignView, PatienteList, PatientesByHopitalView

urlpatterns = [
    path("patientes/create-or-assign/<int:hopital_id>/", PatienteCreateOrAssignView.as_view(), name="patiente-create-assign"),
    path("patientes/<int:hopital_id>/", PatientesByHopitalView.as_view(), name="patientes-list"),
    path("patientes/", PatienteList.as_view(), name="patientes-all-list"),
]
