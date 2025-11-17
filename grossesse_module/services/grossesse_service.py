
from grossesse_module.models import AuditAction, ClotureGrossesse
from grossesse_module.repositories import DossierRepository, GrossesseRepository


class GrossesseService:

    @staticmethod
    def create_grossesse(user, patiente, data):
        
        if not patiente.has_carte:
            raise ValueError("La patiente ne possède pas une carte de santé active.")
        
        grossesse = GrossesseRepository.create(patiente, data)
        AuditAction.objects.create(user=user, patiente=patiente, action_type="CREATE_GROSSESSE")
        return grossesse

    @staticmethod
    def update_grossesse(user, grossesse, data):
        updated = GrossesseRepository.update(grossesse, data)
        AuditAction.objects.create(user=user, patiente=grossesse.patiente, action_type="UPDATE_GROSSESSE")
        return updated

    @staticmethod
    def set_grossesse_state(user, grossesse, new_statut, cloture_data=None):
        from grossesse_module.models import Grossesse
        if new_statut not in dict(Grossesse.STATUTS):
            raise ValueError("Statut invalide")

        # Check if the grossesse already has this statut
        if grossesse.statut == new_statut:
            if new_statut == "TERMINEE":
                raise ValueError("La grossesse a déjà le statut terminée")
            else:
                raise ValueError(f"La grossesse a déjà le statut {new_statut}")

        # Prevent multiple EN_COURS for the same patiente
        if new_statut == "EN_COURS":
            existing_en_cours = Grossesse.objects.filter(patiente=grossesse.patiente, statut="EN_COURS").exclude(id=grossesse.id)
            if existing_en_cours.exists():
                raise ValueError("Une grossesse en cours existe déjà pour cette patiente")

        # Si le statut est TERMINEE, créer les informations de clôture
        if new_statut == "TERMINEE":
            if not cloture_data:
                raise ValueError("Les informations de clôture sont obligatoires pour terminer une grossesse")
            
            # Vérifier si une clôture existe déjà
            if hasattr(grossesse, 'cloture') and grossesse.cloture:
                raise ValueError("Cette grossesse a déjà été clôturée")
            
            # Créer la clôture
            cloture_data['grossesse'] = grossesse
            cloture_data['created_by'] = user
            ClotureGrossesse.objects.create(**cloture_data)

        grossesse.statut = new_statut
        grossesse.save()
        
        # Enregistrer l'action d'audit appropriée
        action_type = "CLOTURE_GROSSESSE" if new_statut == "TERMINEE" else "UPDATE_GROSSESSE"
        AuditAction.objects.create(user=user, patiente=grossesse.patiente, action_type=action_type)
        
        return grossesse


class DossierService:

    @staticmethod
    def create_dossier(user, grossesse, data):
        # Vérifier si un dossier existe déjà pour cette grossesse
        if hasattr(grossesse, "dossier") and grossesse.dossier is not None:
            raise ValueError(f"La grossesse de la patiente {grossesse.patiente} a déjà un dossier obstétrique.")
        dossier = DossierRepository.create(grossesse, data)
        AuditAction.objects.create(user=user, patiente=grossesse.patiente, action_type="CREATE_DOSSIER_OBS")
        return dossier

    @staticmethod
    def update_dossier(user, dossier, data):
        updated = DossierRepository.update(dossier, data)
        AuditAction.objects.create(user=user, patiente=dossier.grossesse.patiente, action_type="UPDATE_DOSSIER_OBS")
        return updated
