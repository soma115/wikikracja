import datetime

from django.conf import settings
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .exceptions import ClientError
from .utils import get_room_or_error, get_slow_mode_delay, OnlineUserRegistry, RoomRegistry
from .models import Message, Room, MessageVote, MessageHistory, MessageHistoryEntry
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

    online_registry = OnlineUserRegistry()

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

            # register user as online
            ChatConsumer.online_registry.make_online(self.scope['user'], self)
            await self.send_online_update(True)

        # Store which rooms the user has joined on this connection
        self.rooms = RoomRegistry()

    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave all the rooms we are still in
        for room_id in self.rooms.items():
            try:
                await self.leave_room(room_id)
            except ClientError:
                pass

        # remove user from online list
        ChatConsumer.online_registry.make_offline(self.scope['user'])
        await self.send_online_update(False)

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
            elif command == "get-online-users":
                await self.send_online_users()
            elif command == "room-seen":
                await self.handle_seen_room(content['room_id'])
            elif command == "message-add-vote":
                await self.handle_add_vote(content['event'], content['message_id'])
            elif command == "message-remove-vote":
                await self.handle_remove_vote(content['event'], content['message_id'])
            elif command == "edit-message":
                await self.handle_edit_message(content['message_id'], content['message'])
            elif command == "get-message-history":
                await self.send_message_history(content['message_id'])
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
        self.rooms.join(room_id)  # 1

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
            "public": room.public,
        })

        # Load all messages from DB to Chat
        cn = self.channel_name
        messages = await self.get_messages(room_id)
        for message in messages:
            u = await self.get_user_by_id(message['sender_id'])
            upvotes, downvotes = await self.count_votes(message['id'])
            # message: id, sender_id, time, text, room_id
            # t=str(message['time'])[0:19]
            await self.channel_layer.send(
                cn,
                {
                    "type": "chat.message",
                    "room_id": room_id,
                    "user_id": u.id,
                    "anonymous": message['anonymous'],
                    "message": message['text'],
                    "new": False,
                    "message_id": message['id'],
                    "upvotes": upvotes,
                    "downvotes": downvotes,
                    "edited": await self.was_message_edited(message['id'])
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
        self.rooms.leave(room_id)
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
        if int(room_id) not in self.rooms.items():
            raise ClientError("ROOM_ACCESS_DENIED")

        # Get the room...
        room = await get_room_or_error(room_id, self.scope["user"])

        # impossible to send anonymous messages in private chat
        if not room.public and is_anonymous:
            raise ClientError("ANONYMOUS_IN_PRIVATE")

        # make sure enough time has passed if slow mode enabled in it
        time_now = datetime.datetime.now()
        last_message_by_user = await self.get_own_latest_message(room)
        delay = get_slow_mode_delay(room)

        if last_message_by_user is not None \
            and delay is not None \
                and time_now.timestamp() - last_message_by_user.time.timestamp() < delay:
            raise ClientError("SLOW_MODE")

        # Save message to DB
        u = await self.get_user_by_name(self.scope["user"].username)  # ???
        r = await self.get_room(room_id)
        msg = Message(sender=u, text=message, room=r, anonymous=is_anonymous)  # time is added in a models.py
        message_id = await self.save_message(msg)

        # Add upvote by author (default behaviour)
        upvotes, downvotes = await self.add_vote("upvote", message_id)

        # ...and send to the group info about it
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.message",
                "room_id": room_id,
                "user_id": self.scope["user"].id,
                "anonymous": is_anonymous,
                "message": message,  # goes to chat and DB
                "message_id": message_id,
                "upvotes": upvotes,
                "downvotes": downvotes,
                "new": True,
                "edited": False,  # not necessary but let it be
                # "time": dt.now(),
            }
        )

        # Make rooms appear unseen for some users
        for member in await database_sync_to_async(lambda x: list(x.allowed.all()))(room):
            if not ChatConsumer.online_registry.is_online(member):
                continue

            if member == self.scope['user']:
                continue

            consumer = ChatConsumer.online_registry.get_consumer(member)
            if consumer.rooms.present(room):
                continue

            await consumer.send_unsee_room(room)

    async def send_online_users(self):
        """ Send list of private chats with online user in it. Sent on request. """
        online_data = []
        for online_user_id in ChatConsumer.online_registry.get_online():
            if online_user_id == self.scope['user'].id:
                continue

            user = await self.get_user_by_id(online_user_id)
            private_chat = await self.find_room_with(user, self.scope['user'])
            online_data.append({
                'user_id': user.id,
                'room_id': private_chat.id,
                'online': True,
            })

        await self.send_json({
            'online_data': online_data
        })

    async def send_online_update(self, is_online):
        updated_user = self.scope['user']
        for room_with_user in await self.find_rooms_with(updated_user):

            user_to_notify = await database_sync_to_async(
                lambda x: room_with_user.get_other(x)
            )(updated_user)

            if not ChatConsumer.online_registry.is_online(user_to_notify):
                continue

            consumer = ChatConsumer.online_registry.get_consumer(user_to_notify)
            await consumer.send_json({
                'online_data': [{
                    'user_id': updated_user.id,
                    'room_id': room_with_user.id,
                    'online': is_online
                }]
            })

    async def handle_seen_room(self, room_id):
        """ Handle user reading channel """
        room = await self.get_room(room_id)

        if not await self.room_is_seen(room):
            await self.see_room(room)

    async def send_unsee_room(self, room):
        """ Make room appear not seen for user """

        # if user is in this room right now do not send
        if self.rooms.present(room):
            return

        # room is not seen at the moment
        if not self.room_is_seen(room):
            return

        # update database
        await self.unsee_room(room)

        # send update to user
        await self.send_json({
            "unsee_room": room.id
        })

    async def handle_add_vote(self, event: str, message_id: int):
        existing_vote = await self.get_vote(message_id)
        opposite_vote_events = {
            "upvote": "downvote",
            "downvote": "upvote",
        }

        if existing_vote is not None:
            # Prevent duplicate votes
            if existing_vote.vote == event:
                return

            opposite_event = opposite_vote_events.get(event)
            # If two vote events conflict with each other e.g. (upvote and downvote)
            # remove conflicting vote and then add new one
            if opposite_event is not None:
                await self.remove_vote(opposite_event, message_id)

        upvotes, downvotes = await self.add_vote(event, message_id)
        room = await self.get_room_by_message(message_id)

        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.vote",
                "update_votes": {
                    "message_id": message_id,
                    "upvotes": upvotes,
                    "downvotes": downvotes,
                    "user_id": self.scope['user'].id,
                    "vote": event,
                    "add": True,
                }
            }
        )

    async def handle_remove_vote(self, vote: str, message_id: int):
        upvotes, downvotes = await self.remove_vote(vote, message_id)

        room = await self.get_room_by_message(message_id)

        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.vote",
                "update_votes": {
                    "message_id": message_id,
                    "upvotes": upvotes,
                    "downvotes": downvotes,
                    "user_id": self.scope['user'].id,
                    "vote": vote,
                    "add": False,
                }
            }
        )

    async def handle_edit_message(self, message_id: int, new_message: str):
        message = await self.get_message(message_id)

        # only sender can edit own message
        if await self.get_message_sender(message) != self.scope['user']:
            print(f"users not equal{await self.get_message_sender(message)} and {self.scope['user']}")
            return

        # if new message is same don't save it
        if message.text == new_message:
            print("message is same")
            return

        room = await self.get_room_by_message(message_id)

        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.edit",
                "edit_message": {
                    "message_id": message_id,
                    "user_id": self.scope['user'].id,
                    "text": new_message,
                }
            }
        )

        # Save old state and update current state in database
        await self.edit_message_and_history(message_id, new_message)

    async def send_message_history(self, message_id):
        message_states = await self.get_message_states(message_id)
        await self.send_json({"message_history": message_states})

    ###########################################################
    # Handlers for messages sent over the channel layer       #
    #                                                         #
    # These helper methods are named by the types             #
    # we send - so: chat.join    becomes chat_join (removed)  #
    #               chat.leave   becomes chat_leave (removed) #
    #               chat.message becomes chat_message         #
    #               chat.vote    becomes chat_vote            #
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
        vote = await self.get_vote(event['message_id'])

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
                "message_id": event['message_id'],  # send message id to identify upvotes
                "upvotes": event['upvotes'],
                "downvotes": event['downvotes'],
                "your_vote": vote.vote if vote is not None else None,
                "edited": event['edited'],
                "own": self.scope['user'] == user,
                # "time": 'czas',
            },
        )

    async def chat_vote(self, event):
        """
        Send vote updates to each interested client.
        """

        # copy sub dictionary, just in case
        update = {**event['update_votes']}

        who_triggered = update['user_id']

        # Tell client if it was this client who triggered update to highlight button
        # None if it was not this client, event name string e.g. 'upvote' if it was
        update["your_vote"] = update['vote'] if who_triggered == self.scope["user"].id else None

        # delete unused field
        del update['vote']

        await self.send_json({
            "update_votes": update,
        })

    async def chat_edit(self, event):
        edit = event['edit_message']
        await self.send_json({
            "edit_message": edit,
        })

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
    def find_room_with(self, *users):
        """ Find private 1 to 1 room with given users """
        return Room.find_with_users(*users)

    @database_sync_to_async
    def find_rooms_with(self, *users):
        """ Find private 1 to 1 room with given users """
        # convert to list to avoid lazy evaluation inside async context
        return list(Room.find_all_with_users(*users))

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
        message.save()
        return message.id

    @database_sync_to_async
    def get_own_latest_message(self, room):
        return room.messages.filter(sender=self.scope['user']).order_by("-time").first()

    @database_sync_to_async
    def room_is_seen(self, room):
        return self.scope['user'].seen_rooms.filter(id=room.id).exists()

    @database_sync_to_async
    def see_room(self, room):
        room.seen_by.add(self.scope['user'])

    @database_sync_to_async
    def unsee_room(self, room):
        room.seen_by.remove(self.scope['user'])

    @database_sync_to_async
    def get_message(self, message_id):
        return Message.objects.get(pk=message_id)

    @database_sync_to_async
    def add_vote(self, event: str, message_id: int):
        vote = MessageVote(vote=event, message_id=message_id, user=self.scope['user'])
        vote.full_clean()  # to enforce validation of event name according to choices of MessageVote
        vote.save()
        m = Message.objects.get(pk=message_id)
        return m.votes.filter(vote="upvote").count(), m.votes.filter(vote="downvote").count()

    @database_sync_to_async
    def remove_vote(self, event: str, message_id: int):
        MessageVote.objects.filter(vote=event, message_id=message_id, user=self.scope['user']).delete()
        m = Message.objects.get(pk=message_id)
        return m.votes.filter(vote="upvote").count(), m.votes.filter(vote="downvote").count()

    @database_sync_to_async
    def count_votes(self, message_id):
        m = Message.objects.get(pk=message_id)
        return m.votes.filter(vote="upvote").count(), m.votes.filter(vote="downvote").count()

    @database_sync_to_async
    def get_vote(self, message_id: int):
        return MessageVote.objects.filter(message_id=message_id, user=self.scope['user']).first()

    @database_sync_to_async
    def get_room_by_message(self, message_id: int):
        return Message.objects.get(pk=message_id).room

    @database_sync_to_async
    def edit_message_and_history(self, message_id: int, new_message: str):
        """
        Save current message state as old and update message text
        """
        message = Message.objects.get(pk=message_id)

        # Each message has one associated history object
        msg_history, created = MessageHistory.objects.get_or_create(message=message)

        # Create old message state based on current message text
        MessageHistoryEntry.objects.create(history=msg_history, text=message.text)

        # Update current text
        message.text = new_message
        message.save()

    @database_sync_to_async
    def get_message_sender(self, message):
        return message.sender

    @database_sync_to_async
    def was_message_edited(self, message_id):
        return MessageHistory.objects.filter(message_id=message_id).exists()

    @database_sync_to_async
    def get_message_states(self, message_id):
        history = MessageHistory.objects.filter(message_id=message_id)
        if not history.exists():
            return []

        history = history.first()

        states = [
            {"text": state.text, "date": int(state.time.timestamp())} for state in history.entries.all().order_by("-time")
        ]
        return states
