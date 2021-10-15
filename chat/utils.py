import inspect
from typing import Union

from channels.db import database_sync_to_async
from .exceptions import ClientError
from .models import Room
from django.conf import settings

import datetime


# This decorator turns this function from a synchronous function into an async
# one we can call from our async consumers, that handles Django DBs correctly.
# For more, see http://channels.readthedocs.io/en/latest/topics/databases.html
@database_sync_to_async
def get_room_or_error(room_id, user):
    """
    Tries to fetch a room for the user, checking permissions along the way.
    """
    # Check if the user is logged in
    if not user.is_authenticated:
        raise ClientError("USER_HAS_TO_LOGIN")
    # Find the room they requested (by ID)
    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        raise ClientError("ROOM_INVALID")
    return room


def get_slow_mode_delay(room) -> Union[int, None]:
    """ Returns amount of seconds required between messages by configuration """
    slow_mode_config = settings.SLOW_MODE
    return slow_mode_config.get(room.title) or slow_mode_config.get('*')


# added those wrappers to encapsulate underlying data structure
# in case we want to change a way data is stored
class OnlineUserRegistry:
    """ Utility class to keep track of users who are currently connected to websocket """
    def __init__(self):
        self._reg = {}

    def make_online(self, user, consumer):
        self._reg[user.id] = consumer

    def make_offline(self, user):
        del self._reg[user.id]

    def is_online(self, user):
        return self._reg.get(user.id) is not None

    def get_online(self):
        return list(self._reg.keys())

    def get_consumer(self, user):
        return self._reg[user.id]


class RoomRegistry:
    def __init__(self):
        self._reg = {}

    def join(self, room_id):
        self._reg[int(room_id)] = {'joined_at': datetime.datetime.now()}

    def leave(self, room_id):
        if self._reg.get(int(room_id)):
            del self._reg[int(room_id)]

    def present(self, room):
        return self._reg.get(room.id) is not None

    def items(self):
        return list(self._reg.keys())


class HandledMessage:
    def __init__(self):
        self.messages = []

    def send_json(self, message: Union[dict, str, int, float], to_consumer=None, ignore_trace=False):
        self.messages.append([None, message, to_consumer, ignore_trace])

    def group_send(self, group: str, message: dict, ignore_trace=False):
        self.messages.append([group, message, None, ignore_trace])

    def get_messages(self):
        return self.messages

    # TODO: perhaps passing lambda to handle message and perform post-processing is a good idea
    async def send_all(self, consumer):
        """
        Sends all prepared messages in case post-processing is not needed.
        """
        for group, message, receiver, _ in self.messages:
            if group is not None:
                await consumer.channel_layer.group_send(group, message)
                return

            if receiver is not None:
                await receiver.send_json(message)
                return

            await consumer.send_json(message)


class Handlers:
    def __init__(self):
        self.map = {}

    def register(self, command):
        def inner(func):
            x = inspect.getfullargspec(func)
            positional = x.args
            args = x.varargs
            kwargs = x.varkw
            assert positional[1] == "proxy"
            assert args is None
            assert kwargs is None
            self.map[command] = {'handler': func, 'args': positional[2:]}
            return func
        return inner
