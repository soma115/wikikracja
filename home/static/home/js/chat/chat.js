import WsApi from './wsapi.js';
import DomApi from './domapi.js';
import { makeNotification, formatDate, formatTime, inRoom } from './utility.js';

let WS_API;
let DOM_API;
let current_room = null;

$(document).ready(()=>{
  WS_API = new WsApi();
  DOM_API = new DomApi();

  WS_API.wsOnConnect = async () => {
    // Request data about who is online
    let response = await WS_API.getOnlineUsers();
    let online = response.online_data;
    for (let user of online) {
      DOM_API.updateOnline(user.room_id, user.online);
    }

    // get room id of first room in DOM
    let room_id = $('.room-link[data-room-type="public"]').data('room-id');

    if (room_id) {
      onRoomTryJoin(room_id);
    }

  }
});

const slow_mode = {};
const slow_mode_time_left = {};

export async function onRoomJoin(room_id, room_title, is_public, room_slow_mode, has_notifs) {

  if (current_room) {
    // let server know
    await onRoomTryLeave(current_room);
  }

  current_room = room_id;

  // TODO: send seen confirmation to server after a little while
  DOM_API.seenChat(room_id);
  WS_API.seenRoom(room_id);

  DOM_API.setRoomTitle(room_title);
  DOM_API.setRoomNotifications(has_notifs);

  DOM_API.createRoomDiv(
    room_id, room_title, is_public,
    room_slow_mode, has_notifs);

  slow_mode[room_id] = room_slow_mode || 0;
  DOM_API.setSlowMode(room_id, slow_mode[room_id]);
}

export async function onRoomLeave(room_id) {
  DOM_API.getRoom(room_id).remove();
}

export async function onReceiveMessages(messages) {

  let room_id = messages[0].room_id;
  let msgdiv = DOM_API.getMessagesDiv(room_id);
  DOM_API.removeNoMessagesBanner(room_id);


  for (let message of messages) {
    let type = DOM_API.getRoomType(message.room_id);

    let current_banner = formatDate(message.timestamp);
    let banner_div = DOM_API.getLastMessageBanner(message.room_id);
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
    }

    if (message.your_vote /* You voted for this message e.g. 'upvote' or 'downvote' */) {
        // find message div and make button appear active
        let active_btn = DOM_API.getVoteDiv(message.message_id, message.your_vote);
        active_btn.addClass('active');
    }
  }

  msgdiv.scrollTop(msgdiv.prop("scrollHeight"));
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
    } /* vote was removed */ else {
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
  if ( inRoom(room_id) ) {
    return;
  }
  DOM_API.getRoomIcon(room_id).addClass("room-not-seen");
}

export async function onRoomTryJoin(room_id) {
  DOM_API.getRoomIcon(room_id).addClass("joined");
  WS_API.joinRoom(room_id);
}

export async function onRoomTryLeave(room_id) {
  DOM_API.getRoomIcon(room_id).removeClass("joined");
  WS_API.leaveRoom(room_id);
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
  let text = "<table class='table' style='border-bottom: 1px solid #dee2e6;'>";
  for (let [i, entry] of Object.entries(history.message_history)) {
    let n = parseInt(i) + 1;

    text += `
    <tr>
      <td style='width: 0'>${n}.</td>
      <td>${entry.text}</td>
      <td style='text-align: end; font-size: smaller; color: gray;'>${formatTime(entry.timestamp)}</td>
    </tr>
    `;
  }
  text += "</table>"
  $("#message-history-modal").modal('show').find(".modal-body").html(text);
}

export async function onSubmitMessage(room_id, message, editing_message_id) {
  // message being edited
  if (editing_message_id) {
    WS_API.editMessage(editing_message_id, message);
    DOM_API.stopEditing(room_id);
    return;
  }

  if (slow_mode_time_left[room_id] > 0) {
    return;
  }

  let files = DOM_API.getFiles(room_id);
  let attachments = {};
  let is_anonymous = DOM_API.getAnonymousValue(room_id);

  if (message.replace(" ", "").length == 0 && files.length == 0) {
    return;
  }

  if (files.length) {
    let response = await WS_API.uploadFiles(files);
    attachments.images = response.filenames;
  }

  WS_API.sendMessage(room_id, message, is_anonymous, attachments);

  // remove files from input and image preview
  DOM_API.clearFiles(room_id);

  // Clears input field
  DOM_API.getMessageInput(room_id).val("");

  DOM_API.setSlowModeTimeLeft(room_id, slow_mode[room_id]);
  slow_mode_time_left[room_id] = slow_mode[room_id];

  let i = setInterval( ()=> {
    let d = parseInt(slow_mode_time_left[room_id]);
    if (d == 0) {
        clearInterval(i);
        return;
    }
    slow_mode_time_left[room_id] = d - 1;
    DOM_API.setSlowModeTimeLeft(room_id, slow_mode_time_left[room_id]);
  }, 1000);

}
