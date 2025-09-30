from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from hospital_module.permissions import IsGestionnaireAdminLocal, IsSuperAdmin
from hospital_module.serializers import AddGestionnaireSerializer, CreateHopitalSerializer, GestionnaireSerializer, HopitalSerializer
from hospital_module.services import HopitalService


class HopitalViewSet(viewsets.ViewSet):
    @action(detail=True, methods=['put', 'patch'], url_path='update')
    def update_hopital(self, request, pk=None):
        """PUT/PATCH /api/hospitals/{id}/update/ - Modifier un hôpital"""
        hopital = HopitalService.get_hopital(pk)
        if isinstance(hopital, Response):
            return hopital
        serializer = CreateHopitalSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # Mise à jour des champs hôpital
        for attr, value in serializer.validated_data.items():
            if attr != "gestionnaire":
                setattr(hopital, attr, value)
        hopital.save()

        # Mise à jour du gestionnaire principal si fourni
        gestionnaire_data = serializer.validated_data.get("gestionnaire")
        if gestionnaire_data:
            gestionnaire = hopital.gestionnaires.filter(is_admin_local=True).first()
            if gestionnaire:
                user = gestionnaire.user
                # Met à jour les champs du user
                for field in ["nom", "postnom", "prenom", "email", "telephone"]:
                    if field in gestionnaire_data:
                        setattr(user, field, gestionnaire_data[field])
                user.save()
                # Met à jour is_admin_local si fourni
                if "is_admin_local" in gestionnaire_data:
                    gestionnaire.is_admin_local = gestionnaire_data["is_admin_local"]
                    gestionnaire.save()
        return Response({"message": "Hôpital et gestionnaire modifiés avec succès."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_hopital(self, request, pk=None):
        """DELETE /api/hospitals/{id}/delete/ - Supprimer un hôpital et son gestionnaire"""
        hopital = HopitalService.get_hopital(pk)
        if isinstance(hopital, Response):
            return hopital
        # Supprimer tous les gestionnaires liés à l'hôpital
        gestionnaires = hopital.gestionnaires.all()
        for gestionnaire in gestionnaires:
            user = gestionnaire.user
            gestionnaire.delete()
            user.delete()
        hopital.delete()
        return Response({"message": "Hôpital et tous ses gestionnaires supprimés avec succès."}, status=status.HTTP_200_OK)
    permission_classes = [IsSuperAdmin]  # Permission par défaut
  

    @action(detail=False, methods=['get'], url_path='list')
    def list_hopitaux(self, request):
        """GET /api/hospitals/list/ - liste tous les hôpitaux"""
        self.check_permissions(request)
        hopitaux = HopitalService.list_hopitaux()
        # Si hopitaux est déjà une Response (ex: aucun trouvé)
        if isinstance(hopitaux, Response):
            return hopitaux
        serializer = HopitalSerializer(hopitaux, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='retrieve')
    def retrieve_hopital(self, request, pk=None):
        """GET /api/hospitals/{id}/retrieve/ - détail d'un hôpital"""
        hopital = HopitalService.get_hopital(pk)
        if isinstance(hopital, Response):
            return hopital
        serializer = HopitalSerializer(hopital)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='create')
    def create_hopital(self, request):
        """POST /api/hospitals/create/ - créer un hôpital avec son gestionnaire"""
        serializer = CreateHopitalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hopital_data = {k: v for k, v in serializer.validated_data.items() if k != "gestionnaire"}
        gestionnaire_data = serializer.validated_data["gestionnaire"]
        response = HopitalService.create_hopital_with_gestionnaire(
            hopital_data, gestionnaire_data, request.user
        )
        return response

    @action(detail=True, methods=['post'], url_path='add-gestionnaire',permission_classes=[IsSuperAdmin|IsGestionnaireAdminLocal]
            )
    def add_gestionnaire(self, request, pk=None):
        """POST /api/hospitals/{id}/add-gestionnaire/ - Ajouter un gestionnaire à un hôpital"""
        
        hopital = HopitalService.get_hopital(pk)
       
        serializer = AddGestionnaireSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return HopitalService.add_gestionnaire(hopital, serializer.validated_data, request.user)

    @action(detail=True, methods=['get'], url_path='gestionnaires', permission_classes=[IsSuperAdmin|IsGestionnaireAdminLocal])
    def list_gestionnaires(self, request, pk=None):
        """
        GET /api/hospitals/{id}/gestionnaires/ - Liste tous les gestionnaires d'un hôpital
        Accessible par le superadmin ou un gestionnaire admin local
        """
        hopital = HopitalService.get_hopital(pk)
        if isinstance(hopital, Response):
            return hopital
        gestionnaires = hopital.gestionnaires.all()
        serializer = GestionnaireSerializer(gestionnaires, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)