# cards_module/services.py

from django.db import transaction
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status

import random

from cards_module.models import CarteAttribuee, LotCarte, LotCarteDetail, RegistreCarte, SessionScan
from hospital_module.repositories import HopitalRepository
from patiente__module.models.patiente import Patiente
from .repositories import RegistreRepository, SessionRepository, LotRepository
from datetime import timedelta

SESSION_DEFAULT_SECONDS = 120  # durée session

class SessionService:
    @staticmethod
    def create_session(type, device, user, cible_id=None, expires_in=SESSION_DEFAULT_SECONDS):
        expires_at = timezone.now() + timedelta(seconds=expires_in)
        s = SessionScan.objects.create(
            type=type,
            device=device,
            lance_par_user=user,
            cible_id=cible_id,
            expires_at=expires_at
        )
        return s

    @staticmethod
    def close_session(session: SessionScan):
        session.mark_completed()


class CardService:
    @staticmethod
    @transaction.atomic
    def handle_scan(token, uid, device):
        # Validation session
        session = SessionRepository.get_valid_by_token(token)
        if not session:
            return Response({"message": "Session invalide ou expirée."}, status=status.HTTP_400_BAD_REQUEST)

        # Vérification du device
        if session.device_id != device.id:
            return Response({"message": "Device non autorisé pour cette session."}, status=status.HTTP_403_FORBIDDEN)

        # Vérification si la carte existe
        registre = RegistreRepository.get_by_uid(uid)

        if session.type == "ENREGISTREMENT":
            if registre:
                return Response({"message": "Carte déjà enregistrée."}, status=status.HTTP_400_BAD_REQUEST)

            registre = RegistreRepository.create(uid, user=session.lance_par_user)
            registre.statut = "ENREGISTREE"
            registre.est_viacareme = True
            registre.save()
            SessionService.close_session(session)

            return Response({
                "action": "registered",
                "registre_id": registre.id,
                "status": "success"
            }, status=status.HTTP_200_OK)


        # Si type de session inconnu
        return Response({"message": "Type de session inconnu."}, status=status.HTTP_400_BAD_REQUEST)



class LotService:
    @staticmethod
    @transaction.atomic
    def create_lot_by_count(numero_lot, hopital_id, livre_par_user, nombre_cartes):
        # Vérifier existence de l’hôpital
        hopital = HopitalRepository.get_by_id(hopital_id)
        if not hopital:
            return None, "Hôpital introuvable.", []

        # Vérifier doublon de numéro de lot
        if LotCarte.objects.filter(numero_lot__iexact=numero_lot, hopital=hopital).exists():
            return None, f"Le numéro de lot '{numero_lot}' existe déjà pour cet hôpital.", []

        # Récupérer toutes les cartes disponibles pour attribution
        cartes_disponibles = RegistreRepository.get_available_for_delivery()
        if len(cartes_disponibles) < nombre_cartes:
            return None, f"Stock insuffisant : {len(cartes_disponibles)} cartes disponibles.", []

        # Sélection aléatoire des cartes
        cartes_selectionnees = random.sample(cartes_disponibles, nombre_cartes)
        cartes_uids = [c.uid_rfid for c in cartes_selectionnees]

        # Créer le lot
        lot = LotCarte.objects.create(
            numero_lot=numero_lot,
            hopital=hopital,
            livre_par_user=livre_par_user
        )

        # Ajouter les détails et mettre à jour le statut
        for reg in cartes_selectionnees:
            LotRepository.add_detail(lot, reg)
            reg.statut = "LIVREE"
            reg.save()

        return lot, None, cartes_uids





class AttributionService:
    @staticmethod
    @transaction.atomic
    def attribuer_carte(user, carte_id, patiente_id):
        # Vérifier si gestionnaire
        if not user.role == "GESTIONNAIRE":
            return None, "Seul un gestionnaire peut attribuer une carte."

        # Vérifier carte
        try:
            carte = RegistreCarte.objects.select_for_update().get(id=carte_id)
        except RegistreCarte.DoesNotExist:
            return None, "Carte introuvable."

        # Vérifier patiente
        try:
            patiente = Patiente.objects.get(id=patiente_id)
        except Patiente.DoesNotExist:
            return None, "Patiente introuvable."

        # Vérifier que la carte est bien Viacareme
        if not carte.est_viacareme:
            return None, "Cette carte n'est pas une carte Viacareme."

        # Vérifier que la carte est livrée
        if carte.statut != "LIVREE":
            return None, "Cette carte n'est pas disponible (statut non LIVREE)."

        # Vérifier que la carte appartient au lot de l'hôpital du gestionnaire
        hopital_id = user.gestionnaire.hopital_id
        if not LotCarteDetail.objects.filter(lot__hopital_id=hopital_id, registre=carte).exists():
            return None, "Cette carte n'appartient pas au lot de votre hôpital."

        # Vérifier si déjà attribuée
        if CarteAttribuee.objects.filter(carte=carte).exists():
            return None, "Cette carte est déjà attribuée."

        if CarteAttribuee.objects.filter(patiente=patiente).exists():
            return None, "Cette patiente a déjà une carte attribuée."

        # Créer attribution
        attribution = CarteAttribuee.objects.create(
            carte=carte,
            patiente=patiente,
            hopital=patiente.creer_a_hopital,
            attribuee_par=user
        )

        # Mettre à jour carte + patiente
        carte.statut = "AFFECTEE"
        carte.save()
        patiente.has_carte = True
        patiente.save()

        return attribution, None