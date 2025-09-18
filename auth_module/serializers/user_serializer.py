from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from auth_module.models.user import User

# Fonction utilitaire pour valider les codes à 6 chiffres
def validate_code(value: str) -> str:
    if not value.isdigit() or len(value) != 6:
        raise serializers.ValidationError("Le code doit être un nombre à 6 chiffres.")
    return value


class UserFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Tous les champs utiles, mais pas le mot de passe ni totp_secret
        fields = [
            "id",
            "nom",
            "postnom",
            "prenom",
            "email",
            "telephone",
            "photo_url",
            "role",
            "date_creation",
        ]
        
class AddNewUserSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=150)
    postnom = serializers.CharField(max_length=150)
    prenom = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    telephone = serializers.CharField(
        max_length=20, required=False, allow_null=True, allow_blank=True
    )
    photo_file = serializers.ImageField(required=False, allow_null=True)
    role = serializers.ChoiceField(
        choices=["SUPERADMIN", "GESTIONNAIRE", "MEDECIN", "PATIENTE"], 
        default="GESTIONNAIRE"
    )

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_nom(self, value: str) -> str:
        return value.strip().title()

    def validate_postnom(self, value: str) -> str:
        return value.strip().title()

    def validate_prenom(self, value: str) -> str:
        return value.strip().title()



class RegisterUserSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=150)
    postnom = serializers.CharField(max_length=150)
    prenom = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    telephone = serializers.CharField(
        max_length=20, required=False, allow_null=True, allow_blank=True
    )
    photo_file = serializers.ImageField(required=False, allow_null=True)
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=["SUPERADMIN", "GESTIONNAIRE", "MEDECIN", "PATIENTE"], 
        default="SUPERADMIN"
    )

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_nom(self, value: str) -> str:
        return value.strip().title()

    def validate_postnom(self, value: str) -> str:
        return value.strip().title()

    def validate_prenom(self, value: str) -> str:
        return value.strip().title()

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value


class ActivateAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_code(self, value: str) -> str:
        return validate_code(value)


class InitiateLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

class Confirm2FASerializer(serializers.Serializer):
    email = serializers.EmailField()
    setup_token = serializers.CharField()
    totp_code = serializers.CharField(max_length=6)

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_totp_code(self, value: str) -> str:
        # Ici tu peux mettre une fonction de validation comme validate_code
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Le code TOTP doit être un nombre à 6 chiffres.")
        return value

class FinalizeLogin2FASerializer(serializers.Serializer):
    email = serializers.EmailField()
    totp_code = serializers.CharField(max_length=6)

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_totp_code(self, value: str) -> str:
        return validate_code(value)
