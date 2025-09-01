from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from patiente__module.permissions.patiente_permissions import IsAuthenticatedAndManagerOrSuperAdmin
from patiente__module.services.patiente_service import PatienteService
from patiente__module.serializers.patiente_serializers import PatienteCreateOrAssignSerializer, PatienteBaseSerializer


class PatienteCreateOrAssignView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedAndManagerOrSuperAdmin]

    def post(self, request):
        serializer = PatienteCreateOrAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            pat = PatienteService.create_or_assign_patiente(request.user, serializer.validated_data)
            return Response(PatienteBaseSerializer(pat).data, status=status.HTTP_201_CREATED)
        except (ValidationError, PermissionDenied) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PatienteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pats = PatienteService.list_patientes()
        return Response(PatienteBaseSerializer(pats, many=True).data)
