# auth_app/utils/crypto.py
from cryptography.fernet import Fernet
from django.conf import settings

def _get_fernet():
    key = getattr(settings, "FERNET_KEY", None)
    if not key:
        raise RuntimeError("FERNET_KEY is not set in settings")
    return Fernet(key.encode())

def encrypt_str(plain: str) -> str:
    f = _get_fernet()
    return f.encrypt(plain.encode()).decode()

def decrypt_str(token: str) -> str:
    f = _get_fernet()
    return f.decrypt(token.encode()).decode()
