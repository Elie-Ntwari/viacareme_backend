# cards_module/repositories.py
from .models import RegistreCarte, SessionScan, LotCarteDetail, LotCarte
from django.utils import timezone

class RegistreRepository:
    @staticmethod
    def get_by_uid(uid):
        try:
            return RegistreCarte.objects.get(uid_rfid=uid)
        except RegistreCarte.DoesNotExist:
            return None
        
    @staticmethod
    def get_available_for_delivery():
        # toutes les cartes ENREGISTREE et non encore LIVREE pour cet hôpital
        return list(RegistreCarte.objects.filter(
            statut="ENREGISTREE",
         
        ))


    @staticmethod
    def create(uid, user=None, est_viacareme=False):
        # numero_serie interne généré simple
        numero = f"VC-{int(timezone.now().timestamp())}-{uid[-4:]}"
        return RegistreCarte.objects.create(numero_serie=numero, uid_rfid=uid, enregistre_par_user=user, est_viacareme=est_viacareme)

class SessionRepository:
    @staticmethod
    def get_valid_by_token(token):
        try:
            s = SessionScan.objects.get(token=token)
        except SessionScan.DoesNotExist:
            return None
        if s.is_valid():
            return s
        return None

class LotRepository:
    @staticmethod
    def add_detail(lot: LotCarte, registre):
        return LotCarteDetail.objects.create(lot=lot, registre=registre)
