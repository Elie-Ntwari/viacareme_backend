from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from auth_module.serializers.user_serializer import (
    AddNewUserSerializer,
    Confirm2FASerializer,
    FinalizeLogin2FASerializer,
    InitiateLoginSerializer,
    RegisterUserSerializer,
    UserFullSerializer,
    InitiateLoginByPhoneSerializer
)
from auth_module.services.user_service import UserService
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from hospital_module import permissions

class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_user(self, request):
        """
        PUT/PATCH /auth/update-user/
        Body: { "user_id": ..., autres champs à modifier }
        """
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id requis."}, status=status.HTTP_400_BAD_REQUEST)
        
        from auth_module.models.user import User
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Vérification email déjà utilisé par un autre utilisateur
        new_email = request.data.get("email")
        if new_email and new_email != user.email:
            if User.objects.filter(email=new_email).exclude(id=user_id).exists():
                return Response({"detail": "Un utilisateur avec cet Email existe déjà."}, status=status.HTTP_400_BAD_REQUEST)

        # Liste des champs modifiables
        modifiable_fields = ["nom", "postnom", "prenom", "email", "telephone", "photo_url", "role"]
        updated = False
        for field in modifiable_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
                updated = True
        if updated:
            user.save()
            return Response({"message": "Utilisateur modifié avec succès."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Aucune donnée à modifier."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def list_users(self, request):  
        """GET /auth/list-users/ - liste tous les utilisateurs"""
        users = UserService.list_all_users()
        if not users.exists():
            return Response({"message": "Aucun utilisateur trouvé."}, status=status.HTTP_200_OK)
        serializer = UserFullSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def list_users_paginated(self, request):
        """
        GET /auth/list-users-paginated/?page=1&page_size=20
        Liste paginée des utilisateurs
        """
        return UserService.list_users_paginated(request)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                result = UserService.register_user(**serializer.validated_data)
                return Response(result, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def activate(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        try:
            result = UserService.activate_account(email, code)
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    @action(detail=False, methods=['post'])
    def resend_code(self, request):
        """
        Endpoint: /auth/resend-code/
        Body: {
            "email": "user@example.com",
            "canal": "EMAIL"  # optionnel, default EMAIL
        }
        """
        email = request.data.get('email')
        canal = request.data.get('canal', 'EMAIL')
        try:
            result = UserService.resend_verification_code(email, canal)
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = InitiateLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                result = UserService.initiate_login(email, password)
                return Response(result, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login_http(self, request):
        serializer = InitiateLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                result = UserService.initiate_login(email, password)

                access_token = result["access_token"]
                refresh_token = result["refresh_token"]
                user_data = result["user"]

                # On prépare la réponse de base
                response_data = {
                    "access_token": access_token,
                    "user": user_data
                }

                # Si on a des infos hospitalières, on les ajoute
                if result.get("hospital_id") is not None:
                    response_data["hopital_id"] = result["hospital_id"]

                if result.get("hospital_ids"):
                    response_data["hopital_ids"] = result["hospital_ids"]

                response = Response(response_data, status=status.HTTP_200_OK)


                # Ajout du refresh token en HttpOnly cookie
                response.set_cookie(
                    key="refreshToken",
                    value=refresh_token,
                    httponly=True,
                    secure=False,  # ⚠️ mettre True en prod avec HTTPS
                    samesite="Strict",
                    path="/api/auth/refresh_http"  # cookie envoyé uniquement sur ce path
                )

                return response

            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """
        Endpoint: /auth/refresh/
        Body: { "refresh": "<refresh_token>" }
        """
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({
                "access_token": access_token
            }, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"detail": "Refresh token invalide ou expiré."}, status=status.HTTP_401_UNAUTHORIZED)


    @action(detail=False, methods=['post'])
    def refresh_http(self, request):
        """
        Endpoint: /auth/refresh/
        Le refresh token est lu depuis le cookie HttpOnly
        """
        refresh_token = request.COOKIES.get("refreshToken")

        if not refresh_token:
            return Response({"detail": "Refresh token manquant."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response({"access_token": access_token},
                                status=status.HTTP_200_OK)

            # Optionnel : rotation → renvoyer un nouveau refresh token
            response.set_cookie(
                key="refreshToken",
                value=str(refresh),
                httponly=True,
                secure=False,  # ⚠️ mettre True en prod
                samesite="Strict",
                path="/api/auth/refresh_http"
            )

            return response

        except TokenError:
            return Response({"detail": "Refresh token invalide ou expiré."},
                            status=status.HTTP_401_UNAUTHORIZED)




    @action(detail=False, methods=['post'])
    def finalize_login(self, request):
        serializer = FinalizeLogin2FASerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            totp_code = serializer.validated_data['totp_code']
            try:
                result = UserService.finalize_login_with_2fa(email, totp_code)
                return Response(result, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def confirm_2fa(self, request):
        serializer = Confirm2FASerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            setup_token = serializer.validated_data['setup_token']
            totp_code = serializer.validated_data['totp_code']
            try:
                result = UserService.confirm_2fa_setup(email, setup_token, totp_code)
                return Response(result, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Endpoint: /auth/logout/
        Body: {
            "refresh_token": "xxx"
        }
        """
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "Refresh token requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = UserService.logout_user(refresh_token)
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
    @action(detail=False, methods=['post'],permission_classes=[IsAuthenticated])
    def logout_http(self, request):
        """
        Déconnexion : supprime le cookie HttpOnly + blackliste le refresh token
        """
        try:
            # Récupérer le refresh token du cookie
            refresh_token = request.COOKIES.get("refresh_token")
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()  # nécessite simplejwt.token_blacklist activé
                except TokenError:
                    pass

            # Supprimer le cookie côté client
            response = Response({"detail": "Déconnexion réussie"}, status=status.HTTP_200_OK)
            response.delete_cookie("refresh_token")
            return response

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)




    @action(detail=False, methods=['post'],permission_classes=[IsAuthenticated])
    def add_user(self, request):
        """POST api/auth/add_user/ - ajoute un utilisateur"""
        serializer = AddNewUserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                result = UserService.create_user(request.user, **serializer.validated_data)
                return Response(result, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    

    @action(detail=False, methods=['post'])
    def login_phone(self, request):
        """
        POST /auth/login_phone/
        Body: { "telephone": "...", "password": "..." }
        """
        serializer = InitiateLoginByPhoneSerializer(data=request.data)
        if serializer.is_valid():
            telephone = serializer.validated_data['telephone']
            password = serializer.validated_data['password']
            try:
                result = UserService.initiate_login_by_phone(telephone, password)
                return Response(result, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
