# consultation_module/repositories.py
from django.utils import timezone
from .models import ActionOTP, Consultation, RendezVous, Vaccination
from cards_module.models import RegistreCarte, CarteAttribuee

class OtpRepository:
    @staticmethod
    def create( patiente, action, code, expire_at, created_par=None, uid_rfid=None):
        return ActionOTP.objects.create(
            patiente=patiente,
            action=action,
            code_otp=code,
            expire_at=expire_at,
            uid_rfid=uid_rfid
        )

    @staticmethod
    def get_by_token(token):
        try:
            return ActionOTP.objects.get(token=token)
        except ActionOTP.DoesNotExist:
            return None

    @staticmethod
    def get_by_id(id):
        try:
            return ActionOTP.objects.get(id=id)
        except ActionOTP.DoesNotExist:
            return None

class CardRepository:
    @staticmethod
    def find_patiente_by_rfid(uid_rfid):
        try:
            reg = RegistreCarte.objects.get(uid_rfid=uid_rfid)
        except RegistreCarte.DoesNotExist:
            return None
        try:
            attrib = reg.attribution  # OneToOne via CarteAttribuee
            return attrib.patiente
        except Exception:
            return None
