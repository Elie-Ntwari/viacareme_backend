from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from django.utils import timezone
from auth_module.models.user import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import cloudinary.uploader
import secrets
from typing import Optional, List
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from auth_module.repositories.user_repository import UserRepository
from auth_module.repositories.verification_repository import VerificationRepository
from auth_module.serializers.user_serializer import UserFullSerializer
from auth_module.services.totp_service import TOTPService
from auth_module.services.email_service import EmailService
from hospital_module.models import Gestionnaire

# Configs
ACTIVATION_CODE_EXP_MINUTES = 15
MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_CONTENT_TYPES = ("image/jpeg", "image/png", "image/jpg")


def _validate_image_file(file_obj):
    content_type = getattr(file_obj, "content_type", None)
    size = getattr(file_obj, "size", None)

    if not content_type:
        raise ValidationError("Impossible de déterminer le type du fichier.")
    if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise ValidationError("Type de fichier non autorisé. (jpg/png seulement)")
    if size is not None and size > MAX_PHOTO_BYTES:
        raise ValidationError("Image trop grande (max 5MB).")
    return True


def normalize_phone(phone: str) -> str:
    """
    Transforme le numéro au format +2439... (pour la RDC)
    Exemples acceptés :
    - +243 97777...
    - +24397777...
    - 097777...
    - 97777...
    Retourne toujours +2439...
    """
    import re
    if not phone:
        return None
    phone = re.sub(r"\D", "", phone)  # retire tout sauf chiffres
    if phone.startswith("243"):
        phone = "+" + phone
    elif phone.startswith("0"):
        phone = "+243" + phone[1:]
    elif phone.startswith("9") and len(phone) == 8:
        phone = "+243" + phone
    elif phone.startswith("9") and len(phone) == 9:
        phone = "+243" + phone
    elif phone.startswith("+243"):
        phone = "+243" + phone[4:]
    else:
        # format inconnu, retourne tel quel
        phone = "+243" + phone[-9:] if len(phone) >= 9 else phone
    return phone

class UserService:


    @staticmethod
    def list_all_users():
        return UserRepository.list_all_users()
    
    @staticmethod
    def list_users_paginated(request):
        """
        Liste paginée des utilisateurs.
        """
        queryset = UserRepository.list_users_queryset()
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get("page_size", 5))  # page_size param dynamique

        page = paginator.paginate_queryset(queryset, request)
        serializer = UserFullSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    @staticmethod
    def register_user(nom, postnom, prenom, email, telephone=None, photo_file=None, password=None, role="SUPERADMIN"):
        if UserRepository.get_by_email(email):
            raise ValidationError("Un utilisateur avec cet email existe déjà.")

        if role not in dict(User.ROLE_CHOICES).keys():
            raise ValidationError(f"Rôle invalide. Choisissez parmi {', '.join(dict(User.ROLE_CHOICES).keys())}.")

        photo_url = None
        if photo_file:
            _validate_image_file(photo_file)
            try:
                upload_result = cloudinary.uploader.upload(
                    photo_file,
                    folder="jali_images/users/profile_photos",
                    resource_type="image"
                )
                photo_url = upload_result.get("secure_url")
            except Exception as e:
                raise ValidationError(f"Erreur upload photo: {str(e)}")

        if not password:
            raise ValidationError("Le mot de passe est requis.")
        hashed = make_password(password)

        # Normalisation du téléphone
        telephone_norm = normalize_phone(telephone) if telephone else None

        user = UserRepository.create_user(
            nom=nom,
            postnom=postnom,
            prenom=prenom,
            email=email,
            telephone=telephone_norm,
            photo_url=photo_url,  # corrigé
            password=hashed,
            role=role,
            est_actif=True,
            est_verifie=True,
            deux_facteurs_active=False,
        )

        # code = str(secrets.randbelow(900000) + 100000)
        # VerificationRepository.create_code(user, code, canal="EMAIL", expiration_minutes=ACTIVATION_CODE_EXP_MINUTES)

        # EmailService.send_activation_email(user.email, code)

        return {"message": "Compte créé avec succès", "user_id": user.id}

    @staticmethod
    @transaction.atomic
    def create_user(creer_par, nom, postnom, prenom, email, telephone=None, photo_file=None, role="SUPERADMIN"):
        if UserRepository.get_by_email(email):
            raise ValidationError(f"Un utilisateur avec {email} existe déjà.")

        if role not in dict(User.ROLE_CHOICES).keys():
            raise ValidationError(f"Rôle invalide. Choisissez parmi {', '.join(dict(User.ROLE_CHOICES).keys())}.")

        # Vérification des droits
        if creer_par.role not in ["SUPERADMIN", "GESTIONNAIRE"]:
            raise ValidationError("Vous n'avez pas les droits pour créer un utilisateur.")

        # Upload photo
        photo_url = None
        if photo_file:
            try:
                upload_result = cloudinary.uploader.upload(
                    photo_file,
                    folder="jali_images/users/profile_photos",
                    resource_type="image"
                )
                photo_url = upload_result.get("secure_url")
            except Exception as e:
                raise ValidationError(f"Erreur upload photo: {str(e)}")

        # Création avec mot de passe par défaut
        hashed = make_password("1234567890")

        # Normalisation du téléphone
        telephone_norm = normalize_phone(telephone) if telephone else None

        user = UserRepository.create_user(
            nom=nom,
            postnom=postnom,
            prenom=prenom,
            email=email,
            telephone=telephone_norm,
            photo_url=photo_url,
            password=hashed,
            role=role,
            est_actif=True,
            est_verifie=True,
            deux_facteurs_active=False,
        )

        return {"message": "Compte créé avec succès.", "user_id": user.id}

    @staticmethod
    @transaction.atomic
    def activate_account(email, code):
        user = UserRepository.get_by_email(email)
        if not user:
            raise ValidationError("Utilisateur introuvable.")

        vc = VerificationRepository.get_valid_code(user, code, canal="EMAIL")
        if not vc:
            raise ValidationError("Code invalide ou expiré.")

        VerificationRepository.mark_code_as_used(vc)
        UserRepository.update_user(user, est_actif=True, est_verifie=True)

        return {"message": "Compte activé. Vous pouvez maintenant vous connecter."}

    @staticmethod
    def initiate_login(email, password):
        user = UserRepository.get_by_email(email)
        if not user or not check_password(password, user.password):
            raise ValidationError("Identifiants invalides.")
        if not user.est_actif:
            raise ValidationError("Compte inactif, activez-le via email.")

        # # 2FA obligatoire : si pas configuré, on renvoie provisioning_uri et qr_url mais PAS le secret
        # if not user.deux_facteurs_active:
        #     qr_data = TOTPService.start_totp_setup(user.email)

        #     return {
        #         "2fa_setup_required": True,
        #         "provisioning_uri": qr_data["provisioning_uri"],
        #         "qr_url": qr_data["qr_url"],
        #         "setup_token": qr_data["setup_token"],  # jeton temporaire pour confirmer setup
        #     }

        # # 2FA configuré, le client doit envoyer le code TOTP via finalize_login_with_2fa
        # return {"2fa_setup_required": False, "message": "Entrez le code 2FA pour finaliser la connexion."}
       
        # On génère tokens avec simplejwt
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        
        # Sérialiser l'utilisateur
        user_data = UserFullSerializer(user).data
        
      
         # Valeurs par défaut
        hospital_info = {
            "hospital_id": None,
            "hospital_name": None,
            "hopitaux": []  # ⚡ tableau [{id, nom}] pour médecin
        }

        # Injecter infos liées aux hôpitaux selon rôle
        if user.role == "GESTIONNAIRE":
            try:
                hopital = user.gestionnaire.hopital
                hospital_info["hospital_id"] = hopital.id
                hospital_info["hospital_name"] = hopital.nom
            except Exception:
                hospital_info["hospital_id"] = None
                hospital_info["hospital_name"] = None

        elif user.role == "MEDECIN":
                try:
                    hopitaux = user.profil_medecin.hopitaux.all()
                    hospital_info["hopitaux"] = [
                        {"id": h.id, "nom": h.nom} for h in hopitaux
                    ]
                except Exception:
                    hospital_info["hopitaux"] = []


        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_data,
            **hospital_info
        }
    
    
    
    def get_related_hospitals(self) -> Optional[dict]:
        """
        Retourne les hôpitaux liés à l'utilisateur selon son rôle :
        - GESTIONNAIRE : un seul hospital_id
        - MEDECIN : liste des hospital_ids
        - sinon : None
        """
        if self.role == "GESTIONNAIRE":
            try:
                hospital_id = self.gestionnaire.hopital.id
                return {"hospital_id": hospital_id}
            except Gestionnaire.DoesNotExist:
                return {"hospital_id": None}

        elif self.role == "MEDECIN":
            # si tu as une table Medecin avec une relation ManyToMany Hopital
            hospital_ids = list(self.medecin.hopitaux.values_list("id", flat=True))
            return {"hospital_ids": hospital_ids}

        return None
    
    @staticmethod
    def confirm_2fa_setup(email, setup_token, totp_code):
        user = UserRepository.get_by_email(email)
        if not user:
            raise ValidationError("Utilisateur introuvable.")

        # Confirme la configuration avec le token setup et le code TOTP
        if TOTPService.confirm_totp_setup(user, setup_token, totp_code):
            return {"message": "2FA configuré avec succès."}
        else:
            raise ValidationError("Erreur lors de la confirmation 2FA.")

    @staticmethod
    def finalize_login_with_2fa(email, totp_code):
       
        user = User.objects.get(email=email)
        if not user:
            raise ValidationError("Utilisateur introuvable.")
        secret = user.get_totp_secret()
        if not secret:
            raise ValidationError("2FA non configuré.")

        if not TOTPService.verify_code(secret, totp_code):
            raise ValueError("Code 2FA invalide")

        # On génère tokens avec simplejwt
        token_data = TokenObtainPairSerializer.get_token(user)
        access_token = str(token_data.access_token)
        refresh_token = str(token_data)

        
        # Sérialiser l'utilisateur
        user_data = UserFullSerializer(user).data

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_data,
            # "user_id": user.id,
            # "user_email": user.email,
            # "role": user.role,
        }
    
    @staticmethod
    def resend_verification_code(email: str, canal: str = "EMAIL"):
        user = UserRepository.get_by_email(email)
        if not user:
            raise ValidationError("Utilisateur introuvable.")

        if user.est_verifie:
            raise ValidationError("Compte déjà vérifié.")

        new_code_instance = VerificationRepository.resend_code(user, canal, expiration_minutes=15)

        # Envoi email si canal EMAIL
        if canal == "EMAIL":
            EmailService.send_activation_email(user.email, new_code_instance.code)

      

        return {"message": f"Un nouveau code de vérification a été envoyé via {canal}."}


    @staticmethod
    def logout_user(refresh_token: str):
        """
        Invalide le refresh token en le mettant dans la blacklist.
        """
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return {"message": "Déconnexion réussie."}
        except Exception:
            raise ValidationError("Token invalide ou déjà expiré.")
                
        

        
        



    @staticmethod
    def initiate_login_by_phone(telephone, password):
        try:
            user = User.objects.get(telephone=telephone)
        except User.DoesNotExist:
            raise ValidationError("Identifiants invalides.")

        if not check_password(password, user.password):
            raise ValidationError("Identifiants invalides.")

        if not user.est_actif:
            raise ValidationError("Compte inactif, activez-le via email.")

        # Génération tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        user_data = UserFullSerializer(user).data

        # Infos hôpitaux si applicable
        hospital_info = {"hospital_id": None, "hospital_ids": []}
        if user.role == "GESTIONNAIRE":
            try:
                hospital_info["hospital_id"] = user.gestionnaire.hopital.id
            except Exception:
                pass
        elif user.role == "MEDECIN":
            try:
                hospital_info["hospital_ids"] = list(user.medecin.hopitaux.values_list("id", flat=True))
            except Exception:
                pass

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_data,
            **hospital_info
        }
