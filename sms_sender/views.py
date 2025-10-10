# sms_sender/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SendSMSSerializer
from .services import send_sms_via_md

class SendSMSAPIView(APIView):
    def post(self, request):
        serializer = SendSMSSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = send_sms_via_md(**serializer.validated_data)

        if result.get("success"):
            return Response({"code": 0, "message": "Success", "data": result.get("data")}, status=status.HTTP_200_OK)

        # Prioriser l'affichage du code d'erreur de l'API MD SMS si présent
        if result.get("error_type") == "api_error":
            return Response({
                "code": result.get("api_error_code"),
                "message": result.get("api_error_description"),
                "details": result.get("raw")
            }, status=status.HTTP_400_BAD_REQUEST)

        # autres mapping d'erreurs
        etype = result.get("error_type")
        if etype == "timeout":
            return Response({"code": "timeout", "message": result.get("error")}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        if etype == "connection":
            return Response({"code": "connection_error", "message": result.get("error")}, status=status.HTTP_502_BAD_GATEWAY)
        if etype == "config":
            return Response({"code": "config_error", "message": result.get("error")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # default
        return Response({"code": "error", "message": result.get("error"), "raw": result.get("raw", result.get("raw_text"))},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
