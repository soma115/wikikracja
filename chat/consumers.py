import base64
import datetime
import imghdr
import io
import os
import uuid

from django.conf import settings
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .exceptions import ClientError
from .utils import get_room_or_error, get_slow_mode_delay, OnlineUserRegistry, RoomRegistry, HandledMessage, Handlers
from .models import Message, Room, MessageVote, MessageHistory, MessageHistoryEntry, MessageAttachment
from datetime import datetime as dt
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from django.db import IntegrityError

from .group_messages import format_chat_message


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    This chat consumer handles websocket connections for chat clients.

    It uses AsyncJsonWebsocketConsumer, which means all the handling functions
    must be async functions, and any sync work (like ORM access) has to be
    behind database_sync_to_async or sync_to_async. For more, read
    http://channels.readthedocs.io/en/latest/topics/consumers.html
    """

    # map of commands and handlers
    handlers = Handlers()

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

            proxy = HandledMessage()
            await self.send_online_update(proxy, True)
            await proxy.send_all(self)

        # Store which rooms the user has joined on this connection
        self.rooms = RoomRegistry()

    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave all the rooms we are still in
        for room_id in self.rooms.items():
            try:
                proxy = HandledMessage()
                await self.leave_room(proxy, room_id)
                await proxy.send_all(self)
            except ClientError:
                pass

        # remove user from online list
        ChatConsumer.online_registry.make_offline(self.scope['user'])

        proxy = HandledMessage()
        await self.send_online_update(proxy, False)
        await proxy.send_all(self)

    async def receive_json(self, content):
        """
        Called when we get a text frame. Channels will JSON-decode
        the payload for us and pass it as the first argument.
        """
        # Messages will have a "command" key we can switch on
        command = content.get("command", None)

        # trace id is a identifier attached to the message by client,
        # that makes request and hopes to get response back with same trace id.
        # therefore, trace id must be attached to the message sent to client
        # who sent message containing it.
        trace_id = content.get("__TRACE_ID")

        handler_data = ChatConsumer.handlers.map.get(command)
        # Unknown command
        if handler_data is None:
            return

        handler = handler_data.get('handler')
        arg_names = handler_data.get('args')
        args = {arg_name: content[arg_name] for arg_name in arg_names}
        try:
            result = HandledMessage()
            # Each handler must have named argument 'proxy', that will collect prepared ws messages for post-processing.
            # After handler has executed and prepared all the messages, we can insert trace ID to the messages,
            # unless it was explicitly specified not to.
            # It is done to prevent some messages sent by handler to be treated as response to request.
            # For example, client asks for messages history and server needs to notify everyone
            # that user fetches message history. It will be done in same handler, but notification will not have trace id,
            # unlike message history sent to user.
            # bruh that's a lot of text.
            await handler(self=self, proxy=result, **args)
            # there are 3 possible scenarios:
            #  1) handler sends message to the consumer who sent command
            #  2) handler sends message to another consumer
            #  3) handler sends message to group
            for group, message, to_consumer, ignore_trace in result.get_messages():
                if group is None:
                    if to_consumer:
                        await to_consumer.send_json(message)
                    else:
                        # Attach trace id only to messages sent to same client,
                        # As it is the one awaiting this response
                        if not ignore_trace:
                            message['__TRACE_ID'] = trace_id
                        await self.send_json(message)
                else:
                    await self.channel_layer.group_send(group, message)
        except ClientError as e:
            # Catch any errors and send it back
            await self.send_json({"error": e.code})

    #################################################
    # Command helper methods called by receive_json #
    #################################################

    @handlers.register("join")
    async def join_room(self, proxy: HandledMessage, room_id: int):  # and scope{user, }!
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
        proxy.send_json({
            "join": str(room.id),  # 1
            "title": room.title,   # "Room 1"
            "slow_mode_delay": get_slow_mode_delay(room),  # delay in seconds or None if slow mode is disabled
            "public": room.public,
            "notifications": not await self.has_muted_room(room.id)
        })

        # Load all messages from DB to Chat
        messages = await self.get_messages(room_id)
        for message in messages:
            latest_message_version = None
            history = await self.get_message_history(message['id'])
            if history:
                latest_message_version = history[-1]

            u = await self.get_user_by_id(message['sender_id'])
            upvotes, downvotes = await self.count_votes(message['id'])
            # message: id, sender_id, time, text, room_id
            # t=str(message['time'])[0:19]
            data = format_chat_message(
                room_id=room_id,
                user_id=u.id,
                anonymous=message['anonymous'],
                message=message['text'],
                message_id=message['id'],
                new=False,
                upvotes=upvotes,
                downvotes=downvotes,
                edited=await self.was_message_edited(message['id']),
                date=message['time'],
                latest_date=latest_message_version.time if latest_message_version else message['time'],
                attachments=await self.load_attachments(message['id']),
            )
            proxy.send_json(await self.format_chat_message_data(data))

        return messages

    @handlers.register("leave")
    async def leave_room(self, proxy: HandledMessage, room_id):
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
        proxy.send_json({"leave": str(room.id)})

    @handlers.register("send")
    async def send_room(self, proxy: HandledMessage, room_id, message, is_anonymous, attachments):
        """
        Called by receive_json when someone
        sends a message to a room.
        """

        # Check they are in this room
        if int(room_id) not in self.rooms.items():
            raise ClientError("ROOM_ACCESS_DENIED")

        # verify that all attachments are valid
        for key, value in attachments.items():
            if key not in ('images',):
                raise ClientError("BAD_ATTACHMENT_TYPE")
            for filename in value:
                if not os.path.exists(f"{settings.BASE_DIR}/media/uploads/{filename}"):
                    raise ClientError("FILE_NOT_FOUND")

        if not message.lstrip() and not attachments:
            raise ClientError("EMPTY_MESSAGE")

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

        await self.save_attachments(message_id, attachments)

        # Add upvote by author (default behaviour)
        upvotes, downvotes = await self.add_vote("upvote", message_id)

        # ...and send to the group info about it
        proxy.group_send(
            room.group_name,
            format_chat_message(
                room_id=room_id,
                user_id=self.scope['user'].id,
                anonymous=is_anonymous,
                message=message,
                message_id=message_id,
                upvotes=upvotes,
                downvotes=downvotes,
                new=True,
                edited=False,
                date=msg.time,
                latest_date=msg.time,
                attachments=attachments,
            )
        )

        # Make rooms appear unseen for some users
        for member in await database_sync_to_async(lambda x: list(x.allowed.all()))(room):
            if not ChatConsumer.online_registry.is_online(member):
                continue

            if member.id == self.scope['user'].id:
                continue

            consumer = ChatConsumer.online_registry.get_consumer(member)

            # room is not seen at the moment
            if consumer.room_is_seen(room):
                # update database
                await consumer.unsee_room(room)

                # send message to user
                await consumer.send_unsee_room(proxy=proxy, room=room)

            if consumer.rooms.present(room):
                continue

            # if room is not muted send notification
            if not await consumer.has_muted_room(room_id):
                await consumer.send_notification(proxy, message_id)

    @handlers.register("get-online-users")
    async def send_online_users(self, proxy: HandledMessage):
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

        proxy.send_json({
            'online_data': online_data
        })

    @handlers.register("room-seen")
    async def handle_seen_room(self, proxy: HandledMessage, room_id):
        """ Handle user reading channel """
        room = await self.get_room(room_id)

        if not await self.room_is_seen(room):
            await self.see_room(room)

    @handlers.register("message-add-vote")
    async def handle_add_vote(self, proxy: HandledMessage, vote: str, message_id: int):
        existing_vote = await self.get_vote(message_id)
        opposite_vote_events = {
            "upvote": "downvote",
            "downvote": "upvote",
        }

        if existing_vote is not None:
            # Prevent duplicate votes
            if existing_vote.vote == vote:
                return

            opposite_event = opposite_vote_events.get(vote)
            # If two vote events conflict with each other e.g. (upvote and downvote)
            # remove conflicting vote and then add new one
            if opposite_event is not None:
                await self.remove_vote(opposite_event, message_id)

        upvotes, downvotes = await self.add_vote(vote, message_id)
        room = await self.get_room_by_message(message_id)

        proxy.group_send(
            room.group_name,
            {
                "type": "chat.vote",
                "update_votes": {
                    "message_id": message_id,
                    "upvotes": upvotes,
                    "downvotes": downvotes,
                    "user_id": self.scope['user'].id,
                    "vote": vote,
                    "add": True,
                }
            }
        )

    @handlers.register("message-remove-vote")
    async def handle_remove_vote(self, proxy: HandledMessage, vote: str, message_id: int):
        upvotes, downvotes = await self.remove_vote(vote, message_id)

        room = await self.get_room_by_message(message_id)

        proxy.group_send(
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

    @handlers.register("edit-message")
    async def handle_edit_message(self, proxy: HandledMessage, message_id: int, new_message: str):
        message = await self.get_message(message_id)

        # only sender can edit own message
        if await self.get_message_sender(message) != self.scope['user']:
            return

        # if new message is same don't save it
        if message.text == new_message:
            return

        room = await self.get_room_by_message(message_id)

        # Save old state and update current state in database
        state = await self.edit_message_and_history(message_id, new_message)

        proxy.group_send(
            room.group_name,
            {
                "type": "chat.edit",
                "edit_message": {
                    "message_id": message_id,
                    "user_id": self.scope['user'].id,
                    "text": new_message,
                    "timestamp": int(state.time.timestamp()) * 1000
                }
            }
        )

    @handlers.register("get-message-history")
    async def send_message_history(self, proxy: HandledMessage, message_id):
        message_states = await self.get_message_states(message_id)
        proxy.send_json({"message_history": message_states})

    @handlers.register("toggle-notifications")
    async def toggle_notifications(self, proxy, room_id, enabled):
        if enabled:
            await self.unmute_room(room_id)
        else:
            await self.mute_room(room_id)

    ##########################################################
    # Helper functions called by custom or built-in handlers #
    ##########################################################

    async def send_online_update(self, proxy: HandledMessage, is_online):
        updated_user = self.scope['user']
        for room_with_user in await self.find_rooms_with(updated_user):

            user_to_notify = await database_sync_to_async(
                lambda x: room_with_user.get_other(x)
            )(updated_user)

            if not ChatConsumer.online_registry.is_online(user_to_notify):
                continue

            consumer = ChatConsumer.online_registry.get_consumer(user_to_notify)

            proxy.send_json({
                'online_data': [{
                    'user_id': updated_user.id,
                    'room_id': room_with_user.id,
                    'online': is_online
                }]
            }, to_consumer=consumer)

    async def send_notification(self, proxy: HandledMessage, message_id):
        message = await self.get_message(message_id)
        sender = await self.get_message_sender(message_id)
        # send update to user
        proxy.send_json({
            "notification": {
                'title': "Anonymous User" if message.anonymous else sender.username,
                'body': message.text[:100],
                'link': None,
            }
        },
            to_consumer=self
        )

    async def send_unsee_room(self, proxy, room):
        # if user is in this room right now do not send
        if self.rooms.present(room):
            return

        # send update to user
        proxy.send_json({
            "unsee_room": room.id,
        },
            # we have to specify receiver because
            # this is a utility method
            # and can be called for any consumer,
            # but proxy does not know about it
            # and will call consumer.send_json()
            # for consumer associated with handler
            # TODO: decorator for utility methods
            to_consumer=self
        )

    async def format_chat_message_data(self, event):
        user = await self.get_user_by_id(event["user_id"])
        vote = await self.get_vote(event['message_id'])

        return {
            **event,  # copy event
            # Override some of fields based on receiver
            'username': 'Anonymous User' if event["anonymous"] else user.username,
            "new": event["new"] if self.scope['user'] != user else False,
            "your_vote": vote.vote if vote is not None else None, "own": self.scope['user'] == user
        }

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

        await self.send_json(
            await self.format_chat_message_data(event)
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
        state = MessageHistoryEntry.objects.create(history=msg_history, text=message.text)

        # Update current text
        message.text = new_message
        message.save()

        return state

    @database_sync_to_async
    def get_message_sender(self, message):
        # message_id was passed
        if isinstance(message, (int, str)):
            return Message.objects.get(pk=message).sender
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

    @database_sync_to_async
    def save_attachments(self, message_id, attachments):
        for attachment_type, filenames in attachments.items():
            for filename in filenames:
                MessageAttachment.objects.create(message_id=message_id, type=attachment_type, filename=filename)

    @database_sync_to_async
    def load_attachments(self, message_id):
        attachments = {}
        for attachment in MessageAttachment.objects.filter(message_id=message_id):
            attachments_of_type = attachments.get(attachment.type, [])
            attachments_of_type.append(attachment.filename)
            attachments[attachment.type] = attachments_of_type
        return attachments

    @database_sync_to_async
    def get_message_history(self, message_id):
        return list(MessageHistoryEntry.objects.filter(history__message_id=message_id))

    @database_sync_to_async
    def has_muted_room(self, room_id):
        room = Room.objects.get(pk=room_id)
        return room.muted_by.filter(id=self.scope['user'].id).exists()

    @database_sync_to_async
    def unmute_room(self, room_id):
        Room.objects.get(pk=room_id).muted_by.remove(self.scope['user'])

    @database_sync_to_async
    def mute_room(self, room_id):
        room = Room.objects.get(pk=room_id)
        user = self.scope['user']
        if not room.muted_by.filter(id=user.id).exists():
            room.muted_by.add(self.scope['user'])
