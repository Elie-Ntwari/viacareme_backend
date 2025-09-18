from django.utils import timezone
from .models import Grossesse, DossierObstetrical, DossierAccess

class GrossesseRepository:

    @staticmethod
    def create(patiente, data):
        # Vérifier si une grossesse EN_COURS existe
        if Grossesse.objects.filter(patiente=patiente, statut="EN_COURS").exists():
            raise ValueError("La patiente a déjà une grossesse en cours.")
        return Grossesse.objects.create(patiente=patiente, **data)

    @staticmethod
    def update(grossesse, data):
        for k, v in data.items():
            setattr(grossesse, k, v)
        grossesse.save()
        return grossesse

    @staticmethod
    def list_by_patiente(patiente):
        return Grossesse.objects.filter(patiente=patiente).select_related("dossier")


class DossierRepository:

    @staticmethod
    def create(grossesse, data):
        if hasattr(grossesse, "dossier"):
            raise ValueError("Cette grossesse a déjà un dossier obstétrical.")
        return DossierObstetrical.objects.create(grossesse=grossesse, **data)

    @staticmethod
    def update(dossier, data):
        for k, v in data.items():
            setattr(dossier, k, v)
        dossier.save()
        return dossier
