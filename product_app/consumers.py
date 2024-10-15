import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from django.contrib.auth.models import AnonymousUser
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from rest_framework_simplejwt.authentication import JWTAuthentication


        query_string = parse_qs(self.scope['query_string'].decode())
        token_key = query_string.get('token', [None])[0]

        if token_key:
            try:
           
                UntypedToken(token_key)
          
                jwt_authenticator = JWTAuthentication()
                validated_token = await sync_to_async(jwt_authenticator.get_validated_token)(token_key)
                self.scope['user'] = await sync_to_async(jwt_authenticator.get_user)(validated_token)
            except (InvalidToken, TokenError) as e:
                logger.warning(f"Invalid token: {e}")
                self.scope['user'] = AnonymousUser()

        if self.scope["user"].is_authenticated:
            self.user_id = self.scope['user'].id
            self.group_name = f"user_{self.user_id}"

            # Join group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()
            logger.info(f"User {self.user_id} connected to group {self.group_name}")
        else:
            logger.warning("User not authenticated, closing connection")
            await self.close()

    async def disconnect(self, close_code):

        if hasattr(self, 'group_name'):
        
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            logger.info(f"User {self.user_id} disconnected from group {self.group_name}")

    async def receive(self, text_data):
        logger.info(f"Received message from user {self.user_id}: {text_data}")


        await self.send(text_data=json.dumps({
            'message': text_data
        }))

    async def send_notification(self, event):
        message = event['message']
        logger.info(f"Sending message to user {self.user_id}: {message}")


        await self.send(text_data=json.dumps({
            'message': message
        }))
