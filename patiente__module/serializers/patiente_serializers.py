
from rest_framework import serializers
from medical_module.models.medecin import Medecin
from hospital_module.models import Hopital
from patiente__module.models.patiente import Patiente



class CreerAHopital(serializers.ModelSerializer):
    class Meta:
        model = Hopital
        fields = ["id", "nom","email" ]

class MedecinSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    nom = serializers.CharField(source="user.nom", read_only=True)
    postnom = serializers.CharField(source="user.postnom", read_only=True)
    prenom = serializers.CharField(source="user.prenom", read_only=True)
    telephone = serializers.CharField(source="user.telephone", read_only=True)

    class Meta:
        model = Medecin
        fields = ["id", "email", "nom", "postnom", "prenom", "telephone", "specialite"]

class PatienteBaseSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    nom = serializers.CharField(source="user.nom", read_only=True)
    postnom = serializers.CharField(source="user.postnom", read_only=True)
    prenom = serializers.CharField(source="user.prenom", read_only=True)
    telephone = serializers.CharField(source="user.telephone", read_only=True)
    creer_a_hopital = CreerAHopital(read_only=True)
    medecins = MedecinSerializer(many=True, read_only=True)

    class Meta:
        model = Patiente
        fields = [
            "id", "email", "nom", "postnom", "prenom", "telephone",
            "date_naissance", "adresse", "ville", "province","has_carte","creer_a_hopital", "medecins"
        ]


class PatienteCreateOrAssignSerializer(serializers.Serializer):
    # Cas 1 : rattacher un compte existant
    existing_user_email = serializers.EmailField(required=False)

    # Cas 2 : création d’un nouveau compte user + patiente
    nom = serializers.CharField(required=False)
    postnom = serializers.CharField(required=False, allow_blank=True)
    prenom = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    telephone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    date_naissance = serializers.DateField(required=False, allow_null=True)
    adresse = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    ville = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    province = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        has_existing = bool(attrs.get("existing_user_email"))
        has_new = bool(attrs.get("email") and attrs.get("nom") and attrs.get("prenom"))
        if not (has_existing or has_new):
            raise serializers.ValidationError(
                "Fournir soit existing_user_email, soit les champs de création (nom, prenom, email)."
            )
        return attrs
