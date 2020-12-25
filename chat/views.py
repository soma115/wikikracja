from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Room


@login_required
def chat(request):
    """
    Root page view. This is essentially a single-page app, if you ignore the
    login and admin parts.
    """
    # Get a list of rooms, ordered alphabetically
    rooms = Room.objects.order_by("title")

    # Render that in the chat template
    return render(request, "chat/chat.html", {
        "rooms": rooms
    })
