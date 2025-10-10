from django.urls import path
from .views import SendSMSAPIView

urlpatterns = [
    path("sms/send/", SendSMSAPIView.as_view(), name="sms_send"),
]
