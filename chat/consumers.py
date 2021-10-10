import datetime

from django.conf import settings
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .exceptions import ClientError
from .utils import get_room_or_error, get_slow_mode_delay
from .models import Message, Room
from datetime import datetime as dt
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from django.db import IntegrityError


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    This chat consumer handles websocket connections for chat clients.

    It uses AsyncJsonWebsocketConsumer, which means all the handling functions
    must be async functions, and any sync work (like ORM access) has to be
    behind database_sync_to_async or sync_to_async. For more, read
    http://channels.readthedocs.io/en/latest/topics/consumers.html
    """

    # WebSocket event handlers

    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        # Are they logged in?
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        else:
            # Accept the connection
            await self.accept()
        # Store which rooms the user has joined on this connection
        self.rooms = set()

    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave all the rooms we are still in
        for room_id in list(self.rooms):
            try:
                await self.leave_room(room_id)
            except ClientError:
                pass

    async def receive_json(self, content):
        """
        Called when we get a text frame. Channels will JSON-decode
        the payload for us and pass it as the first argument.
        """
        # Messages will have a "command" key we can switch on
        command = content.get("command", None)
        try:
            if command == "join":
                # Make them join the room
                await self.join_room(content["room"])
            elif command == "leave":
                # Leave the room
                await self.leave_room(content["room"])
            elif command == "send":
                await self.send_room(content["room"], content["message"], content["is_anonymous"])  # goes to chat and DB
                # await self.send_room(content["room"], str(content["message"]+'===='))
        except ClientError as e:
            # Catch any errors and send it back
            await self.send_json({"error": e.code})

    #################################################
    # Command helper methods called by receive_json #
    #################################################

    async def join_room(self, room_id):  # and scope{user, }!
        """
        Called by receive_json when someone sent a join command.
        """
        # The logged-in user is in our scope thanks to
        # the authentication ASGI middleware
        room = await get_room_or_error(room_id, self.scope["user"])

        # Store that we're in the room
        self.rooms.add(room_id)  # 1

        # Add them to the group so they get room messages
        await self.channel_layer.group_add(
            room.group_name,    # room-1
            self.channel_name,  # specific.BZcPrnWw!vvvelNWGEgbE
        )
        # Instruct their client to finish opening the room
        await self.send_json({
            "join": str(room.id),  # 1
            "title": room.title,   # "Room 1"
            "slow_mode_delay": get_slow_mode_delay(room),  # delay in seconds or None if slow mode is disabled
        })

        # Load all messages from DB to Chat
        cn = self.channel_name
        messages = await self.get_messages(room_id)
        for message in messages:
            u = await self.get_user_by_id(message['sender_id'])
            # message: id, sender_id, time, text, room_id
            # t=str(message['time'])[0:19]
            await self.channel_layer.send(
                cn,
                {
                    "type": "chat.message",
                    "room_id": room_id,
                    "user_id": u.id,
                    "anonymous": message['anonymous'],
                    # "message": t+': '+message['text'], 
                    "message": message['text'],
                    "new": False,
                    # "time": message['time'], 
                    # "time": 'asd', 
                }
            )

    async def leave_room(self, room_id):
        """
        Called by receive_json when someone sent a leave command.
        """
        # The logged-in user is in our scope thanks to
        # the authentication ASGI middleware
        room = await get_room_or_error(room_id, self.scope["user"])

        # Remove info that we're in the room
        self.rooms.discard(room_id)
        # Remove them from the group so they no longer get room messages
        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name,
        )
        # Instruct their client to finish closing the room
        await self.send_json({
            "leave": str(room.id),
        })

    async def send_room(self, room_id, message, is_anonymous=False):
        """
        Called by receive_json when someone
        sends a message to a room.
        """

        # Check they are in this room
        if room_id not in self.rooms:
            raise ClientError("ROOM_ACCESS_DENIED")

        # Get the room...
        room = await get_room_or_error(room_id, self.scope["user"])

        # impossible to send anonymous messages in private chat
        if not room.public and is_anonymous:
            raise ClientError("ANONYMOUS_IN_PRIVATE")

        # make sure enough time has passed if slow mode enabled in it
        time_now = datetime.datetime.now()
        last_message_by_user = await self.get_latest_message_by_user(room, self.scope['user'])
        delay = get_slow_mode_delay(room)

        if last_message_by_user is not None \
            and delay is not None \
                and time_now.timestamp() - last_message_by_user.time.timestamp() < delay:
            raise ClientError("SLOW_MODE")

        # ...and send to the group info about it
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.message",
                "room_id": room_id,
                "user_id": self.scope["user"].id,
                "anonymous": is_anonymous,
                "message": message,  # goes to chat and DB
                "new": True,
                # "time": dt.now(),
            }
        )

        # Save message to DB
        u = await self.get_user_by_name(self.scope["user"].username)
        r = await self.get_room(room_id)
        msg = Message(sender=u, text=message, room=r, anonymous=is_anonymous)  # time is added in a models.py
        await self.save_message(msg)

    ###########################################################
    # Handlers for messages sent over the channel layer       #
    #                                                         #
    # These helper methods are named by the types             #
    # we send - so: chat.join    becomes chat_join (removed)  #
    #               chat.leave   becomes chat_leave (removed) #
    #               chat.message becomes chat_message         #
    ###########################################################

    async def chat_message(self, event):
        """
        Called when someone has messaged our chat
        """
        # print(event["time"])
        # for i in event:
        #     print(i)
        # print(event)
        # Send a message down to the client
        user = await self.get_user_by_id(event["user_id"])
        await self.send_json( 
            {
                # type, room_id, username, message
                "room": event["room_id"],
                # Hide username if message is anonymous
                "username": 'Anonymous User' if event["anonymous"] else user.username,
                "message": event["message"],  # goes only from DB to chat. Display alteration possible but only from DB.
                # "time": event["time"],
                # "time": dt.now(),
                "time": str(dt.now()),  # tylko to dziala
                # let client know if message was sent by a another user (True) or loaded from database (False)
                "new": event["new"] if self.scope['user'] != user else False,
                # "time": 'czas',
            },
        )

    ###########################
    # Sync to async functions #
    ###########################

    @database_sync_to_async
    def get_messages(self, room):
        m = list(Message.objects.filter(room=room).values().order_by('time'))
        return m

    @database_sync_to_async
    def get_room(self, room_id):
        r = Room.objects.get(id=room_id)
        return r

    @database_sync_to_async
    def get_user_by_id(self, id):
        u = User.objects.get(id=id)
        return u

    @database_sync_to_async
    def get_user_by_name(self, user):
        u = User.objects.get(username=user)
        return u

    @database_sync_to_async
    def save_message(self, message):
        if message.text:
            message.save()

    @database_sync_to_async
    def get_latest_message_by_user(self, room, user):
        return room.messages.filter(sender=self.scope['user']).order_by("-time").first()