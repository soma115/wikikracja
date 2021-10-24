from django import template

register = template.Library()


@register.filter('name_for')
def name_for(room, user):
    """Returns name of room given user will see"""
    return room.displayed_name(user)


@register.filter('seen_by')
def seen_by(room, user):
    return "" if (room.seen_by.filter(id=user.id) or room.messages.all().count() == 0) else "room-not-seen"


@register.filter("has_messages")
def has_messages(user):
    for room in user.rooms.all():
        # print(room)
        seen_by_user = room.seen_by.filter(id=user.id)
        # print(f"is seen: {seen_by_user}")
        # print(f"has messages: {room.messages.all().count()}")

    return "chat-has-messages" if \
        [room for room in user.rooms.all() if not room.seen_by.filter(id=user.id).exists() and
         room.messages.all().count() > 0] \
        else ""
