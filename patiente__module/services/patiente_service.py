from django.core.exceptions import ValidationError, PermissionDenied
from hospital_module.models import Gestionnaire, Hopital
from patiente__module.models.patiente import Patiente
from patiente__module.repositories.patiente_repository import PatienteRepository
from auth_module.models.user import User



class PatienteService:
    @staticmethod
    def _assert_user_can_manage_hopital(user: User, hopital_id: int):
        if user.role == "SUPERADMIN":
            return
        try:
            gest = Gestionnaire.objects.get(user=user)
        except Gestionnaire.DoesNotExist:
            raise PermissionDenied("Vous n'êtes pas gestionnaire.")
        if gest.hopital_id != hopital_id:
            raise PermissionDenied("Action non autorisée pour cet hôpital.")

    @staticmethod
    def create_or_assign_patiente(request_user: User, payload: dict, hopital_id: int):
        
        creer_a_hopital = Hopital.objects.filter(id=hopital_id).first()
        if not creer_a_hopital:
            raise ValidationError("Hôpital de création introuvable.")
        
        PatienteService._assert_user_can_manage_hopital(request_user, hopital_id)

        existing_email = payload.get("existing_user_email")
        if existing_email:
            user = PatienteRepository.get_user_by_email(existing_email)
            if not user:
                raise ValidationError("Aucun utilisateur trouvé avec cet email.")
            if user.role != "PATIENTE":
                raise ValidationError("L'utilisateur trouvé n'a pas le rôle PATIENTE.")

            pat = PatienteRepository.get_patiente_by_user(user)
            if pat:
                raise ValidationError("Cette patiente est déjà enregistrée.")  # ✅ gestion doublon

            # créer la patiente liée à ce compte utilisateur
            return Patiente.objects.create(
                user=user,
                date_naissance=payload.get("date_naissance"),
                adresse=payload.get("adresse"),
                ville=payload.get("ville"),
                province=payload.get("province"),
                creer_a_hopital=creer_a_hopital
            )
        else:
            email = payload.get("email")
            if PatienteRepository.get_user_by_email(email):
                raise ValidationError("Un utilisateur avec cet email existe déjà.")

            return PatienteRepository.create_user_patiente(
                nom=payload.get("nom"),
                postnom=payload.get("postnom", ""),
                prenom=payload.get("prenom"),
                email=email,
                telephone=payload.get("telephone"),
                date_naissance=payload.get("date_naissance"),
                adresse=payload.get("adresse"),
                ville=payload.get("ville"),
                province=payload.get("province"),
                creer_a_hopital=creer_a_hopital,
            )

    @staticmethod
    def list_patientes_by_hopital(user: User, hopital_id: int):
        PatienteService._assert_user_can_manage_hopital(user, hopital_id)
        hopital = Hopital.objects.filter(id=hopital_id).first()
        if not hopital:
            raise ValidationError("Hôpital introuvable.")
        return PatienteRepository.list_patientes_by_hopital(hopital)
    
    @staticmethod
    def get_all_patientes():
        return PatienteRepository.get_all_patientes()

    @staticmethod
    def assign_medecin_to_patiente(request_user: User, patiente_id: int, medecin_id: int, hopital_id: int):
        PatienteService._assert_user_can_manage_hopital(request_user, hopital_id)

        # Vérifier que la patiente existe et appartient à l'hôpital
        patiente = Patiente.objects.filter(id=patiente_id, creer_a_hopital_id=hopital_id).first()
        if not patiente:
            raise ValidationError("Patiente introuvable ou n'appartient pas à cet hôpital.")

        # Vérifier que le médecin existe et est affecté à l'hôpital
        from medical_module.models.medecin import MedecinHopital
        medecin_hopital = MedecinHopital.objects.filter(medecin_id=medecin_id, hopital_id=hopital_id).first()
        if not medecin_hopital:
            raise ValidationError("Médecin introuvable ou non affecté à cet hôpital.")

        updated_patiente = PatienteRepository.assign_medecin_to_patiente(patiente_id, medecin_id)
        if not updated_patiente:
            raise ValidationError("Erreur lors de l'affectation du médecin.")
        return updated_patiente

    @staticmethod
    def unassign_medecin_from_patiente(request_user: User, patiente_id: int, medecin_id: int, hopital_id: int):
        PatienteService._assert_user_can_manage_hopital(request_user, hopital_id)

        # Vérifier que la patiente existe et appartient à l'hôpital
        patiente = Patiente.objects.filter(id=patiente_id, creer_a_hopital_id=hopital_id).first()
        if not patiente:
            raise ValidationError("Patiente introuvable ou n'appartient pas à cet hôpital.")

        # Vérifier que le médecin est assigné à cette patiente
        if not patiente.medecins.filter(id=medecin_id).exists():
            raise ValidationError("Ce médecin n'est pas assigné à cette patiente.")

        updated_patiente = PatienteRepository.unassign_medecin_from_patiente(patiente_id, medecin_id)
        if not updated_patiente:
            raise ValidationError("Erreur lors de la désaffectation du médecin.")
        return updated_patiente

    @staticmethod
    def get_medecins_for_patiente(request_user: User, patiente_id: int, hopital_id: int):
        PatienteService._assert_user_can_manage_hopital(request_user, hopital_id)

        # Vérifier que la patiente existe et appartient à l'hôpital
        patiente = Patiente.objects.filter(id=patiente_id, creer_a_hopital_id=hopital_id).first()
        if not patiente:
            raise ValidationError("Patiente introuvable ou n'appartient pas à cet hôpital.")

        medecins = PatienteRepository.get_medecins_for_patiente(patiente_id)
        return medecins