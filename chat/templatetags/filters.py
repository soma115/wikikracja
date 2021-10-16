from django import template

register = template.Library()


@register.filter('name_for')
def name_for(room, user):
    """Returns name of room given user will see"""
    return room.displayed_name(user)


@register.filter('seen_by')
def seen_by(room, user):
    return "" if room.seen_by.filter(id=user.id) else "room-not-seen"
