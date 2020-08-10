import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime as dt
from channels.db import database_sync_to_async
from .models import User


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # TODO: Tutaj dodać wczytywanie historii wiadomości z bazy
        print("Wczytuję wiadomości z bazy")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # event - dictionary of strings (type, message)

        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
        # TODO: Tutaj dodać zapisywanie wiadomości do bazy
        print("Zapisuję wiadomość do bazy")
        # print(f'time:{dt.today()}')  # To jest oczywiscie ok
        # print(f'text:{message}')  # To jest ok
        # print(self.scope['url_route']['kwargs']['room_name'])  # To jest ok

        # Usefull self.scope values:
        # key:path, value:/ws/chat/room1/
        # key:raw_path, value:b'/ws/chat/room1/'
        # key:user, value:a
        # key:url_route, value:{'args': (), 'kwargs': {'room_name': 'room1'}}

        # print(self.scope['user'])  # To mi nic nie daje bo wyswiatla wszystkich rozmawiajacych



        # via: https://stackoverflow.com/questions/55310717/sending-notification-to-one-user-using-channels-2
        self.user = self.scope["user"]
        self.user_room_name = "notif_room_for_user_"+str(self.user.id)  #Notification room name
        await self.channel_layer.group_add(
            self.user_room_name,
            self.channel_name
            )
        print(self.user_room_name)
        print(f'self.channel_name: {self.channel_name}')
        print(event)
        print(self.scope['user'].username)
        print(self.scope['user'].pk)
        print(self.scope['user'])
        print(self.room_group_name)
        print(self.room_name)



        # TODO: Być może tutaj można dodać nadawcę wiadomości. Ale requesterem
        # jest user, który odbiera wiadomość więc wpierw musi istnieć model,
        # który przechowa Nadawcę, Czas, Wiadomość, itd.
        # Jak wyciągnąć nadawcę wiadomości?
