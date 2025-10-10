# sms_sender/serializers.py
from rest_framework import serializers

class SendSMSSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)
    mobile_numbers = serializers.CharField()  # acceptes "243812345678" ou "2438...,2438..."
    sender_id = serializers.CharField(required=False, allow_blank=True)
    is_unicode = serializers.BooleanField(required=False)
    is_flash = serializers.BooleanField(required=False)
    data_coding = serializers.ChoiceField(choices=["0","3","8"], required=False)
    schedule_time = serializers.CharField(required=False, allow_blank=True)  # yyyy-MM-dd HH:MM si utilisé
    group_id = serializers.CharField(required=False, allow_blank=True)
