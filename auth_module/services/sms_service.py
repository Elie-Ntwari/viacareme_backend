# auth_module/services/sms_service.py
from django.conf import settings
from django.core.exceptions import ValidationError
from sms_sender.services import send_sms_via_md

DEFAULT_SENDER_ID = getattr(settings, "MD_SMS_SENDER_ID", "VIACAREME")


class SMSService:
    @staticmethod
    def _send_sms(phone: str, message: str, sender_id: str = None):
        """
        Envoie un SMS via l'API MD SMS.
        """
        if not sender_id:
            sender_id = DEFAULT_SENDER_ID

        result = send_sms_via_md(
            message=message,
            mobile_numbers=phone,
            sender_id=sender_id
        )

        if not result.get("success"):
            error_type = result.get("error_type")
            if error_type == "api_error":
                raise ValidationError(f"Erreur API SMS: {result.get('api_error_description')} (code {result.get('api_error_code')})")
            elif error_type == "timeout":
                raise ValidationError("Timeout envoi SMS")
            elif error_type == "connection":
                raise ValidationError("Erreur de connexion au service SMS")
            else:
                raise ValidationError(f"Erreur envoi SMS: {result.get('error')}")

    @classmethod
    def send_activation_sms(cls, phone: str, code: str):
        """
        Envoie un SMS d'activation avec le code.
        """
        message = f"Votre code d'activation VIACAREME est: {code}. Valide 15 minutes."
        cls._send_sms(phone, message)

    @classmethod
    def send_generic_sms(cls, phone: str, message: str):
        """
        Envoie un SMS générique.
        """
        cls._send_sms(phone, message)