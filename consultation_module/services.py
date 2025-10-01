# consultation_module/services.py
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .repositories import OtpRepository, CardRepository
from .models import ActionOTP, Consultation, RendezVous, Vaccination
from auth_module.models.user import User

# TODO: implémenter send_sms/send_notification selon ta stack
def send_sms(phone, message):
    # stub - remplace par Twilio/SMSSender
    print(f"ENVOI SMS {phone}: {message}")


def create_otp_by_rfid(uid_rfid: str, action: str, expiry_minutes: int = 30):
    """
    Scan RFID -> retrouve patiente -> crée OTP -> envoie SMS -> retourne otp token/id (non code)
    """
    patiente = CardRepository.find_patiente_by_rfid(uid_rfid)
    if not patiente:
        raise ValueError("Carte non associée à une patiente")
    code = ActionOTP.generate_code()
    expire_at = timezone.now() + timedelta(minutes=expiry_minutes)
    with transaction.atomic():
        otp = OtpRepository.create(
            patiente=patiente,
            action=action,
            code=code,
            expire_at=expire_at,
            uid_rfid=uid_rfid
        )
        # send SMS to patiente.user.telephone
        phone = getattr(patiente.user, "telephone", None)
        if phone:
            send_sms(phone, f"Votre code Viacareme pour {action} est: {code}. Valable {expiry_minutes} minutes.")
        # NE PAS RENVOYER LE CODE DANS LA REPONSE API
    return otp  # contient token/id


def verify_otp(patiente_id: int, action: str, otp_token_or_id, code: str):
    """
    Vérifie l'OTP, incrémente attempts, marque used si succès.
    """
    # rechercher par token (UUID) ou id entier
    otp = None
    if isinstance(otp_token_or_id, str):
        try:
            otp = ActionOTP.objects.get(token=otp_token_or_id, patiente_id=patiente_id, action=action)
        except ActionOTP.DoesNotExist:
            otp = None
    else:
        try:
            otp = ActionOTP.objects.get(id=otp_token_or_id, patiente_id=patiente_id, action=action)
        except ActionOTP.DoesNotExist:
            otp = None

    if otp is None:
        raise ValueError("OTP introuvable")

    if otp.is_used or timezone.now() > otp.expire_at:
        raise ValueError("OTP invalide ou expiré")

    otp.attempts += 1
    otp.save(update_fields=["attempts"])

    if otp.code_otp != code:
        otp.save()
        raise ValueError(f"Code incorrect. Tentatives: {otp.attempts}")

    # succès
    otp.mark_used()
    return True
