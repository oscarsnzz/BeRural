from channels.generic.websocket import WebsocketConsumer
from .models import ChatGroup, GroupMessage
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
import json

class ChatRoomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)
        self.accept()


    def receive(self, text_data):
        data = json.loads(text_data)
        body = data.get("body")

        message = GroupMessage.objects.create(
            group=self.chatroom,
            body=body,
            author=self.user
        )

        context = {
            "message": message,
            "user": self.user,
        }

        html = render_to_string("chat_message.html", {
            "message": message,
            "user": self.scope["user"],
            "just_added": True,
            "es_mio": True,  # 👈 Esto es la clave
        })


        # Enviar el mensaje HTML como parte de una respuesta JSON
        self.send(text_data=html)




