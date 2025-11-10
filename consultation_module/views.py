from patiente__module.models.patiente import Patiente
from patiente__module.serializers.patiente_serializers import PatienteBaseSerializer
from grossesse_module.models import Grossesse, DossierObstetrical
from grossesse_module.serializers import GrossesseSerializer, DossierObstetricalSerializer
# consultation_module/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from .models import Consultation, RendezVous, Vaccination, ActionOTP
from .serializers import ConsultationSerializer, RendezVousSerializer, VaccinationSerializer, ActionOtpCreateSerializer, ActionOtpVerifySerializer
from .services import create_otp_by_rfid, verify_otp
from grossesse_module.models import Grossesse
from auth_module.models.user import User
from hospital_module.models import Hopital
from medical_module.models.medecin import Medecin
from sms_sender.services import send_sms_via_md



# Endpoint pour rechercher une patiente par nom ou téléphone et afficher toutes ses infos
class PatienteFullInfoBySearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("query")
        if not query:
            return Response({"detail": "Paramètre 'query' requis (email ou téléphone)."}, status=status.HTTP_400_BAD_REQUEST)
        # Recherche par email ou téléphone (user)
        patientes = Patiente.objects.filter(
            user__email__icontains=query
        ) | Patiente.objects.filter(
            user__telephone__icontains=query
        )
        if not patientes.exists():
            return Response({"detail": "Aucune patiente trouvée."}, status=status.HTTP_404_NOT_FOUND)
        result = []
        for pat in patientes:
            pat_data = PatienteBaseSerializer(pat).data
            # Ajout des infos carte (remontée à Register via id carte attribuée)
            carte_info = None
            try:
                from cards_module.models import CarteAttribuee, RegistreCarte
                carte_attribuee = CarteAttribuee.objects.filter(patiente=pat).first()
                if carte_attribuee:
                    registre = carte_attribuee.carte  # lien direct OneToOne vers RegistreCarte
                    carte_info = {
                        "uid_rfid": getattr(registre, "uid_rfid", None),
                        "statut": getattr(registre, "statut", None),
                        "date_attribution": getattr(carte_attribuee, "date_attribution", None)
                    }
                else:
                    carte_info = None
            except Exception:
                carte_info = None
            grossesses = Grossesse.objects.filter(patiente=pat)
            grossesses_data = []
            for g in grossesses:
                g_data = GrossesseSerializer(g).data
                dossier = getattr(g, "dossier", None)
                g_data["dossier_obstetrical"] = DossierObstetricalSerializer(dossier).data if dossier else None
                consultations = Consultation.objects.filter(grossesse=g)
                g_data["consultations"] = ConsultationSerializer(consultations, many=True).data
                rdvs = RendezVous.objects.filter(grossesse=g)
                g_data["rendezvous"] = RendezVousSerializer(rdvs, many=True).data
                vaccins = Vaccination.objects.filter(grossesse=g)
                g_data["vaccinations"] = VaccinationSerializer(vaccins, many=True).data
                grossesses_data.append(g_data)
            result.append({
                "patiente": pat_data,
                "carte": carte_info,
                "grossesses": grossesses_data
            })
        return Response(result, status=status.HTTP_200_OK)



# Endpoint pour lister les infos complètes de toutes les patientes
class AllPatientesFullInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,hopital_id):
        hopital = Hopital.objects.get(id=hopital_id) 
        
        if not hopital:
            return Response({"detail": "Hôpital introuvable."}, status=status.HTTP_404_NOT_FOUND)
        patientes = Patiente.objects.filter(creer_a_hopital_id=hopital_id)
        result = []
        for pat in patientes:
            pat_data = PatienteBaseSerializer(pat).data
            grossesses = Grossesse.objects.filter(patiente=pat)
            grossesses_data = []
            for g in grossesses:
                g_data = GrossesseSerializer(g).data
                dossier = getattr(g, "dossier", None)
                g_data["dossier_obstetrical"] = DossierObstetricalSerializer(dossier).data if dossier else None
                consultations = Consultation.objects.filter(grossesse=g)
                g_data["consultations"] = ConsultationSerializer(consultations, many=True).data
                rdvs = RendezVous.objects.filter(grossesse=g)
                g_data["rendezvous"] = RendezVousSerializer(rdvs, many=True).data
                vaccins = Vaccination.objects.filter(grossesse=g)
                g_data["vaccinations"] = VaccinationSerializer(vaccins, many=True).data
                grossesses_data.append(g_data)
            result.append({
                "patiente": pat_data,
                "grossesses": grossesses_data
            })
        return Response(result, status=status.HTTP_200_OK)
        

# Endpoint pour mettre à jour une consultation
class UpdateConsultationView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        obj_id = request.data.get("id")
        data = request.data.get("data", {})
        if not obj_id:
            return Response({"detail": "id requis."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            obj = Consultation.objects.get(id=obj_id)
        except Consultation.DoesNotExist:
            return Response({"detail": "Consultation introuvable."}, status=status.HTTP_404_NOT_FOUND)
        s = ConsultationSerializer(obj, data=data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_200_OK)

# Endpoint pour mettre à jour un rendez-vous
class UpdateRendezVousView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        obj_id = request.data.get("id")
        data = request.data.get("data", {})
        if not obj_id:
            return Response({"detail": "id requis."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            obj = RendezVous.objects.get(id=obj_id)
        except RendezVous.DoesNotExist:
            return Response({"detail": "Rendez-vous introuvable."}, status=status.HTTP_404_NOT_FOUND)
        s = RendezVousSerializer(obj, data=data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_200_OK)

# Endpoint pour mettre à jour une vaccination
class UpdateVaccinationView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        obj_id = request.data.get("id")
        data = request.data.get("data", {})
        if not obj_id:
            return Response({"detail": "id requis."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            obj = Vaccination.objects.get(id=obj_id)
        except Vaccination.DoesNotExist:
            return Response({"detail": "Vaccination introuvable."}, status=status.HTTP_404_NOT_FOUND)
        s = VaccinationSerializer(obj, data=data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_200_OK)

# Perms: crée tes permissions personnalisées (IsMedecin, etc.)
class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]  # + IsMedecin

    def create(self, request, *args, **kwargs):
        # Récupère l'id du médecin à partir du user connecté
        medecin = getattr(request.user, "profil_medecin", None)
        if not medecin:
            return Response({"detail": "Aucun profil médecin associé à cet utilisateur."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data["medecin"] = medecin.id

        # Vérifie que la grossesse existe
        grossesse_id = data.get("grossesse")
        try:
            grossesse = Grossesse.objects.get(id=grossesse_id)
        except Grossesse.DoesNotExist:
            return Response({"detail": "Grossesse introuvable."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        # lecture nécessite OTP (en-têtes ou query params)
        otp_token = request.query_params.get("otp_token") or request.headers.get("X-OTP-TOKEN")
        otp_code = request.query_params.get("otp_code") or request.headers.get("X-OTP-CODE")
        obj = self.get_object()
        grossesse = obj.grossesse
        if not (otp_token and otp_code):
            return Response({"detail": "OTP requis pour lecture"}, status=status.HTTP_403_FORBIDDEN)
        try:
            verify_otp(grossesse.patiente_id, "LECTURE", otp_token, otp_code)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)


class RendezVousViewSet(viewsets.ModelViewSet):
    queryset = RendezVous.objects.all()
    serializer_class = RendezVousSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        medecin = getattr(request.user, "profil_medecin", None)
        if not medecin:
            return Response({"detail": "Aucun profil médecin associé à cet utilisateur."}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        data["medecin"] = medecin.id
        grossesse_id = data.get("grossesse")
        try:
            grossesse = Grossesse.objects.get(id=grossesse_id)
        except Grossesse.DoesNotExist:
            return Response({"detail": "Grossesse introuvable"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class VaccinationViewSet(viewsets.ModelViewSet):
    queryset = Vaccination.objects.all()
    serializer_class = VaccinationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        medecin = getattr(request.user, "profil_medecin", None)
        if not medecin:
            return Response({"detail": "Aucun profil médecin associé à cet utilisateur."}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        data["medecin"] = medecin.id

        grossesse_id = data.get("grossesse")
        if not grossesse_id:
            return Response({"detail": "Le champ 'grossesse' est requis."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            grossesse = Grossesse.objects.get(id=grossesse_id)
        except Grossesse.DoesNotExist:
            return Response({"detail": f"Grossesse introuvable pour l'id {grossesse_id}."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Endpoint pour créer OTP via scan RFID
class CreateOtpByRfidView(APIView):
    # + permission IsMedecin

    def post(self, request):
        s = ActionOtpCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        uid_rfid = s.validated_data.get("uid_rfid")
        patiente_id = s.validated_data.get("patiente_id")
        action = s.validated_data["action"]

        try:
            if uid_rfid:
                result = create_otp_by_rfid(uid_rfid=uid_rfid, action=action)
                if not result.get("success"):
                    return Response({"detail": result.get("error")}, status=400)
                return Response(result, status=201)
            else:
                from django.utils import timezone
                from datetime import timedelta
                from patiente__module.models.patiente import Patiente
                try:
                    pat = Patiente.objects.get(id=patiente_id)
                except Patiente.DoesNotExist:
                    return Response({"detail":"Patiente introuvable"}, status=404)
                code = ActionOTP.generate_code()
                expire_at = timezone.now() + timedelta(minutes=10)
                otp = ActionOTP.objects.create(patiente=pat, action=action, code_otp=code, expire_at=expire_at)
                phone = getattr(pat.user, "telephone", None)
                if not phone:
                    return Response({"detail": "Aucun numéro de téléphone pour cette patiente"}, status=400)
                # Normalize phone to start with 2438 and be 12 characters
                phone = phone.lstrip('+').lstrip('0')
                if not phone.startswith('243'):
                    phone = '2438' + phone
                if len(phone) > 12:
                    phone = phone[:12]
                elif len(phone) < 12:
                    phone = phone.ljust(12, '0')
                message = f"ViàCareme: Code OTP pour {action}: {code} 🔐. Valide 10 min ⏱️."
                sms_result = send_sms_via_md(message, phone)
                if not sms_result.get("success"):
                    error_type = sms_result.get("error_type")
                    if error_type == "api_error":
                        error_msg = f"Erreur API SMS: {sms_result.get('api_error_code')} - {sms_result.get('api_error_description')}"
                    elif error_type == "timeout":
                        error_msg = "Timeout lors de l'envoi du SMS"
                    elif error_type == "connection":
                        error_msg = "Erreur de connexion lors de l'envoi du SMS"
                    elif error_type == "config":
                        error_msg = "Configuration manquante pour l'envoi du SMS"
                    else:
                        error_msg = f"Erreur inconnue lors de l'envoi du SMS: {sms_result.get('error')}"
                    return Response({"detail": error_msg}, status=400)
                # Return similar format
                patiente_info = {
                    "id": pat.id,
                    "nom": pat.user.nom,
                    "prenom": pat.user.prenom,
                    "telephone": pat.user.telephone,
                    "email": pat.user.email,
                }
                return Response({
                    "success": True,
                    "message": "OTP envoyé sur le SMS",
                    "otp_token": str(otp.token),
                    "otp_expire_at": otp.expire_at,
                    "patiente": patiente_info,
                    "grossesse_en_cours": None,  # Could add if needed
                    "dossier_obstetrical": None,
                    "derniere_consultation": None,
                }, status=201)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

class VerifyOtpView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # On attend juste code, patiente_id et action
        s = ActionOtpVerifySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        code = s.validated_data["code"]
        patiente_id = s.validated_data["patiente_id"]
        action = s.validated_data["action"]
        try:
            # Recherche l'OTP correspondant à la patiente, action et code
            otp = ActionOTP.objects.filter(patiente_id=patiente_id, action=action, code_otp=code, is_used=False).first()
            if not otp:
                return Response({"valid": False, "detail": "OTP invalide ou expiré"}, status=400)
            if timezone.now() > otp.expire_at:
                return Response({"valid": False, "detail": "OTP expiré"}, status=400)
            otp.mark_used()
            return Response({"valid": True})
        except Exception as e:
            return Response({"valid": False, "detail": str(e)}, status=400)


class MedecinPatientesFullInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        # Récupérer l'utilisateur et vérifier qu'il a un profil médecin
        try:
            user = User.objects.get(id=user_id)
            medecin = getattr(user, 'profil_medecin', None)
            if not medecin:
                return Response({"detail": "Cet utilisateur n'a pas de profil médecin."}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"detail": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Récupérer toutes les patientes assignées à ce médecin
        patientes = medecin.patientes_assignees.all().select_related('user', 'creer_a_hopital')

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)
        paginated_patientes = paginator.paginate_queryset(patientes, request)

        result = []
        for pat in paginated_patientes:
            pat_data = PatienteBaseSerializer(pat).data

            # Ajout des infos carte
            carte_info = None
            try:
                from cards_module.models import CarteAttribuee, RegistreCarte
                carte_attribuee = CarteAttribuee.objects.filter(patiente=pat).first()
                if carte_attribuee:
                    registre = carte_attribuee.carte
                    carte_info = {
                        "uid_rfid": getattr(registre, "uid_rfid", None),
                        "statut": getattr(registre, "statut", None),
                        "date_attribution": getattr(carte_attribuee, "date_attribution", None)
                    }
            except Exception:
                carte_info = None

            # Grossesses avec consultations, RDV et vaccinations
            grossesses = Grossesse.objects.filter(patiente=pat)
            grossesses_data = []
            for g in grossesses:
                g_data = GrossesseSerializer(g).data
                dossier = getattr(g, "dossier", None)
                g_data["dossier_obstetrical"] = DossierObstetricalSerializer(dossier).data if dossier else None

                # Consultations pour cette grossesse
                consultations = Consultation.objects.filter(grossesse=g)
                g_data["consultations"] = ConsultationSerializer(consultations, many=True).data

                # Rendez-vous pour cette grossesse
                rdvs = RendezVous.objects.filter(grossesse=g)
                g_data["rendezvous"] = RendezVousSerializer(rdvs, many=True).data

                # Vaccinations pour cette grossesse
                vaccins = Vaccination.objects.filter(grossesse=g)
                g_data["vaccinations"] = VaccinationSerializer(vaccins, many=True).data

                grossesses_data.append(g_data)

            result.append({
                "patiente": pat_data,
                "carte": carte_info,
                "grossesses": grossesses_data
            })

        return paginator.get_paginated_response(result)






