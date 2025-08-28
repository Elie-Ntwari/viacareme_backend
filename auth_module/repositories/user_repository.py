import stat
from typing import Optional
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from auth_module.models.user import User


class UserRepository:

    @staticmethod
    @transaction.atomic
    def create_user(**kwargs) -> User:
        """
        Crée un utilisateur.
        Utilise une transaction pour éviter les incohérences.
        """
        try:
            return User.objects.create(**kwargs)
        except IntegrityError as e:
            raise ValueError(f"Erreur lors de la création de l'utilisateur : {e}")

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """
        Récupère un utilisateur par email.
        """
        try:
            return User.objects.get(email=email)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """
        Récupère un utilisateur par ID.
        """
        try:
            return User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def update_user(user: User, **kwargs) -> User:
        """
        Met à jour un utilisateur existant.
        """
        for attr, value in kwargs.items():
            setattr(user, attr, value)
        user.save()
        return user
    
    @staticmethod
    def list_all_users():
        """
        Récupère tous les utilisateurs.
        """
        return User.objects.all().order_by("-date_creation")
    
    @staticmethod
    def list_users_queryset():
        """
        Retourne un queryset de tous les utilisateurs (pour pagination).
        """
        return User.objects.all().order_by("-date_creation")
