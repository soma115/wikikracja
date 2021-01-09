from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Room, Message
from django.contrib.auth.models import User
from chat.forms import RoomForm
from django.http import HttpResponse
from datetime import datetime as dt
from datetime import timedelta as td
from django.utils import timezone
from django.shortcuts import redirect

import logging as l

l.basicConfig(filename='wiki.log', datefmt='%d-%b-%y %H:%M:%S', format='%(asctime)s %(levelname)s %(funcName)s() %(message)s', level=l.INFO)

@login_required
def add_room(request):
    """
    Add public chat room
    """
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('chat:chat')
    else:
        form = RoomForm()
    return render(request, 'chat/add.html', {'form': form})

@login_required
def chat(request):
    """
    Root page view. This is essentially a single-page app, if you ignore the
    login and admin parts.
    """

    # Create all 1to1 rooms
    active_users = User.objects.filter(is_active=True)
    for i in active_users:
        for j in active_users:
            # User A will not talk to user A
            if i == j:  
                continue
            # Avoid A-B B-A because it is the same thing
            t=sorted([i.username, j.username])  
            r, created = Room.objects.get_or_create(title='-'.join(t), public=False)
            r.allowed.set((i, j,))

    # Add all active_users to public_rooms.
    # It is done here because it is needed when:
    # 1. new public room is created
    # 2. new user is activated
    public_rooms = Room.objects.filter(public=True)
    for i in public_rooms:
        i.allowed.set(active_users)

    # Archive/Delete old public chat rooms
    all_public_rooms = Room.objects.filter(public=True)
    for i in all_public_rooms:
        try:
            last_message = Message.objects.filter(room_id=i.id).latest('time')
        except Message.DoesNotExist:
            continue
        if last_message.time < (timezone.now() - td(days=90)):  # archive after 3 months
            l.info(f'Chat room {i.title} archived.')
            i.archived = True  # archive
            i.save()
        elif last_message.time > (timezone.now() - td(days=90)):  # unarchive
            i.archived = False  # unarchive
            i.save()
        if last_message.time < (timezone.now() - td(days=365)):  # delete after 1 year
            l.info(f'Chat room {i.title} deleted.')
            i.delete()  # delete

    # Archive/Delete old private messages
    all_private_rooms = Room.objects.filter(public=False)
    for i in all_private_rooms:
        for user in i.allowed.all():
            if user.is_active == False:
                i.archived = True
                i.save()
                try:
                    last_message = Message.objects.filter(room_id=i.id).latest('time')
                except Message.DoesNotExist:
                    continue
                if last_message.time < (timezone.now() - td(days=365)):  # delete after 1 year
                    l.info(f'Chat room {i.title} deleted.')
                    i.delete()  # delete
            elif user.is_active == True:
                i.archived = False
                i.save()


    # Get a list of rooms, ordered alphabetically
    allowed_rooms = Room.objects.filter(allowed=request.user.id).order_by("title")

    # Render that in the chat template
    return render(request, "chat/chat.html", {
        "allowed_rooms": allowed_rooms,
    })
