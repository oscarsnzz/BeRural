from channels.generic.websocket import WebsocketConsumer
from .models import ChatGroup, GroupMessage
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
import json
from asgiref.sync import async_to_sync

class ChatRoomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)

        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name,
            self.channel_name
        )


    def receive(self, text_data):
        data = json.loads(text_data)
        body = data.get("body")

        message = GroupMessage.objects.create(
            group=self.chatroom,
            body=body,
            author=self.user
        )

        # Solo ENVÍA al grupo (incluidos todos los conectados MENOS el emisor)
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name,
            {
                "type": "menssage_handler",
                "message_id": message.id,
            }
        )

        # Renderiza el mensaje del usuario para él mismo (solo local)
        html = render_to_string("chat_message.html", {
            "message": message,
            "user": self.scope["user"],
            "just_added": True,
            "es_mio": True,
        })

        self.send(text_data=html)

        
    def menssage_handler(self, event):
        message_id = event["message_id"]
        message = GroupMessage.objects.get(id=message_id)

        html = render_to_string("chat_message.html", {
            "message": message,
            "user": self.scope["user"],  # importante para saber si es suyo
            "just_added": True,
        })

        self.send(text_data=html)

           




