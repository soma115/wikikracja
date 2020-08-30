from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Room
from django.contrib.auth.models import User


@login_required
def index(request):
    """
    Root page view. This is essentially a single-page app, if you ignore the
    login and admin parts.
    """
    # Get a list of rooms, ordered alphabetically
    rooms = Room.objects.order_by("title")

    # TODO: List of users for 1-to-1 communication
    # Get a list o users
    uid = User.objects.filter(is_active=True)

    # Render that in the index template
    return render(request, "chat/index.html", {
        "rooms": rooms, 'uid': uid
    })


def generate_private_chatroom_for_each_user():
    pass
