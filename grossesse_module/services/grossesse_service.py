
from grossesse_module.models import AuditAction
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
    def set_grossesse_state(user, grossesse, new_statut):
        from grossesse_module.models import Grossesse
        if new_statut not in dict(Grossesse.STATUTS):
            raise ValueError("Statut invalide")
        grossesse.statut = new_statut
        grossesse.save()
        AuditAction.objects.create(user=user, patiente=grossesse.patiente, action_type="UPDATE_GROSSESSE")
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
