# cards_module/urls.py
from django.urls import path
from .views import AttribuerCarteView, ListAVailableCardsViewByHopital, ListLivreeCardsViewByHopital, LotHistoriqueView, StartScanSessionView, ReceiveScanView, CreateLotView

urlpatterns = [
    path("cards/session/start/", StartScanSessionView.as_view(), name="start_session"),
    path("cards/scan/", ReceiveScanView.as_view(), name="receive_scan"),
    path("cards/lots/", CreateLotView.as_view(), name="create_lot"),
    path("cards/lots/history/", LotHistoriqueView.as_view(), name="lot_history"),
    path("cards/",ListAVailableCardsViewByHopital.as_view(), name="list_available_cards_by_hopital"),  
    path("cards/<int:hopital_id>/available/",ListLivreeCardsViewByHopital.as_view(), name="list_available_cards_by_hopital"),
    path("cards/deliver/",AttribuerCarteView.as_view(), name="delivered_cards"),
]
