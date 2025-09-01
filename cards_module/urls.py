# cards_module/urls.py
from django.urls import path
from .views import StartScanSessionView, ReceiveScanView, CreateLotView

urlpatterns = [
    path("cards/session/start/", StartScanSessionView.as_view(), name="start_session"),
    path("cards/scan/", ReceiveScanView.as_view(), name="receive_scan"),
    path("cards/lots/", CreateLotView.as_view(), name="create_lot"),
]
