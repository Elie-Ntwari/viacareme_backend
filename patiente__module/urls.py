from django.urls import path
from patiente__module.views.patiente_views import PatienteCreateOrAssignView, PatienteListView

urlpatterns = [
    path("patientes/create-or-assign", PatienteCreateOrAssignView.as_view(), name="patiente-create-assign"),
    path("patientes", PatienteListView.as_view(), name="patientes-list"),
]
