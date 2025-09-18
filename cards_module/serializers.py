# cards_module/serializers.py
from rest_framework import serializers

from hospital_module.models import Hopital
from .models import CarteAttribuee, Device, RegistreCarte, LotCarte, LotCarteDetail, SessionScan

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"

class RegistreCarteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistreCarte
        read_only_fields = ("numero_serie", "date_enregistrement", "enregistre_par_user")
        fields = "__all__"
class HopitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hopital
        fields = "__all__"

class LotCarteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LotCarte
        fields = "__all__"
# serializers.py

class RegistreCarteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistreCarte
        fields = ["id", "uid_rfid", "statut", "date_enregistrement"]


class LotCarteDetailSerializer(serializers.ModelSerializer):
    registre = RegistreCarteSerializer()

    class Meta:
        model = LotCarteDetail
        fields = ["id", "registre"]


class LotCarteHistoriqueSerializer(serializers.ModelSerializer):
    hopital = HopitalSerializer()
    livre_par_user = serializers.StringRelatedField()
    details = LotCarteDetailSerializer(many=True)

    class Meta:
        model = LotCarte
        fields = [
            "id",
            "numero_lot",
            "date_livraison",
            "hopital",
            "livre_par_user",
            "details",
        ]



class SessionScanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionScan
        read_only_fields = ("token", "statut", "created_at")
        fields = ("id", "type", "cible_id", "hopital", "device", "lance_par_user", "expires_at", "token", "statut")

class SessionScanDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionScan
        fields = "__all__"


class CarteAttribueeSerializer(serializers.ModelSerializer):
    carte_uid = serializers.CharField(source="carte.uid_rfid", read_only=True)
    patiente_nom = serializers.CharField(source="patiente.user.nom", read_only=True)
    patiente_prenom = serializers.CharField(source="patiente.user.prenom", read_only=True)

    class Meta:
        model = CarteAttribuee
        fields = [
            "id",
            "carte_uid",
            "patiente_nom",
            "patiente_prenom",
            "hopital",
            "attribuee_par",
            "date_attribution",
        ]


