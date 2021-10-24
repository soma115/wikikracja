import imghdr
import json
import uuid

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import Room, Message
from django.contrib.auth.models import User
from chat.forms import RoomForm
from django.http import JsonResponse
from datetime import timedelta as td
from django.utils import timezone
from django.shortcuts import redirect
from django.conf import settings as s
import logging as l

from django.utils.translation import gettext as _

l.basicConfig(filename='wiki.log', datefmt='%d-%b-%y %H:%M:%S', format='%(asctime)s %(levelname)s %(funcName)s() %(message)s', level=l.INFO)

@login_required
def add_room(request):
    """
    Add public chat room
    """
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            return redirect(f"{reverse('chat:chat')}#room_id={room.id}")
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
            t = sorted([i.username, j.username])
            title = '-'.join(t)

            existing_room = Room.find_with_users(i, j)

            # check if room for user i and j exists, if so make sure room name is correct
            if existing_room is not None:
                existing_room.title = title
                existing_room.save()
            # if not, create room
            else:
                r = Room.objects.create(title=title, public=False)
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
        if last_message.time < (timezone.now() - td(days=s.ARCHIVE_CHAT_ROOM)):  # archive after 3 months
            l.info(f'Chat room {i.title} archived.')
            i.archived = True  # archive
            i.save()
        elif last_message.time > (timezone.now() - td(days=s.ARCHIVE_CHAT_ROOM)):  # unarchive
            i.archived = False  # unarchive
            i.save()
        if last_message.time < (timezone.now() - td(days=s.DELETE_CHAT_ROOM)):  # delete after 1 year
            l.info(f'Chat room {i.title} deleted.')
            i.delete()  # delete

    # Archive/Delete old private chat room
    all_private_rooms = Room.objects.filter(public=False)
    for i in all_private_rooms:
        for user in i.allowed.all():
            if not user.is_active:
                i.archived = True
                i.save()
                try:
                    last_message = Message.objects.filter(room_id=i.id).latest('time')
                except Message.DoesNotExist:
                    continue
                if last_message.time < (timezone.now() - td(days=s.DELETE_CHAT_ROOM)):  # delete after 1 year
                    l.info(f'Chat room {i.title} deleted.')
                    i.delete()  # delete
            elif user.is_active:
                i.archived = False
                i.save()

    # Get a list of rooms, ordered alphabetically
    allowed_rooms = Room.objects.filter(allowed=request.user.id).order_by("title")

    # Find out which room to open by default
    last_user_room = None
    messages_by_user = Message.objects.filter(sender=request.user).order_by("-time")
    if messages_by_user.exists():
        last_user_room = messages_by_user.first().room.id

    # Render that in the chat template
    return render(request, "chat/chat.html", {
        'last_used_room': json.dumps(last_user_room),
        'translations': get_translations(),

        'public_active': allowed_rooms.filter(public=True, archived=False),
        'public_archived': allowed_rooms.filter(public=True, archived=True),
        'private_active': allowed_rooms.filter(public=False, archived=False),
        'private_archived': allowed_rooms.filter(public=False, archived=True),

        'user': request.user,
        'ARCHIVE_CHAT_ROOM': td(days=s.ARCHIVE_CHAT_ROOM).days,
        'DELETE_CHAT_ROOM': td(days=s.DELETE_CHAT_ROOM).days,
    })


@csrf_exempt
def upload_image(request):
    filenames = []
    for image in request.FILES.getlist('images'):

        file_type = imghdr.what(image)
        image.seek(0)

        file_bytes = image.read()
        if len(file_bytes) > (s.UPLOAD_IMAGE_MAX_SIZE_MB * 1000000 * 2):
            return JsonResponse({'error': 'file too big'})

        if file_type is None:
            return JsonResponse({'error': 'bad type'})

        filename = f"{uuid.uuid4()}.{file_type}"
        with open(f"{s.BASE_DIR}/media/uploads/{filename}", "wb") as f:
            f.write(file_bytes)
        filenames.append(filename)

    return JsonResponse({'filenames': filenames})


def get_translations():
    _("Manage notifications"),
    _("Today"),
    _("Yesterday"),
    _("Anonymous"),
    _("⚠ slow-mode is active. You can send messages once in %d seconds."),
    _("Enable Notifications"),
    _("Chat works better with notifications. You can allow them to see new messages even beyond chat room."),
    _("Do you want to receive notifications?"),
    _("If nothing happens, you may have ignored permission prompt too many times. Check your browser settings to enable them."),
    _("Yes"),
    _("No, don't show again"),
    _("edit"),
    _("edited"),
    _("Select a chat to start messaging."),
    _("Message History"),
    _("Close"),
    _("This room is empty, be the first one to write something."),
    _("editing: "),
    _("Sunday"), _("Monday"), _("Tuesday"), _("Wednesday"), _("Thursday"), _("Friday"), _("Saturday"),
    _("Jan"), _("Feb"), _("Mar"), _("Apr"), _("May"), _("Jun"), _("Jul"), _("Aug"), _("Sep"), _("Oct"), _("Nov"), _("Dec"),

    strings = [
        "Manage notifications",
        "Today",
        "Yesterday",
        "Anonymous",
        "⚠ slow-mode is active. You can send messages once in %d seconds.",
        "Enable Notifications",
        "Chat works better with notifications. You can allow them to see new messages even beyond chat room.",
        "Do you want to receive notifications?",
        "If nothing happens, you may have ignored permission prompt too many times. Check your browser settings to enable them.",
        "Yes",
        "No, don't show again",
        "edit",
        "edited",
        "Select a chat to start messaging.",
        "Message History",
        "Close",
        "This room is empty, be the first one to write something.",
        "editing: ",
        "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
        "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    translation = {x: _(x) for x in strings}
    # for i in translation:
    #     print(i, _(i))
    return translation
