from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Grossesse, DossierObstetrical
from patiente__module.models.patiente import Patiente
from .serializers import GrossesseSerializer, DossierObstetricalSerializer, GrossesseClotureSerializer, ClotureGrossesseSerializer
from .services.otp_service import OTPService
from .services.grossesse_service import GrossesseService, DossierService

class UnlockPatiente(APIView):
 

    def post(self, request, patiente_id):
        try:
            patiente = get_object_or_404(Patiente, id=patiente_id)
            access = OTPService.generate_otp(patiente)
            return Response({"message": "Code envoyé par email"}, status=200)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)  

class VerifyOTP(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, patiente_id):
        try:
            patiente = get_object_or_404(Patiente, id=patiente_id)
            code = request.data.get("code")
            if OTPService.verify_otp(patiente, code):
                return Response({"message": "Accès accordé pour 24h"}, status=200)
            return Response({"error": "Code invalide ou expiré"}, status=400)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        


class GrossesseListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, patiente_id):
        try:
            patiente = get_object_or_404(Patiente, id=patiente_id)
            serializer = GrossesseSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            grossesse = GrossesseService.create_grossesse(request.user, patiente, serializer.validated_data)
            return Response(GrossesseSerializer(grossesse).data, status=201)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

    def get(self, request, patiente_id):
        try:
            patiente = get_object_or_404(Patiente, id=patiente_id)
            grossesses = patiente.grossesses.select_related("dossier").all()
            return Response(GrossesseSerializer(grossesses, many=True).data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)


class GrossesseUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        try:
            grossesse = get_object_or_404(Grossesse, id=id)
            serializer = GrossesseSerializer(grossesse, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated = GrossesseService.update_grossesse(request.user, grossesse, serializer.validated_data)
            return Response(GrossesseSerializer(updated).data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

class GrosseSetState(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, id):
        try:
            grossesse = get_object_or_404(Grossesse, id=id)
            
            # Utiliser le nouveau serializer pour valider les données
            serializer = GrossesseClotureSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            validated_data = serializer.validated_data
            new_statut = validated_data.get("statut")
            cloture_data = validated_data.get("cloture_info")
            
            # Appeler le service avec les données de clôture si nécessaire
            updated = GrossesseService.set_grossesse_state(
                request.user,
                grossesse,
                new_statut,
                cloture_data
            )
            
            # Préparer la réponse avec les informations de clôture si disponibles
            response_data = GrossesseSerializer(updated).data
            
            # Si la grossesse a été terminée, inclure les informations de clôture
            if new_statut == "TERMINEE" and hasattr(updated, 'cloture'):
                response_data['cloture'] = ClotureGrossesseSerializer(updated.cloture).data
            
            return Response(response_data)
            
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Une erreur inattendue s'est produite"}, status=500)


class DossierCreateUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, grossesse_id):
        try:
            grossesse = get_object_or_404(Grossesse, id=grossesse_id)
            serializer = DossierObstetricalSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            dossier = DossierService.create_dossier(request.user, grossesse, serializer.validated_data)
            return Response(DossierObstetricalSerializer(dossier).data, status=201)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

    def put(self, request, id):
        try:
            dossier = get_object_or_404(DossierObstetrical, id=id)
            serializer = DossierObstetricalSerializer(dossier, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated = DossierService.update_dossier(request.user, dossier, serializer.validated_data)
            return Response(DossierObstetricalSerializer(updated).data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
