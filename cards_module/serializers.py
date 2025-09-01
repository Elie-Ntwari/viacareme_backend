# cards_module/serializers.py
from rest_framework import serializers
from .models import Device, RegistreCarte, LotCarte, LotCarteDetail, SessionScan

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"

class RegistreCarteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistreCarte
        read_only_fields = ("numero_serie", "date_enregistrement", "enregistre_par_user")
        fields = "__all__"

class LotCarteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LotCarte
        fields = "__all__"

class LotCarteDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LotCarteDetail
        fields = "__all__"

# class CarteAttribueeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CarteAttribuee
#         fields = "__all__"

class SessionScanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionScan
        read_only_fields = ("token", "statut", "created_at")
        fields = ("id", "type", "cible_id", "hopital", "device", "lance_par_user", "expires_at", "token", "statut")

class SessionScanDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionScan
        fields = "__all__"
