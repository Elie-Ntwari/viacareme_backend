# # cards_module/consumers.py
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from .models import Device, SessionScan
# from django.utils import timezone

# class DeviceConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # url route: /ws/device/<device_serial>/
#         self.device_serial = self.scope['url_route']['kwargs']['device_serial']
#         # option: vérification token/auth header
#         await self.accept()
#         # join group for this device if needed
#         await self.channel_layer.group_add(self.device_serial, self.channel_name)

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.device_serial, self.channel_name)

#     async def receive(self, text_data=None, bytes_data=None):
#         payload = json.loads(text_data)
#         # Exemple: {"type":"scan_result", "token":"...", "uid":"..."}
#         if payload.get("type") == "scan_result":
#             token = payload.get("token")
#             uid = payload.get("uid")
#             # Forward to HTTP endpoint or call service directly (sync)
#             # Ici on appelle un endpoint HTTP interne idéalement, ou call sync function via database_sync_to_async
#             from .services import CardService
#             device = await database_sync_to_async(Device.objects.get)(numero_serie=self.device_serial)
#             try:
#                 res = await database_sync_to_async(CardService.handle_scan)(token, uid, device)
#                 await self.send(text_data=json.dumps({"type": "scan_response", "status": "ok", "data": res}))
#             except Exception as e:
#                 await self.send(text_data=json.dumps({"type": "scan_response", "status": "error", "message": str(e)}))

#     # method to push session creation to this device
#     async def send_session(self, event):
#         # event contains session data
#         await self.send(text_data=json.dumps(event["data"]))
