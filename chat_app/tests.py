from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import ChatMessage
from user_app.models import User

class ChatMessageViewSetTests(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        self.chat_message1 = ChatMessage.objects.create(user=self.user, message="Hello, world!")
        self.chat_message2 = ChatMessage.objects.create(user=self.user, message="Another message")
        

        self.list_url = reverse('chatmessage-list')
        self.detail_url = lambda pk: reverse('chatmessage-detail', kwargs={'pk': pk})

    def test_list_chat_messages(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_chat_message(self):
        data = {
            "user": self.user.id,
            "message": "New message"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ChatMessage.objects.count(), 3)
        self.assertEqual(ChatMessage.objects.last().message, "New message")

    def test_retrieve_chat_message(self):
        response = self.client.get(self.detail_url(self.chat_message1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], self.chat_message1.message)

    def test_update_chat_message(self):
        data = {
            "message": "Updated message"
        }
        response = self.client.patch(self.detail_url(self.chat_message1.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.chat_message1.refresh_from_db()
        self.assertEqual(self.chat_message1.message, "Updated message")

    def test_delete_chat_message(self):
        response = self.client.delete(self.detail_url(self.chat_message1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ChatMessage.objects.count(), 1)