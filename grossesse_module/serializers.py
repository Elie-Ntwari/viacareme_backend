from rest_framework import serializers
from .models import Grossesse, DossierObstetrical, ClotureGrossesse

class GrossesseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grossesse
        fields = "id","date_debut","dpa","statut"
        read_only_fields = ("id", "created_at")


class DossierObstetricalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierObstetrical
        fields = "__all__"
        read_only_fields = ("id", "grossesse")


class ClotureGrossesseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClotureGrossesse
        fields = [
            "id", "date_accouchement", "nombre_enfants", "genre_enfant",
            "poids_naissance", "taille_naissance", "type_accouchement",
            "issue_grossesse", "complications", "observations",
            "duree_travail", "created_at"
        ]
        read_only_fields = ("id", "created_at", "grossesse", "created_by")

    def validate_nombre_enfants(self, value):
        if value < 1:
            raise serializers.ValidationError("Le nombre d'enfants doit être au moins 1")
        return value

    def validate_poids_naissance(self, value):
        if value is not None and (value < 0.5 or value > 10):
            raise serializers.ValidationError("Le poids doit être entre 0.5 et 10 kg")
        return value

    def validate_taille_naissance(self, value):
        if value is not None and (value < 20 or value > 70):
            raise serializers.ValidationError("La taille doit être entre 20 et 70 cm")
        return value


class GrossesseClotureSerializer(serializers.Serializer):
    """Serializer pour la clôture de grossesse avec informations détaillées"""
    statut = serializers.CharField()
    cloture_info = ClotureGrossesseSerializer(required=False)
    
    def validate_statut(self, value):
        from .models import Grossesse
        if value not in dict(Grossesse.STATUTS):
            raise serializers.ValidationError("Statut invalide")
        return value
    
    def validate(self, data):
        # Si le statut est TERMINEE, les informations de clôture sont obligatoires
        if data.get('statut') == 'TERMINEE' and not data.get('cloture_info'):
            raise serializers.ValidationError({
                'cloture_info': 'Les informations de clôture sont obligatoires pour terminer une grossesse'
            })
        return data
