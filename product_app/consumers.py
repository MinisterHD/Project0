# consumers.py

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            logger.info(f"Attempting to connect: {self.scope['user']}")
            # Temporarily allow all connections for testing
            await self.accept()
        except Exception as e:
            logger.error(f"Error during connection: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            logger.info(f"Disconnecting: {self.scope['user']}")
        except Exception as e:
            logger.error(f"Error during disconnection: {e}")

    async def receive(self, text_data):
        try:
            logger.info(f"Received message: {text_data}")
            await self.send(text_data=json.dumps({
                'message': f"Server received: {text_data}"
            }))
        except Exception as e:
            logger.error(f"Error during message receive: {e}")

    async def send_notification(self, event):
        try:
            message = event['message']
            logger.info(f"Sending notification: {message}")

            await self.send(text_data=json.dumps({
                'message': message
            }))
        except Exception as e:
            logger.error(f"Error during sending notification: {e}")