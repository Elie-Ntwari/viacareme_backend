# auth_module/services/email_service.py
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError

DEFAULT_FROM = getattr(settings, "DEFAULT_FROM_EMAIL", "noreplyviacareme@gmail.com")


class EmailService:
    @staticmethod
    def _send_email(email: str, subject: str, message: str, html: bool = False):
        """
        Envoie un email. Si html=True, le message est traité comme HTML.
        """
        try:
            send_mail(
                subject,
                message,
                DEFAULT_FROM,
                [email],
                fail_silently=False,
                html_message=message if html else None
            )
        except Exception as e:
            raise ValidationError(f"Erreur envoi email: {str(e)}")

    @classmethod
    def send_activation_email(cls, email: str, code: str):
        """
        Envoie un email d'activation avec un code HTML.
        """
        subject = "Activation de votre compte VIACAREME"

        message = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Activation de compte VIACAREME</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 50px auto;
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333333;
                    font-size: 20px;
                }}
                p {{
                    color: #555555;
                    font-size: 16px;
                    line-height: 1.5;
                }}
                .code {{
                    display: block;
                    width: fit-content;
                    margin: 20px 0;
                    padding: 15px 25px;
                    font-size: 24px;
                    font-weight: bold;
                    background-color: #f0f0f0;
                    border-radius: 4px;
                    letter-spacing: 2px;
                }}
                .footer {{
                    font-size: 12px;
                    color: #888888;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Bonjour,</h1>
                <p>Bienvenue sur <strong>VIACAREME</strong> !</p>
                <p>Pour activer votre compte, utilisez le code ci-dessous :</p>
                <span class="code">{code}</span>
                <p>Ce code expirera dans <strong>15 minutes</strong>.</p>
                <p>Si vous n'avez pas demandé cette activation, vous pouvez ignorer ce message.</p>
                <p class="footer">Merci,<br>L'équipe VIACAREME</p>
            </div>
        </body>
        </html>
        """

        cls._send_email(email, subject, message, html=True)

    @classmethod
    def send_2fa_setup_email(cls, email: str, qr_url: str, provisioning_uri: str = None):
        """
        Envoie un email pour la configuration 2FA avec QR code et URI.
        """
        subject = "Configuration 2FA - JALI"
        message = (
            f"Bonjour,\n\nPour configurer Google Authenticator, scannez ce QR : {qr_url}\n"
            f"Ou utilisez cette URI : {provisioning_uri}\n\n"
            f"Conservez ce code en sécurité.\n\nCordialement,\nL'équipe JALI"
        )
        cls._send_email(email, subject, message)

    @classmethod
    def send_generic(cls, email: str, subject: str, message: str):
        """
        Envoie un email générique.
        """
        cls._send_email(email, subject, message)
