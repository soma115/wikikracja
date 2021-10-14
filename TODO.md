We need working chat application with persistence (messages are saved to DB and presented after login).


List of requirements:

- Integration

    **expected state**: Integration with Diango must be kept. Chat should not use usernames for identification but user id's. Usernames should be presented in the UI. 

    **current state**: Chat is integrated with existing Django project https://github.com/soma115/wikikracja. Curently chat uses usernames as idetifiers which is incorrect. Fixed rooms list and 1 to 1 messages - those 2 is done but should be repaired.


- Persistance

    **expected state**: Currently implemented persistance is not corect and needs to be modify probably from scratch.

    **current state**: The problem is that all messages are loaded as a whole each time chat is reloaded. In this setup creating notifications (about new message) is not possible.


- Slowmode

    **expected state**: Some public rooms should have slowmode (cooldown time before next message can be send). Room name and cooldown time is set up in settings_custom.py per room name. Small counter shows when user can send next message.
    
    **current state**: functionality does not exists


- Anonymous message

    **expected state**: Users should be able to send message anonymously or under own name to public rooms (checkbox). No need for anonymity on DB level - just on UI. 
    
    **current state**: functionality does not exists


- 1 to 1 messages

    **expected state**: If user is present his name changes color. Click username to open 1to1 chat
    
    **current state**: Currently usernames are displayed incorrectly. Other than that 1to1 is mostly implemented.

- Mark channel as 'read'

    **expected state**: Mark channel as 'read' after 5 seconds after it was opened
    
    **current state**: functionality does not exists


- Vote up, vote down

    **expected state**: Vote up, vote down in chat for each message. Those votes are always anonymous. One up/down per user. Only sum of up/down votes is displayed. Sender gives himself 1 upvote automatically.
    
    **current state**: functionality does not exists


- Edit message

    **expected state**: Ability to edit already send messages. Old version is kept in DB. If message was edited there is small link next to a message which opens new tab with history. Timestamps for each one.
    
    **current state**: functionality does not exists


- Clickable links

    **expected state**: Pasted links should be clickable

    **current state**: functionality does not exists


- Banners for each day

    **expected state**: Days should be separated with banners like Today, Yestarday, 2 days ago and then just dates.
    
    **current state**: functionality does not exists


- Translation

    **expected state**: All fixed strings should be translatable to other languages (with django translation module if possible)

    **current state**: functionality does not exists


- Pictures in chat

    **expected state**: Ability to paste/upload picture to message.

    **current state**: functionality does not exists


- Message timestamp

    **expected state**: Messages should have timestamp (very small font). Timestamp should be taken from newest version. Of course messages are sorted by first version timestamp.

    **current state**: functionality does not exists


- Desktop notifications

    **expected state**: Sound in browser, changed favicon and more if possible. Also in app notifications (on menu bar). Rooms/private should be marked if contain new message.

    **current state**: functionality does not exists


- Notifications on/off

    **expected state**: Checkbox to disable notifications from each public _room/private_room separately.

    **current state**: functionality does not exists
    

Other requirements
- Prefereably clean JS. If framework has to be used - we need to negotiate which one will it be.
- Look and feel can be similar to Slack
- modification chat/models.py is allowed
- all global variables in settings_custom.py
- Simplicity and clean code is very much apriecited. That's because chat will be developed much further in the future. Code should be over-commented.

Requirements
- Experience with JavaScript is most important for this job. 
- Python, Django and Channels2 knowledge will be needed too.

We are using:
- Centos 8 Server
- Python 3.6.8
- Django 3.1




Next version:
- number of new messages should be presented
- if there are new messages - chat windows should be scrolled to first new message.
- Users should use picters from profile
- @ woła osobę





I've tried to create really detailed description of this job. Please read through it.
You can also check existing code on https://github.com/soma115/wikikracja
Please check if you are able to create mentioned functionalities and integrate it to existing project.
Let me know if those requirements are fine for you.