from rest_framework import serializers
from .models import Hopital, Gestionnaire
from auth_module.models.user import User
from auth_module.services.user_service import UserService

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nom", "postnom", "prenom", "email", "telephone", "photo_url", "role"]

class GestionnaireSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    class Meta:
        model = Gestionnaire
        fields = ["id","is_admin_local","user",]

class HopitalSerializer(serializers.ModelSerializer):
    gestionnaires = GestionnaireSerializer(many=True, read_only=True)
    
    class Meta:
        model = Hopital
        fields = "__all__"

class CreateHopitalSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=255)
    adresse = serializers.CharField(max_length=255)
    ville = serializers.CharField(max_length=100)
    province = serializers.CharField(max_length=100)
    telephone = serializers.CharField(max_length=20, required=False)
    email = serializers.EmailField(required=False)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    gestionnaire = serializers.DictField()  # nom, postnom, prenom, email, password, telephone
