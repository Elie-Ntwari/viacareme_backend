from django.db import models
from django.utils import timezone
from auth_module.models.user import User

class VerificationCode(models.Model):
    CANAL_CHOICES = (
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=10)  # OTP code ou token court
    canal = models.CharField(max_length=10, choices=CANAL_CHOICES)
    date_envoi = models.DateTimeField(default=timezone.now)
    utilise = models.BooleanField(default=False)
    expiration = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expiration

    def __str__(self):
        return f"Code {self.code} for {self.user.email} via {self.canal}"
