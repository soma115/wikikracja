from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    """
    A room for people to chat in.
    """
    # Allowed users
    allowed = models.ManyToManyField(User)

    # For 1to1 chats
    public = models.BooleanField(default=True)

    # For old chats without activity
    archived = models.BooleanField(default=False)
    
    # Room title
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title

    @property  # adds 'getter', 'setter' and 'deleter' methods
    def group_name(self):
        """
        Returns the Channels Group name that sockets should
        subscribe to to get sent messages as they are generated.
        """
        return "room-%s" % self.id

    @staticmethod
    def find_with_users(*users):
        """
        Returns Room object
        """
        # TODO: replace with better query
        for room in Room.objects.filter(public=False):
            room_members = room.allowed.all()
            for user in users:
                assert isinstance(user, User)
                if user not in room_members:
                    return None
            return room


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    time = models.DateTimeField(auto_now=True)
    text = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, related_name="messages")
    anonymous = models.BooleanField(default=False)
    # TODO: revisions (editMessage(), deleteMessage())

    class Meta:
        unique_together = ('sender', 'text', 'room', 'time')
