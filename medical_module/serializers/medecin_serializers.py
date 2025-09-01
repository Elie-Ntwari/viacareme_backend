
# ==============================
# serializers/medecin_serializers.py
# ==============================
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from auth_module.models.user import User
from medical_module.models.medecin import Medecin, MedecinHopital
from hospital_module.models import Hopital, Gestionnaire


DEFAULT_MEDECIN_PASSWORD = "1234567890"


class MedecinBaseSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    nom = serializers.CharField(source="user.nom", read_only=True)
    postnom = serializers.CharField(source="user.postnom", read_only=True)
    prenom = serializers.CharField(source="user.prenom", read_only=True)
    telephone = serializers.CharField(source="user.telephone", read_only=True)

    class Meta:
        model = Medecin
        fields = [
            "id", "email", "nom", "postnom", "prenom", "telephone", "specialite"
        ]


class MedecinCreateOrAssignSerializer(serializers.Serializer):
    # Cas 1: rattacher un compte existant
    existing_user_email = serializers.EmailField(required=False)

    # Cas 2: créer un nouveau compte médecin
    nom = serializers.CharField(required=False)
    postnom = serializers.CharField(required=False, allow_blank=True)
    prenom = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    telephone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    specialite = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # ciblage hôpital obligatoire
    hopital_id = serializers.IntegerField()

    def validate(self, attrs):
        has_existing = bool(attrs.get("existing_user_email"))
        has_new = bool(attrs.get("email") and attrs.get("nom") and attrs.get("prenom"))
        if not (has_existing or has_new):
            raise serializers.ValidationError(
                "Fournir soit existing_user_email, soit les champs de création (nom, prenom, email)."
            )
        return attrs


class MedecinDetailSerializer(MedecinBaseSerializer):
    hopitaux = serializers.SerializerMethodField()

    def get_hopitaux(self, obj: Medecin):
        return [
            {
                "id": mh.hopital.id,
                "nom": mh.hopital.nom,
                "ville": mh.hopital.ville,
                "province": mh.hopital.province,
                "date_affectation": mh.date_affectation.isoformat(),
            }
            for mh in obj.affectations.select_related("hopital").all()
        ]

    class Meta(MedecinBaseSerializer.Meta):
        fields = MedecinBaseSerializer.Meta.fields + ["hopitaux"]


class MedecinHopitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedecinHopital
        fields = ["id", "medecin", "hopital", "date_affectation"]
