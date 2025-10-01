# consultation_module/serializers.py
from rest_framework import serializers
from .models import Consultation, RendezVous, Vaccination, ActionOTP
from grossesse_module.models import Grossesse

class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = "__all__"
        read_only_fields = ("otp_verifie", "created_at", "updated_at")


class RendezVousSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendezVous
        fields = "__all__"
        read_only_fields = ("otp_verifie", "created_at")


class VaccinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccination
        fields = "__all__"
        read_only_fields = ("otp_verifie", "created_at")


class ActionOtpCreateSerializer(serializers.Serializer):
    uid_rfid = serializers.CharField(required=False, allow_blank=True)
    patiente_id = serializers.IntegerField(required=False)
    action = serializers.ChoiceField(choices=[c[0] for c in ActionOTP.ACTIONS])

    def validate(self, data):
        if not data.get("patiente_id") and not data.get("uid_rfid"):
            raise serializers.ValidationError("patiente_id ou uid_rfid requis")
        return data


class ActionOtpVerifySerializer(serializers.Serializer):
    otp_id = serializers.UUIDField(required=False)   # token or id accepted
    otp_token = serializers.UUIDField(required=False)
    code = serializers.CharField(max_length=6)
    patiente_id = serializers.IntegerField()
    action = serializers.CharField()
