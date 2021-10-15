def format_chat_message(
        room_id, user_id,
        anonymous,
        message, message_id,
        upvotes, downvotes,
        new, edited, date):
    """
    Return formatted dict with message data.
    Used to format messages loaded from DB or messages sent by user to chat
    """
    return {
        "type": "chat.message",
        "room_id": room_id,
        "user_id": user_id,
        "message_id": message_id,
        "message": message,
        "anonymous": anonymous,
        "upvotes": upvotes,
        "downvotes": downvotes,
        "new": new,
        "edited": edited,
        "timestamp": int(date.timestamp()) * 1000  # unix to ms
    }
