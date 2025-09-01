from uuid import UUID
from django.shortcuts import render

# Create your views here.
# cards_module/views.py
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from hospital_module.models import Hopital
from .serializers import SessionScanCreateSerializer, SessionScanDetailSerializer, RegistreCarteSerializer, LotCarteSerializer
from .services import SessionService, CardService, LotService
from .models import Device, SessionScan, RegistreCarte, LotCarte
from auth_module.models.user import User
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

# permission helpers
def is_superadmin(user):
    return user.role == "SUPERADMIN"

def is_gestionnaire(user):
    return user.role == "GESTIONNAIRE"

class StartScanSessionView(APIView):
    permission_classes = [IsAuthenticated]
    """
    POST /api/cards/session/start/
    body: { "type": "ENREGISTREMENT" | "ATTRIBUTION", "device_id": X, "hopital_id": Y, "cible_id": Z (opt) }
    """
    def post(self, request):
        user = request.user
        typ = request.data.get("type")
        device_id = request.data.get("device_id")
        hopital_id = request.data.get("hopital_id")
        cible_id = request.data.get("cible_id", None)

        # role check
        if typ == "ENREGISTREMENT" and not is_superadmin(user):
            return Response({"detail": "Accès refusé"}, status=status.HTTP_403_FORBIDDEN)
        if typ == "ATTRIBUTION" and not is_gestionnaire(user):
            return Response({"detail": "Accès refusé"}, status=status.HTTP_403_FORBIDDEN)

        device = get_object_or_404(Device, id=device_id, actif=True)
        hopital = get_object_or_404(Hopital, id=hopital_id, actif=True)  # ✅ on récupère l’objet

        # create session
        session = SessionService.create_session(
            type=typ,
            hopital=hopital,  # ✅ on passe bien l’objet
            device=device,
            user=user,
            cible_id=cible_id
        )

        serializer = SessionScanDetailSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


class ReceiveScanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")
        uid = request.data.get("uid")
        device_id = request.data.get("device_id")

        # Vérifier que le token est un UUID valide
        try:
            UUID(token, version=4)
        except (ValueError, TypeError):
            return Response({"detail": "Token invalide, doit être un UUID."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Vérifier que device_id est un entier
        try:
            device_id = int(device_id)
        except (ValueError, TypeError):
            return Response({"detail": "device_id invalide."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Récupération du device
        device = Device.objects.filter(id=device_id, actif=True).first()
        if not device:
            return Response({"detail": "Device introuvable ou inactif."},
                            status=status.HTTP_404_NOT_FOUND)

        # Appel du service
        return CardService.handle_scan(token, uid, device)

class CreateLotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not is_superadmin(user) and not is_gestionnaire(user):
            return Response({"message": "Accès refusé"}, status=status.HTTP_403_FORBIDDEN)

        numero_lot = request.data.get("numero_lot")
        hopital_id = request.data.get("hopital_id")
        nombre_cartes = request.data.get("nombre_cartes", 0)

        if nombre_cartes <= 0:
            return Response({"message": "Le nombre de cartes doit être supérieur à zéro."},
                            status=status.HTTP_400_BAD_REQUEST)

        lot, error, cartes_uids = LotService.create_lot_by_count(numero_lot, hopital_id, user, nombre_cartes)
        if error:
            return Response({"message": error}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "lot_id": lot.id,
            "numero_lot": lot.numero_lot,
            "cartes_uids": cartes_uids,
            "status": "success"
        }, status=status.HTTP_201_CREATED)
