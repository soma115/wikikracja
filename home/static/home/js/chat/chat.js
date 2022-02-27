import WsApi from './wsapi.js';
import DomApi from './domapi.js';
import { makeNotification, formatDate, formatTime, Lock, parseParms, _ } from './utility.js';

let WS_API;
let DOM_API;
const RoomLock = new Lock();
let current_room = null;


$(() => {
    WS_API = new WsApi();
    DOM_API = new DomApi();

    WS_API.wsOnConnect = async() => {
        // Request data about who is online
        let response = await WS_API.getOnlineUsers();
        let online = response.online_data;
        for (let user of online) {
            DOM_API.updateOnline(user.room_id, user.online);
        }

        let rooms = await WS_API.getNotificationData();
        for (let room_id of rooms.rooms) {
            DOM_API.setRoomNotifications(room_id, true);
        }

        let room_id;

        if (!room_id && window.location.hash) {

            // get room id passed with hash (room was created)
            let hash = window.location.hash.slice(1);
            let obj = parseParms(hash);
            if (obj.room_id) {
                room_id = obj.room_id;
            }
        }

        // get locally stored last room id
        if (!room_id && localStorage.lastUsedRoomID) {
            room_id = localStorage.lastUsedRoomID;
        }

        // check if room_id was passed from backend
        if (!room_id && LAST_USED_ROOM_ID) {
            room_id = LAST_USED_ROOM_ID;
        }

        if (!room_id) {
            // get room id of first room in DOM
            room_id = $('.room-link[data-room-type="public"]').data('room-id');
        }

        if (room_id) {
            onRoomTryJoin(room_id);
        }

    }
});

const slow_mode = {};
const slow_mode_time_left = {};

export async function onReceiveNotification(notification) {
    makeNotification(notification)
}

export async function onRoomTryJoin(room_id) {
    if (RoomLock.locked()) {
        await RoomLock.wait();
    }
    // already in this room
    if (room_id == current_room) {
        return;
    }

    // leave current room
    if (current_room) {
        // only do client stuff, user will leave
        // serverside automatically with join
        await onRoomTryLeave(false);
    }

    DOM_API.getRoomIcon(room_id).addClass("joined");

    // already in the room
    if (current_room == room_id) {
        return;
    }

    // joined another room while awaiting confirmation
    if (current_room) {
        return;
    }

    RoomLock.lock();
    let response = await WS_API.joinRoom(room_id);
    RoomLock.unlock();

    localStorage.lastUsedRoomID = room_id;

    current_room = room_id;
    let title = response.title;
    let has_notifs = response.notifications;
    let is_public = response.public;
    let room_slow_mode = response.slow_mode_delay;
    let cooldown = response.cooldown

    if (cooldown) {
        setSlowMode(room_id, cooldown);
    }

    // TODO: send seen confirmation to server after a little while
    DOM_API.seenChat(room_id);
    WS_API.seenRoom(room_id);

    //DOM_API.setRoomTitle(title);
    DOM_API.setRoomNotifications(has_notifs);

    DOM_API.createRoomDiv(
        current_room, title, is_public,
        room_slow_mode, has_notifs);

    slow_mode[current_room] = room_slow_mode || 0;
    DOM_API.setSlowMode(slow_mode[current_room]);

    // Put cursor into inout field
    document.querySelector("#c7").focus();
}

export async function onRoomTryLeave(sync_with_server) {
    if (RoomLock.locked()) {
        await RoomLock.wait();
    }

    if (sync_with_server) {
        RoomLock.lock();
        await WS_API.leaveRoom(current_room);
        RoomLock.unlock();
    }
    DOM_API.getRoomIcon(current_room).removeClass("joined");
    DOM_API.clearRoomData();

    current_room = null;
}

export async function onReceiveMessages(messages) {
    let room_id = messages[0].room_id;

    // received data for wrong room if message was delayed
    if (room_id != current_room) {
        console.warn("received message for wrong room");
        return;
    }

    let msgdiv = DOM_API.getMessagesDiv();
    DOM_API.removeNoMessagesBanner();

    for (let message of messages) {
        let type = DOM_API.getRoomType(message.room_id);
        let current_banner = formatDate(message.timestamp);
        let banner_div = DOM_API.getLastMessageBanner();
        let previous_banner = banner_div.length ? banner_div.last().text() : null;

        if (previous_banner != current_banner) {
            msgdiv.append(`<div class='date-banner'>${current_banner}</div>`);
        }

        DOM_API.addMessage(
            message.room_id, message.message_id,
            message.username, message.message,
            message.upvotes, message.downvotes, message.your_vote,
            message.own, message.edited, message.attachments,
            message.timestamp, message.latest_timestamp
        );

        if (message.new) {
            // handle new message in opened channel somehow
            // if page is not active (user at other browser tab)
            if (document.hidden) {
                makeNotification({
                    title: message.username,
                    body: message.message
                })
            }
        }
        if (message.your_vote /* You voted for this message e.g. 'upvote' or 'downvote' */ ) {
            // find message div and make button appear active
            let active_btn = DOM_API.getVoteDiv(message.message_id, message.your_vote);
            active_btn.addClass('active');
        }
    }
    msgdiv.scrollTop(msgdiv.prop("scrollHeight"));
    $("#room > div.chat-controls > div > input").focus();
}

export async function onReceiveVotes(event) {
    // find message on page by id and update counters
    let message_div = DOM_API.getMessageDiv(event.message_id);

    DOM_API.getMessageUpvotesCountDiv(event.message_id).text(event.upvotes);
    DOM_API.getMessageDownvotesCountDiv(event.message_id).text(event.downvotes);

    if (event.your_vote /* vote type e.g. upvote or downvote or null if it wasn't you who triggered */ ) {
        // find vote button you pressed
        let active_btn = DOM_API.getVoteDiv(event.message_id, event.your_vote);
        // make all vote buttons appear incative
        message_div.find('.msg-vote').removeClass('active');

        // vote was added
        if (event.add) {
            active_btn.addClass('active');
        } /* vote was removed */
        else {
            // do nothing, all buttons are inactive
        }
    }
}

export async function onReceiveEdit(edit_info) {
    // update text of message
    DOM_API.editMessageText(edit_info.message_id, edit_info.text, edit_info.timestamp);
    //show history button
    DOM_API.showHistoryButton(edit_info.message_id);
}

export async function onReceiveOnlineUpdates(updates) {
    for (let update of updates) {
        DOM_API.updateOnline(update.room_id, update.online);
    }
};

export async function onRoomUnsee(room_id) {
    // room is seen if we are in it
    if (current_room == room_id) {
        return;
    }
    DOM_API.getRoomIcon(room_id).addClass("room-not-seen");
}

export async function onUpdateVote(vote, message_id, is_add) {
    // toggle button's state
    $(this).toggleClass('active');

    if (is_add) {
        WS_API.addVote(vote, message_id);
    } else {
        WS_API.removeVote(vote, message_id);
    }
}

export async function onToggleNotifications(room_id, is_enabled) {
    WS_API.toggleNotifications(room_id, is_enabled);
}

export async function onMessageHistory(message_id) {
    let history = await WS_API.getMessageHistory(message_id);
    history = history.message_history.map(
        x => { x.formattedTime = formatTime(x.timestamp); return x; }
    );

    DOM_API.showHistoryModal(_("Changes History"), history);
}

export async function onSubmitMessage(message, editing_message_id) {
    // message being edited
    if (editing_message_id) {
        WS_API.editMessage(editing_message_id, message);
        DOM_API.stopEditing();
        return;
    }

    if (slow_mode_time_left[current_room] > 0) {
        return;
    }

    let files = DOM_API.getFiles();
    let attachments = {};
    let is_anonymous = DOM_API.getAnonymousValue();

    if (message.replace(" ", "").length == 0 && files.length == 0) {
        return;
    }

    if (files.length) {
        let response = await WS_API.uploadFiles(files);
        attachments.images = response.filenames;
    }

    WS_API.sendMessage(current_room, message, is_anonymous, attachments);

    // remove files from input and image preview
    DOM_API.clearFiles();

    // Clears input field
    DOM_API.getMessageInput().val("");

    setSlowMode(current_room, slow_mode[current_room]);
}

function setSlowMode(room_id, time_left) {
    if (!time_left) {
        console.warn("falsy time left for cooldown");
        return;
    }

    if (slow_mode_time_left[room_id]) {
        console.warn("tried to set cooldown on room with active cooldown");
        return;
    }

    slow_mode_time_left[room_id] = time_left;

    let i = setInterval(() => {
        slow_mode_time_left[room_id]--;
        if (room_id == current_room) {
            DOM_API.setSlowModeTimeLeft(slow_mode_time_left[room_id]);
        }
        if (slow_mode_time_left[room_id] == 0) {
            clearInterval(i);
            return;
        }
    }, 1000);
}