from rest_framework import serializers
from .models import Grossesse, DossierObstetrical

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
