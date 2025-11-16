# consultation_module/urls.py
from rest_framework import routers
from django.urls import path, include
from .views import (
    ConsultationViewSet,
    AllPatientesFullInfoView,
    UpdateConsultationView,
    UpdateRendezVousView,
    UpdateVaccinationView,
    RendezVousViewSet,
    VaccinationViewSet,
    CreateOtpByRfidView,
    VerifyOtpView,
    PatienteFullInfoBySearchView,
    MedecinPatientesFullInfoView
)

router = routers.DefaultRouter()
router.register(r"consultations", ConsultationViewSet, basename="consultation")
router.register(r"rendezvous", RendezVousViewSet, basename="rendezvous")
router.register(r"vaccinations", VaccinationViewSet, basename="vaccination")

urlpatterns = [
    path("", include(router.urls)),
    path("consultation/otps/create-by-rfid/", CreateOtpByRfidView.as_view(), name="otp-create-by-rfid"),
    path("consultation/otps/verify/", VerifyOtpView.as_view(), name="otp-verify"),
    path("patientes/full-info-consul-rende-vaccin/<int:hopital_id>/", AllPatientesFullInfoView.as_view(), name="all-patientes-full-info"),
    path("consultation/update/", UpdateConsultationView.as_view(), name="consultation-update"),
    path("rendezvous/update/", UpdateRendezVousView.as_view(), name="rendezvous-update"),
    path("vaccination/update/", UpdateVaccinationView.as_view(), name="vaccination-update"),
    path("patientes/search-full-info/", PatienteFullInfoBySearchView.as_view(), name="patiente-search-full-info"),
    path("users/<int:user_id>/medecin-patientes-full-info/<int:hopital_id>/", MedecinPatientesFullInfoView.as_view(), name="medecin-patientes-full-info"),
]
