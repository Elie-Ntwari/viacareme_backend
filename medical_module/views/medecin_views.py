
# ==============================
# views/medecin_views.py
# ==============================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError, PermissionDenied
from medical_module.permissions.medecin_permissions import IsAuthenticatedAndManagerOrSuperAdmin
from medical_module.services.medecin_service import MedecinService
from medical_module.serializers.medecin_serializers import (
    MedecinCreateOrAssignSerializer,
    MedecinBaseSerializer,
    MedecinDetailSerializer,
)


class MedecinCreateOrAssignView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedAndManagerOrSuperAdmin]

    def post(self, request):
        serializer = MedecinCreateOrAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            med = MedecinService.create_or_assign_medecin(request.user, serializer.validated_data)
            return Response(MedecinDetailSerializer(med).data, status=status.HTTP_201_CREATED)
        except (ValidationError, PermissionDenied) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MedecinsByHopitalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, hopital_id: int):
        try:
            meds = MedecinService.list_medecins_by_hopital(hopital_id)
            return Response(MedecinBaseSerializer(meds, many=True).data)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MedecinListPaginatedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # renvoie directement une Response paginée
        return MedecinService.list_medecins_paginated(request)


class RemoveAffectationView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedAndManagerOrSuperAdmin]

    def delete(self, request, medecin_id: int, hopital_id: int):
        try:
            removed = MedecinService.remove_affectation(request.user, medecin_id, hopital_id)
            if removed:
                return Response({"message": "Affectation supprimée."}, status=status.HTTP_200_OK)
            return Response({"detail": "Affectation introuvable."}, status=status.HTTP_404_NOT_FOUND)
        except (ValidationError, PermissionDenied) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

