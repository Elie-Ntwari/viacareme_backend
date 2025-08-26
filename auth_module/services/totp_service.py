# auth_module/services/totp_service.py
from auth_module.models.user import User
import pyotp
import qrcode
import io
import secrets
from typing import Dict
from django.conf import settings
from django.utils import timezone
import cloudinary.uploader
from django.core.exceptions import ValidationError
from datetime import timedelta

from auth_module.models.totp_setup_token import TOTPSetupToken
from auth_module.utils.crypto import encrypt_str, decrypt_str

ISSUER_NAME = getattr(settings, "TOTP_ISSUER_NAME", "JALI")
TOTP_SETUP_TTL_SECONDS = getattr(settings, "TOTP_SETUP_TTL_SECONDS", 10 * 60)
QR_UPLOAD_FOLDER = getattr(settings, "TOTP_QR_FOLDER", "jali_images/users/2fa_qr")

class TOTPService:
    @staticmethod
    def generate_secret() -> str:
        return pyotp.random_base32()

    @staticmethod
    def provisioning_uri(secret: str, email: str, issuer: str = ISSUER_NAME) -> str:
        return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)

    @staticmethod
    def _upload_qr_image_from_uri(uri: str, email: str) -> str:
        img = qrcode.make(uri)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        public_id = f"{QR_UPLOAD_FOLDER}/{email.replace('@', '_')}_{int(timezone.now().timestamp())}"
        try:
            upload_result = cloudinary.uploader.upload(
                buf,
                folder=QR_UPLOAD_FOLDER,
                public_id=public_id,
                overwrite=True,
                resource_type="image"
            )
            return upload_result.get("secure_url")
        except Exception as e:
            raise ValidationError(f"Erreur upload QR Cloudinary: {str(e)}")

    @staticmethod
    def start_totp_setup(email: str) -> Dict[str, str]:
        # Nettoyage des anciens
        TOTPSetupToken.clean_expired()

        secret = TOTPService.generate_secret()
        uri = TOTPService.provisioning_uri(secret, email)
        qr_url = TOTPService._upload_qr_image_from_uri(uri, email)

        setup_token = secrets.token_urlsafe(32)
        encrypted_secret = encrypt_str(secret)

        TOTPSetupToken.objects.create(
            token=setup_token,
            encrypted_secret=encrypted_secret,
            expires_at=timezone.now() + timedelta(seconds=TOTP_SETUP_TTL_SECONDS)
        )

        return {"provisioning_uri": uri, "qr_url": qr_url, "setup_token": setup_token}

    @staticmethod
    def confirm_totp_setup(user, setup_token: str, totp_code: str) -> bool:
        try:
            token_obj = TOTPSetupToken.objects.get(token=setup_token)
        except TOTPSetupToken.DoesNotExist:
            raise ValidationError("Setup token invalide ou expiré.")

        if token_obj.is_expired():
            token_obj.delete()
            raise ValidationError("Setup token expiré. Recommencez la configuration.")

        try:
            secret = decrypt_str(token_obj.encrypted_secret)
        except Exception:
            token_obj.delete()
            raise ValidationError("Impossible de récupérer la clé TOTP.")

        if not pyotp.TOTP(secret).verify(totp_code, valid_window=1):
            raise ValidationError("Code TOTP invalide.")

        user.set_totp_secret(secret)
        user.deux_facteurs_active = True
        user.save()

        token_obj.delete()
        return True

    @staticmethod
    def verify_code(secret: str, code: str) -> bool:
       totp = pyotp.TOTP(secret)
       return totp.verify(code)
