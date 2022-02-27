from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    """
    A room for people to chat in.
    """
    # Allowed users
    allowed = models.ManyToManyField(User, related_name="rooms")

    # For 1to1 chats
    public = models.BooleanField(default=True)

    # For old chats without activity
    archived = models.BooleanField(default=False)
    
    # Room title
    title = models.CharField(max_length=255, unique=True)

    # List of users who saw all messages in this chat
    seen_by = models.ManyToManyField(User, related_name="seen_rooms")

    # List of users who disabled notifications
    muted_by = models.ManyToManyField(User, related_name='muted_rooms')

    def __str__(self):
        return self.title

    def get_other(self, user):
        assert not self.public
        return self.allowed.exclude(id=user.id).first()

    # Name that user will see in chats list
    def displayed_name(self, user):
        if self.public:
            return self.title
        else:
            return self.get_other(user).username

    @property  # adds 'getter', 'setter' and 'deleter' methods
    def group_name(self):
        """
        Returns the Channels Group name that sockets should
        subscribe to to get sent messages as they are generated.
        """
        return "room-%s" % self.id

    @staticmethod
    def find_all_with_users(*users):
        """
        Returns generator of Room objects
        """
        # TODO: replace with better query
        # look through all rooms
        for room in Room.objects.filter(public=False):
            # get all members of the room
            room_members = room.allowed.all()
            # look through users, who must be present in the room
            all_in = True
            for user in users:
                assert isinstance(user, User)
                if user not in room_members:
                    all_in = False
                    break
            if all_in:
                yield room

    @staticmethod
    def find_with_users(*users):
        """
        Returns first matching room.
        """
        for room in Room.find_all_with_users(*users):
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


class MessageVote(models.Model):
    user = models.ForeignKey(User, related_name="votes", on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name="votes", on_delete=models.CASCADE)

    vote_types = [('upvote', 'Upvote'), ('downvote', 'Downvote')]
    vote = models.CharField(choices=vote_types, max_length=50)

    class Meta:
        # can be removed in future to make possible reactions or something like that
        unique_together = ('user', 'message')


# Store changes history separately,
# so you don't have to deal with it unless you need it
class MessageHistory(models.Model):
    """
    All states of given message will be associated with this object.
    They can be easily retrieved like MessageHistory#entries.
    """
    message = models.OneToOneField(Message, on_delete=models.CASCADE)


class MessageHistoryEntry(models.Model):
    """ Stores state of message that is no longer relevant """
    history = models.ForeignKey(MessageHistory, on_delete=models.CASCADE, related_name="entries")
    text = models.TextField()
    time = models.DateTimeField(auto_now=True)


class MessageAttachment(models.Model):
    type = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments")
