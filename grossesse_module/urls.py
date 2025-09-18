from django.urls import path
from .views import UnlockPatiente, VerifyOTP, GrossesseListCreate, GrossesseUpdate, DossierCreateUpdate

urlpatterns = [
    path("patientes/<int:patiente_id>/unlock/", UnlockPatiente.as_view()),
    path("patientes/<int:patiente_id>/verify-otp/", VerifyOTP.as_view()),

    path("patientes/<int:patiente_id>/grossesses/", GrossesseListCreate.as_view()),
    path("grossesses/<int:id>/", GrossesseUpdate.as_view()),

    path("grossesses/<int:grossesse_id>/dossier-obstetrical/", DossierCreateUpdate.as_view()),
    path("dossier-obstetrical/<int:id>/", DossierCreateUpdate.as_view()),
]
