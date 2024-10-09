# chat/models.py
from django.db import models
from user_app.models import User

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    message = models.TextField()  
    timestamp = models.DateTimeField(auto_now_add=True)  

    class Meta:
        ordering = ['timestamp']  

    def __str__(self):
        return f'{self.user.username}: {self.message[:20]}...'  
