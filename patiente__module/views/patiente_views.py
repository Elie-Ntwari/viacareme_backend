from grossesse_module.models import Grossesse, DossierObstetrical
from grossesse_module.serializers import GrossesseSerializer, DossierObstetricalSerializer
from grossesse_module.services.grossesse_service import GrossesseService, DossierService
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated


from medical_module.permissions.medecin_permissions import IsAuthenticatedAndManagerOrSuperAdmin
from patiente__module.serializers.patiente_serializers import PatienteBaseSerializer, PatienteCreateOrAssignSerializer
from patiente__module.services.patiente_service import PatienteService
from patiente__module.models.patiente import Patiente
from grossesse_module.repositories import GrossesseRepository, DossierRepository
      


class PatientesFullInfoByHopitalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, hopital_id):
        from hospital_module.models import Hopital
        from patiente__module.models.patiente import Patiente
        try:
            hopital = Hopital.objects.get(id=hopital_id)
        except Hopital.DoesNotExist:
            return Response({"detail": "Hôpital introuvable."}, status=status.HTTP_404_NOT_FOUND)

        patientes = Patiente.objects.filter(creer_a_hopital=hopital)
        result = []
        for pat in patientes:
            pat_data = PatienteBaseSerializer(pat).data
            grossesses = Grossesse.objects.filter(patiente=pat)
            grossesses_data = []
            for g in grossesses:
                g_data = GrossesseSerializer(g).data
                dossier = getattr(g, "dossier", None)
                g_data["dossier_obstetrical"] = DossierObstetricalSerializer(dossier).data if dossier else None
                grossesses_data.append(g_data)
            result.append({
                "patiente": pat_data,
                "grossesses": grossesses_data
            })
        return Response(result, status=status.HTTP_200_OK)
class UpdateGrossesseAndDossierView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, grossesse_id):
        try:
            grossesse = Grossesse.objects.get(id=grossesse_id)
        except Grossesse.DoesNotExist:
            return Response({"detail": "Grossesse introuvable."}, status=status.HTTP_404_NOT_FOUND)

        dossier = getattr(grossesse, "dossier", None)
        grossesse_data = request.data.get("grossesse", {})
        dossier_data = request.data.get("dossier", {})

        try:
            updated_grossesse = GrossesseService.update_grossesse(request.user, grossesse, grossesse_data)
            updated_dossier = None
            if dossier:
                updated_dossier = DossierService.update_dossier(request.user, dossier, dossier_data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "grossesse": GrossesseSerializer(updated_grossesse).data,
            "dossier_obstetrical": DossierObstetricalSerializer(updated_dossier).data if updated_dossier else None
        }, status=status.HTTP_200_OK)


class PatienteFullInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patiente_id):
        from patiente__module.models.patiente import Patiente
        try:
            pat = Patiente.objects.get(id=patiente_id)
        except Patiente.DoesNotExist:
            return Response({"detail": "Patiente introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Infos personnelles
        pat_data = PatienteBaseSerializer(pat).data

        # Grossesses et dossiers
        grossesses = Grossesse.objects.filter(patiente=pat)
        grossesses_data = []
        for g in grossesses:
            g_data = GrossesseSerializer(g).data
            # Dossier obstétrique lié
            dossier = getattr(g, "dossier", None)
            g_data["dossier_obstetrical"] = DossierObstetricalSerializer(dossier).data if dossier else None
            grossesses_data.append(g_data)

        return Response({
            "patiente": pat_data,
            "grossesses": grossesses_data
        }, status=status.HTTP_200_OK)


class CreateGrossesseAndDossierView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, patiente_id):
        try:
            pat = Patiente.objects.get(id=patiente_id)
        except Patiente.DoesNotExist:
            return Response({"detail": "Patiente introuvable."}, status=status.HTTP_404_NOT_FOUND)

        grossesse_data = request.data.get("grossesse", {})
        dossier_data = request.data.get("dossier", {})

        try:
            grossesse = GrossesseService.create_grossesse(request.user, pat, grossesse_data)
            dossier = DossierService.create_dossier(request.user, grossesse, dossier_data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "grossesse": GrossesseSerializer(grossesse).data,
            "dossier_obstetrical": DossierObstetricalSerializer(dossier).data
        }, status=status.HTTP_201_CREATED)



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
