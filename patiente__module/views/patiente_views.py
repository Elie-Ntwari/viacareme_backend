from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated

from medical_module.permissions.medecin_permissions import IsAuthenticatedAndManagerOrSuperAdmin
from patiente__module.serializers.patiente_serializers import PatienteBaseSerializer, PatienteCreateOrAssignSerializer
from patiente__module.services.patiente_service import PatienteService


class PatienteCreateOrAssignView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedAndManagerOrSuperAdmin]

    def post(self, request, hopital_id: int):
        serializer = PatienteCreateOrAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            pat = PatienteService.create_or_assign_patiente(request.user, serializer.validated_data, hopital_id)
            return Response(PatienteBaseSerializer(pat).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)


class PatientesByHopitalView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedAndManagerOrSuperAdmin]

    def get(self, request, hopital_id: int):
        try:
            pats = PatienteService.list_patientes_by_hopital(request.user, hopital_id)
            return Response(PatienteBaseSerializer(pats, many=True).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
        
class PatienteList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pats = PatienteService.get_all_patientes()
        serializer = PatienteBaseSerializer(pats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
