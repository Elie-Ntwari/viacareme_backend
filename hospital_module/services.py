from .repositories import HopitalRepository
from .models import Hopital, Gestionnaire
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from auth_module.models.user import User
from django.contrib.auth.hashers import make_password

class HopitalService:

    @staticmethod
    def create_hopital_with_gestionnaire(hopital_data, gestionnaire_data, creator_user):
        # Vérifier le rôle
        if creator_user.role != "SUPERADMIN":
            return Response({"error": "Seul un SUPERADMIN peut créer un hôpital."},
                            status=status.HTTP_403_FORBIDDEN)

        # Vérifier doublon hôpital
        if Hopital.objects.filter(nom__iexact=hopital_data['nom'], ville__iexact=hopital_data['ville']).exists():
            return Response({"error": f"L'hôpital '{hopital_data['nom']}' existe déjà dans la ville {hopital_data['ville']}."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Vérifier doublon email gestionnaire
        if User.objects.filter(email__iexact=gestionnaire_data['email']).exists():
            return Response({"error": f"L'utilisateur avec l'email '{gestionnaire_data['email']}' existe déjà."},
                            status=status.HTTP_400_BAD_REQUEST)
        gestDefaultPassword = "1234567890"
        #Hash password
        gestionnaire_data['password'] = make_password(gestDefaultPassword)    
        # Création via repository
        hopital, gestionnaire = HopitalRepository.create_hopital_with_gestionnaire(
            hopital_data, gestionnaire_data, creator_user
        )

        return Response({
            "message": "Hôpital et gestionnaire créés avec succès.",
            "hopital_id": hopital.id,
            "gestionnaire_id": gestionnaire.id,
            "gestionnaire_user_id": gestionnaire.user.id
        }, status=status.HTTP_201_CREATED)

    @staticmethod
    def list_hopitaux():
        hopitaux = Hopital.objects.all()
        if not hopitaux.exists():
            return Response({"message": "Aucun hôpital trouvé."}, status=status.HTTP_200_OK)
        return hopitaux

    @staticmethod
    def get_hopital(hopital_id):
        try:
            hopital = Hopital.objects.get(id=hopital_id)
            return hopital
        except Hopital.DoesNotExist:
            return Response({"error": "Hôpital introuvable."}, status=status.HTTP_404_NOT_FOUND)

    # @staticmethod
    # def add_gestionnaire(hopital, gestionnaire_data, requesting_user):
    #     # Vérifie rôle
    #     if requesting_user.role != "GESTIONNAIRE":
    #         return Response({"error": "Seul un gestionnaire peut ajouter un gestionnaire."},
    #                         status=status.HTTP_403_FORBIDDEN)

    #     # Vérifie droit admin local
    #     gestionnaire = getattr(requesting_user, "gestionnaire", None)
    #     if not gestionnaire or not gestionnaire.is_admin_local or gestionnaire.hopital != hopital:
    #         return Response({"error": "Vous n'avez pas les droits d'administration sur cet hôpital."},
    #                         status=status.HTTP_403_FORBIDDEN)

    #     # Vérifier doublon email gestionnaire
    #     if User.objects.filter(email__iexact=gestionnaire_data['email']).exists():
    #         return Response({"error": f"L'utilisateur avec l'email '{gestionnaire_data['email']}' existe déjà."},
    #                         status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def add_gestionnaire(hopital, gestionnaire_data, requesting_user):
        # Vérifier que c'est un admin local ou superadmin
        if requesting_user.role not in ["SUPERADMIN", "GESTIONNAIRE"]:
            return Response({"error": "Non autorisé."}, status=status.HTTP_403_FORBIDDEN)

        if requesting_user.role == "GESTIONNAIRE":
            try:
                gestionnaire = requesting_user.gestionnaire
            except Gestionnaire.DoesNotExist:
                return Response({"error": "Vous n'êtes pas gestionnaire."}, status=status.HTTP_403_FORBIDDEN)

            if not gestionnaire.is_admin_local or gestionnaire.hopital_id != hopital.id:
                return Response({"error": "Vous n'avez pas les droits pour ajouter un gestionnaire ici."}, 
                                status=status.HTTP_403_FORBIDDEN)

        # Vérifier doublon email
        if User.objects.filter(email__iexact=gestionnaire_data["email"]).exists():
            return Response({"error": f"L'utilisateur {gestionnaire_data['email']} existe déjà."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        gestDefaultPassword = "1234567890"
        # Créer l'utilisateur
        user = User.objects.create(
            nom=gestionnaire_data["nom"],
            postnom=gestionnaire_data["postnom"],
            prenom=gestionnaire_data["prenom"],
            email=gestionnaire_data["email"].lower(),
            telephone=gestionnaire_data.get("telephone"),
            password=make_password(gestDefaultPassword),
            role="GESTIONNAIRE",
            est_actif=True,
            est_verifie=True
        )

        # Lier à l’hôpital
        gestionnaire = Gestionnaire.objects.create(
            user=user,
            hopital=hopital,
            is_admin_local=gestionnaire_data.get("is_admin_local", False)
        )

        return Response({
            "message": "Gestionnaire ajouté avec succès.",
            "gestionnaire_id": gestionnaire.id,
            "user_id": user.id,
            "hopital_id": hopital.id
        }, status=status.HTTP_201_CREATED)