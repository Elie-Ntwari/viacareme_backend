import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail

from grossesse_module.models import DossierAccess
   
from django.core.mail import EmailMultiAlternatives

class OTPService:
    
        
    @staticmethod
    def envoyer_mail_otp(patiente, code):
        subject = "Votre code de vérification Viacareme"
        from_email = "no-reply@viacareme.org"
        to = [patiente.user.email]

        text_content = f"""
        Bonjour {patiente.user.prenom},

        Voici votre code de vérification Viacareme : {code}.
        Ce code est valable pendant 24 heures.

        Il sert à confirmer votre identité et sécuriser l’accès à vos informations médicales.

        L’équipe Viacareme
        """

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f9ff; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: white; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); padding: 20px;">
            <h2 style="color: #0056b3; text-align: center;">🔐 Vérification Viacareme</h2>
            <p style="font-size: 16px; color: #333;">Bonjour <strong>{patiente.user.prenom}</strong>,</p>
            <p style="font-size: 15px; color: #333;">
                Voici votre code de vérification pour accéder à votre espace santé :
            </p>
            <div style="text-align: center; margin: 20px 0;">
                <span style="font-size: 26px; font-weight: bold; color: #009688; background: #e6f7f4; padding: 12px 25px; border-radius: 8px; display: inline-block;">
                {code}
                </span>
            </div>
            <p style="font-size: 14px; color: #555;">
                ✅ Ce code est valable <strong>24 heures</strong>.<br>
                ✅ Il permet de confirmer votre identité et de sécuriser l’accès à vos données médicales.<br>
            </p>
            <p style="font-size: 14px; color: #777; text-align: center; margin-top: 30px;">
                Merci d’utiliser <strong>Viacareme</strong>, votre partenaire pour une maternité plus sûre.
            </p>
            </div>
        </body>
        </html>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()


    @staticmethod
    def generate_otp(patiente):
        
        if patiente.acces_dossier.filter(is_used=False, expire_at__gt=timezone.now()).exists():
            raise ValueError("Un code OTP valide existe déjà pour cette patiente.") 
        
        if not patiente.has_carte:
            raise ValueError("La patiente ne possède pas une carte de santé active.")
        
        code = str(random.randint(100000, 999999))
        expire_at = timezone.now() + timedelta(hours=24)
        access = DossierAccess.objects.create(
            patiente=patiente, code_otp=code, expire_at=expire_at
        )
        OTPService.envoyer_mail_otp(patiente, code)
        return access

    @staticmethod
    def verify_otp(patiente, code):
        
        if not patiente.has_carte:
            raise ValueError("La patiente ne possède pas une carte de santé active.")
        try:
            access = DossierAccess.objects.filter(
                patiente=patiente, code_otp=code, is_used=False
            ).latest("created_at")
        except DossierAccess.DoesNotExist:
            return False
        if access.is_valid():
            access.is_used = True
            access.save()
            return True
        return False
