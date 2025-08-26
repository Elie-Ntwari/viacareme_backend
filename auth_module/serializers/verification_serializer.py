from rest_framework import serializers
from django.utils import timezone
from auth_module.models.verification_code import VerificationCode

class VerificationCodeSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True)

    class Meta:
        model = VerificationCode
        fields = ['id', 'user', 'code', 'canal', 'date_envoi', 'utilise', 'expiration']
        read_only_fields = ['id', 'user', 'date_envoi', 'utilise', 'expiration', 'canal']

    def validate_code(self, value):
        if len(value) != 6 or not value.isdigit():
            raise serializers.ValidationError("Le code doit être un code numérique de 6 chiffres.")
        return value

    def validate(self, data):
        user = self.context.get('user')  # on peut passer user dans le contexte depuis la vue
        canal = data.get('canal', 'EMAIL')  # par défaut 'EMAIL' si non passé

        # On cherche le code dans la base
        try:
            vc = VerificationCode.objects.get(
                user=user,
                code=data['code'],
                canal=canal,
                utilise=False,
            )
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError("Code invalide ou déjà utilisé.")

        if vc.is_expired():
            raise serializers.ValidationError("Le code est expiré.")

        # On peut mettre l'instance dans le validated_data pour la récupérer plus tard si besoin
        data['verification_instance'] = vc
        return data
