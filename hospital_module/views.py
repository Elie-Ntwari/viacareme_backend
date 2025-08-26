from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from hospital_module.permissions import IsGestionnaireAdminLocal, IsSuperAdmin
from hospital_module.serializers import CreateHopitalSerializer, HopitalSerializer
from hospital_module.services import HopitalService


class HopitalViewSet(viewsets.ViewSet):
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

    @action(detail=True, methods=['post'], url_path='add-manager', permission_classes=[IsGestionnaireAdminLocal])
    def add_manager(self, request, pk=None):
        """POST /api/hospitals/{id}/add-manager/ - ajouter un gestionnaire à un hôpital"""
        hopital = HopitalService.get_hopital(pk)
        if isinstance(hopital, Response):
            return hopital
        serializer = CreateHopitalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        gestionnaire_data = serializer.validated_data.get("gestionnaire")
        response = HopitalService.add_gestionnaire(hopital, gestionnaire_data, request.user)
        return response
