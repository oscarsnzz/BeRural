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

        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name,
            self.channel_name
        )

        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count()

    def receive(self, text_data):
        data = json.loads(text_data)
        body = data.get("body")

        message = GroupMessage.objects.create(
            group=self.chatroom,
            body=body,
            author=self.user
        )

        html = render_to_string("Chats/chat_message.html", {
            "message": message,
            "user": self.scope["user"],
            "just_added": True,
            "es_mio": True,
        })

        self.send(text_data=json.dumps({
            "html": html
        }))

        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name,
            {
                "type": "menssage_handler",
                "message_id": message.id,
                "sender_id": self.user.id,
            }
        )

    def menssage_handler(self, event):
        message_id = event["message_id"]
        sender_id = event.get("sender_id")

        if self.user.id == sender_id:
            return

        message = GroupMessage.objects.get(id=message_id)

        html = render_to_string("Chats/chat_message.html", {
            "message": message,
            "user": self.scope["user"],
            "just_added": True,
        })

        self.send(text_data=json.dumps({
            "html": html
        }))

    def update_online_count(self):
        online_count = self.chatroom.users_online.count()

        event = {
            'type': 'online_count_handler',
            'online_count': online_count
        }

        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name,
            event
        )

    def online_count_handler(self, event):
        online_count = event['online_count']

        html = render_to_string('partials/online_count.html', {
            'online_count': online_count
        })

        self.send(text_data=json.dumps({
            "html": html
        }))