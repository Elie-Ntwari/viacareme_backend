from django.urls import path
from patiente__module.views.patiente_views import UpdateGrossesseAndDossierView,PatienteCreateOrAssignView,PatientesFullInfoByHopitalView,CreateGrossesseAndDossierView,PatienteFullInfoView, PatienteList, PatientesByHopitalView, AssignMedecinToPatienteView, UnassignMedecinFromPatienteView, ListMedecinsForPatienteView

urlpatterns = [
    path("patientes/create-or-assign/<int:hopital_id>/", PatienteCreateOrAssignView.as_view(), name="patiente-create-assign"),
    path("patientes/<int:hopital_id>/", PatientesByHopitalView.as_view(), name="patientes-list"),
    path("patientes/", PatienteList.as_view(), name="patientes-all-list"),
    path("patientes/<int:patiente_id>/init-grossesse-dossier/", CreateGrossesseAndDossierView.as_view(), name="patiente-init-grossesse-dossier"),
    path("patientes/<int:patiente_id>/full-info/", PatienteFullInfoView.as_view(), name="patiente-full-info"),
    path("patientes/full-info/<int:hopital_id>/", PatientesFullInfoByHopitalView.as_view(), name="patiente-full-info-hopital"),
    path("patientes/grossesse-dossier/<int:grossesse_id>/update/", UpdateGrossesseAndDossierView.as_view(), name="patiente-update-grossesse"),
    path("patientes/<int:hopital_id>/<int:patiente_id>/assign-medecin/", AssignMedecinToPatienteView.as_view(), name="patiente-assign-medecin"),
    path("patientes/<int:hopital_id>/<int:patiente_id>/unassign-medecin/", UnassignMedecinFromPatienteView.as_view(), name="patiente-unassign-medecin"),
    path("patientes/<int:hopital_id>/<int:patiente_id>/medecins/", ListMedecinsForPatienteView.as_view(), name="patiente-list-medecins")
]
