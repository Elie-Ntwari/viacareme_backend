# cards_module/services.py

from django.db import transaction
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status

import random

from cards_module.models import LotCarte, SessionScan
from hospital_module.repositories import HopitalRepository
from .repositories import RegistreRepository, SessionRepository, LotRepository
from datetime import timedelta

SESSION_DEFAULT_SECONDS = 120  # durée session

class SessionService:
    @staticmethod
    def create_session(type, hopital, device, user, cible_id=None, expires_in=SESSION_DEFAULT_SECONDS):
        expires_at = timezone.now() + timedelta(seconds=expires_in)
        s = SessionScan.objects.create(
            type=type,
            hopital=hopital,
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
            registre.save()
            SessionService.close_session(session)

            return Response({
                "action": "registered",
                "registre_id": registre.id,
                "status": "success"
            }, status=status.HTTP_200_OK)

        # Logic for ATTRIBUTION - currently commented
        # if session.type == "ATTRIBUTION":
        #     if not registre:
        #         return Response({"message": "Carte non trouvée dans registre."}, status=status.HTTP_404_NOT_FOUND)
        #
        #     if registre.statut == "AFFECTEE":
        #         return Response({"message": "Carte déjà attribuée."}, status=status.HTTP_400_BAD_REQUEST)
        #
        #     from patients_module.models import Patiente
        #     try:
        #         pat = Patiente.objects.get(id=session.cible_id)
        #     except Patiente.DoesNotExist:
        #         return Response({"message": "Patiente cible introuvable."}, status=status.HTTP_404_NOT_FOUND)
        #
        #     CarteAttribuee.objects.create(
        #         registre=registre,
        #         patiente=pat,
        #         attribue_par_user=session.lance_par_user
        #     )
        #
        #     registre.statut = "AFFECTEE"
        #     registre.save()
        #     SessionService.close_session(session)
        #
        #     return Response({
        #         "action": "assigned",
        #         "registre_id": registre.id,
        #         "patiente_id": pat.id,
        #         "status": "success"
        #     }, status=status.HTTP_200_OK)

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
