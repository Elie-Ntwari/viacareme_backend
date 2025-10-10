# consultation_module/services.py
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .repositories import OtpRepository, CardRepository
from .models import ActionOTP, Consultation, RendezVous, Vaccination
from auth_module.models.user import User
from sms_sender.services import send_sms_via_md
from grossesse_module.models import Grossesse, DossierObstetrical




def create_otp_by_rfid(uid_rfid: str, action: str, expiry_minutes: int = 120):
    """
    Scan RFID -> retrouve patiente -> crée OTP -> envoie SMS -> retourne dict avec succès, message, infos patiente, grossesse, etc.
    """
    patiente = CardRepository.find_patiente_by_rfid(uid_rfid)
    if not patiente:
        return {
            "success": False,
            "error": "Carte non associée à une patiente"
        }

    code = ActionOTP.generate_code()
    expire_at = timezone.now() + timedelta(minutes=expiry_minutes)
    with transaction.atomic():
        otp = OtpRepository.create(
            patiente=patiente,
            action=action,
            code=code,
            expire_at=expire_at,
            uid_rfid=uid_rfid
        )
        phone = getattr(patiente.user, "telephone", None)
        if not phone:
            return {
                "success": False,
                "error": "Aucun numéro de téléphone pour cette patiente"
            }
        # Normalize phone to start with 2438 and be 12 characters
        phone = phone.lstrip('+').lstrip('0')
        if not phone.startswith('243'):
            phone = '243' + phone
        if len(phone) > 12:
            phone = phone[:12]
        elif len(phone) < 12:
            phone = phone.ljust(12, '0')  # pad with 0 if shorter, though unlikely
        message = f"ViaCareme: Code OTP pour {action}: {code}. Valide {expiry_minutes} min."
        sms_result = send_sms_via_md(message, phone)
        if not sms_result.get("success"):
            error_type = sms_result.get("error_type")
            if error_type == "api_error":
                return {
                    "success": False,
                    "error": f"Erreur API SMS: {sms_result.get('api_error_code')} - {sms_result.get('api_error_description')}"
                }
            elif error_type == "timeout":
                return {
                    "success": False,
                    "error": "Timeout lors de l'envoi du SMS"
                }
            elif error_type == "connection":
                return {
                    "success": False,
                    "error": "Erreur de connexion lors de l'envoi du SMS"
                }
            elif error_type == "config":
                return {
                    "success": False,
                    "error": "Configuration manquante pour l'envoi du SMS"
                }
            else:
                return {
                    "success": False,
                    "error": f"Erreur inconnue lors de l'envoi du SMS: {sms_result.get('error')}"
                }


    # Basic patient info
    patiente_info = {
        "id": patiente.id,
        "nom": patiente.user.nom,
        "prenom": patiente.user.prenom,
        "telephone": patiente.user.telephone,
        "email": patiente.user.email,
    }

    # Current pregnancy
    grossesse = Grossesse.objects.filter(patiente=patiente, statut="EN_COURS").first()
    grossesse_info = None
    dossier_info = None
    last_consultation_info = None

    if grossesse:
        grossesse_info = {
            "id": grossesse.id,
            "date_debut": grossesse.date_debut,
            "dpa": grossesse.dpa,
            "statut": grossesse.statut,
        }
        dossier = getattr(grossesse, "dossier", None)
        if dossier:
            dossier_info = {
                "geste": dossier.geste,
                "parite": dossier.parite,
                "date_ddr": dossier.date_ddr,
                "groupage_sanguin": dossier.groupage_sanguin,
                "rhesus": dossier.rhesus,
                "antecedents_medicaux": dossier.antecedents_medicaux,
                "antecedents_obstetricaux": dossier.antecedents_obstetricaux,
                "allergies": dossier.allergies,
                "prise_medicaments": dossier.prise_medicaments,
                "risque_grossesse": dossier.risque_grossesse,
            }
        last_consultation = Consultation.objects.filter(grossesse=grossesse).order_by("-date_consultation").first()
        if last_consultation:
            last_consultation_info = {
                "id": last_consultation.id,
                "date_consultation": last_consultation.date_consultation,
                "poids": last_consultation.poids,
                "tension_arterielle": last_consultation.tension_arterielle,
                "hauteur_uterine": last_consultation.hauteur_uterine,
                "mouvements_foetaux": last_consultation.mouvements_foetaux,
                "oedemes": last_consultation.oedemes,
                "presentation": last_consultation.presentation,
                "observations": last_consultation.observations,
                "prochaine_consultation": last_consultation.prochaine_consultation,
            }

    return {
        "success": True,
        "message": "OTP envoyé sur le SMS",
        "otp_token": str(otp.token),
        "otp_expire_at": otp.expire_at,
        "patiente": patiente_info,
        "grossesse_en_cours": grossesse_info,
        "dossier_obstetrical": dossier_info,
        "derniere_consultation": last_consultation_info,
    }


def verify_otp(patiente_id: int, action: str, otp_token_or_id, code: str):
    """
    Vérifie l'OTP, incrémente attempts, marque used si succès.
    """
    # rechercher par token (UUID) ou id entier
    otp = None
    if isinstance(otp_token_or_id, str):
        try:
            otp = ActionOTP.objects.get(token=otp_token_or_id, patiente_id=patiente_id, action=action)
        except ActionOTP.DoesNotExist:
            otp = None
    else:
        try:
            otp = ActionOTP.objects.get(id=otp_token_or_id, patiente_id=patiente_id, action=action)
        except ActionOTP.DoesNotExist:
            otp = None

    if otp is None:
        raise ValueError("OTP introuvable")

    if otp.is_used or timezone.now() > otp.expire_at:
        raise ValueError("OTP invalide ou expiré")

    otp.attempts += 1
    otp.save(update_fields=["attempts"])

    if otp.code_otp != code:
        otp.save()
        raise ValueError(f"Code incorrect. Tentatives: {otp.attempts}")

    # succès
    otp.mark_used()
    return True
