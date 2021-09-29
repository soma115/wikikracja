We need working chat application with persistence (messages are saved to DB and presented after login).
You may use this tutorial (https://channels.readthedocs.io/en/latest/) as a starting point but persistence needs to be added.

List of requirements:

|     title    |   expected state       |       current state     |

- Integration  |  Integration with Diango must be kept.  |  Chat is integrated with existing Django project https://github.com/soma115/wikikracja
- Persistance  |  Currently implemented persistance is not corect and needs to be modify probably from scratch. The problem is that all messages are loaded as a whole each time chat is reloaded. In this setup creating notifications (about new message) is not possible.
- Slowmode. Some public rooms should have slowmode (cooldown time before next message will be allowed). Room name and cooldown time is set up in settings_custom.py per room. Small counter shows when user can send next message.
- Users should be able to send message anonymously or under own name to public rooms (checkbox). No need for anonymity on DB level - just on UI.
- 1 to 1 messages. If user is present his name changes color. Currently usernames are displayed incorrectly. Other than that it is mostly implemented.
- Users should use picters from profile
- Mark channel as 'read' after 5 seconds when opened
- Vote up, vote down in chat for each message. Those votes are always anonymous. One up/down per user. Only sum of up/down votes is displayed. Sender gives himself 1 upvote automatically.
- Ability to edit already send messages. Old version is kept in DB. Small link to old versions opens in new tab. Timestamps for each one.
- Pasted links should be clickable
- Days should be separated with banners like Today, Yestarday, 2 days ago and then just dates.
- All strings should be translatable to other languages (with django translation module if possible)
- Ability to paste/upload picture to message.
- Messages should have timestamp (very small font). Timestamp should be taken from newest version.
- Desktop notifications (sound in browser, changed favicon and more if possible) and in app notifications (on menu bar). Rooms/private messages in bold if contain new message.
- Checkbox to disable notifications from each public _room/private_room separately.

- Prefereably clean JS. If framework has to be used - we need to negotiate which one will it be.
- Look and feel can be similar to Slack
- modification chat/models.py is allowed

Simplicity and clean code is very much apriecited. That's because chat will be developed much further in the future. Code should be over-commented.

Experience with JavaScript is most important for this job. 
Python, Django and Channels2 knowledge will be needed too.

We are using:
Centos 8 Server
Python 3.6.8
Django 3.1


Next version:
- number of new messages should be presented
- if there are new messages - chat windows should be scrolled to first new message.