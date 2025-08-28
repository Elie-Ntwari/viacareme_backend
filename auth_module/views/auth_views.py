from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from auth_module.serializers.user_serializer import (
    Confirm2FASerializer,
    FinalizeLogin2FASerializer,
    InitiateLoginSerializer,
    RegisterUserSerializer,
    UserFullSerializer,
)
from auth_module.services.user_service import UserService
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class AuthViewSet(viewsets.ViewSet):

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