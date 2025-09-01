from .models import Hopital, Gestionnaire
from auth_module.repositories.user_repository import UserRepository
from django.db import transaction

class HopitalRepository:

    @staticmethod
    @transaction.atomic
    def create_hopital_with_gestionnaire(hopital_data, gestionnaire_data, creator_user):
        # Création du User gestionnaire
        user = UserRepository.create_user(
            nom=gestionnaire_data['nom'],
            postnom=gestionnaire_data.get('postnom', ''),
            prenom=gestionnaire_data['prenom'],
            email=gestionnaire_data['email'],
            telephone=gestionnaire_data.get('telephone'),
            password=gestionnaire_data['password'],
            role="GESTIONNAIRE",
            est_actif=True,
            est_verifie=True
        )

        # Création de l'hôpital
        hopital = Hopital.objects.create(
            nom=hopital_data['nom'],
            adresse=hopital_data['adresse'],
            ville=hopital_data['ville'],
            province=hopital_data['province'],
            telephone=hopital_data.get('telephone'),
            email=hopital_data.get('email'),
            latitude=hopital_data.get('latitude'),
            longitude=hopital_data.get('longitude'),
            cree_par_user=creator_user
        )

        # Lier gestionnaire
        gestionnaire = Gestionnaire.objects.create(
            user=user,
            hopital=hopital,
            is_admin_local=True
        )

        return hopital, gestionnaire

    @staticmethod
    def add_gestionnaire(hopital, gestionnaire_data):
        user = UserRepository.create_user(
            nom=gestionnaire_data['nom'],
            postnom=gestionnaire_data.get('postnom', ''),
            prenom=gestionnaire_data['prenom'],
            email=gestionnaire_data['email'],
            telephone=gestionnaire_data.get('telephone'),
            password=gestionnaire_data['password'],
            role="GESTIONNAIRE",
            est_actif=True,
            est_verifie=True
        )
        gestionnaire = Gestionnaire.objects.create(
            user=user,
            hopital=hopital,
            is_admin_local=True
        )
        return gestionnaire
    

    @staticmethod
    def get_by_id(hopital_id):
        try:
            return Hopital.objects.get(id=hopital_id)
        except Hopital.DoesNotExist:
            return None
