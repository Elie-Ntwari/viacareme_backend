# auth_module/models/totp_setup_token.py
from django.db import models
from django.utils import timezone
from datetime import timedelta

class TOTPSetupToken(models.Model):
    token = models.CharField(max_length=64, unique=True)
    encrypted_secret = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    @classmethod
    def clean_expired(cls):
        cls.objects.filter(expires_at__lt=timezone.now()).delete()

    def is_expired(self):
        return timezone.now() > self.expires_at
