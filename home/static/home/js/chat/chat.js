import WsApi from './wsapi.js';
import DomApi from './domapi.js';
import { makeNotification, formatDate } from './utility.js';

let WS_API = new WsApi();
let DOM_API = new DomApi();

// Says if we joined a room or not by if there's a div for it
function inRoom (roomId) {
    return $("#room-" + roomId).length > 0;
};

// global handler for sync WS messages used by wsapi.js
WS_API.receiveSync = (data) => {
  // Handle joining
  if (data.join) {
      console.log("Joining room " + data.join);

      // TODO: send seen confirmation to server after a little while
      DOM_API.seenChat(data.join);
      WS_API.seenRoom(data.join);

      let room_icon = DOM_API.getRoomIcon(data.join);
      let roomdiv = DOM_API.createRoomDiv(data.join, data.title, data.public, data.notifications);


      let submit_handler = async function (e) {
        let room_id = $(this).data('room-id');
        let edit_message_id = DOM_API.getEditedMessageId(room_id);

        // message being edited
        if (edit_message_id) {
          let message = DOM_API.getEnteredText(room_id);
          WS_API.editMessage(edit_message_id, message);
        } else {
          let attachments = {};
          let message = DOM_API.getEnteredText(room_id);
          let is_anonymous = DOM_API.getAnonymousValue(room_id);

          let files = DOM_API.getFiles(room_id);

          if (files.length) {
            let response = await WS_API.uploadFiles(files);
            attachments.images = response.filenames;
          }
          WS_API.sendMessage(data.join, message, is_anonymous, attachments);
        }

        let room = DOM_API.getRoom(room_id);

        // remove data about editing message
        room.find("input.message-input").removeData('edit-message');

        // Clears input field
        room.find("input.message-input").val("");
      }
      
      // Hook up send button to send a message
      roomdiv.find(".send-message").on("click", submit_handler);
      roomdiv.find(".message-input").on("keypress", function(e) {
        if (e.keyCode == 13) {
            submit_handler.bind(this)(e);
        }
      });

  // Handle leaving
  } else if (data.leave) {
      console.log("Leaving room " + data.leave);
      DOM_API.getRoom(data.leave).remove();

  // Handle getting a message
} else if (data.message) {
      let type = DOM_API.getRoomType(data.room_id);
      DOM_API.addMessage(
        data.room_id, data.message_id,
        data.username, data.message,
        data.upvotes, data.downvotes,
        data.own, data.edited, data.attachments,
        data.timestamp, data.latest_timestamp
      );

      let current_banner = formatDate(data.timestamp);
      let banner_div = DOM_API.getLastMessageBanner(data.room_id);
      let previous_banner = banner_div.length ? banner_div.last().text() : null;

      let msgdiv = DOM_API.getMessagesDiv(data.room_id);
      if (previous_banner != current_banner) {
        msgdiv.append(`<div class='date-banner'>${current_banner}</div>`);
      }

      msgdiv.scrollTop(msgdiv.prop("scrollHeight"));

      if (data.new) {
          // handle new message in opened channel somehow
      }

      if (data.your_vote /* You voted for this message e.g. 'upvote' or 'downvote' */) {
          // find message div and make button appear active
          let active_btn = DOM_API.getVoteDiv(data.message_id, data.your_vote);
          active_btn.addClass('active');
      }
  } else if (data.unsee_room) {
    // room is seen if we are in it
    if ( inRoom(data.unsee_room) ) {
      return;
    }
    let room_icon = DOM_API.getRoomIcon(data.unsee_room);
    room_icon.addClass("room-not-seen");


  } else if (data.notification) {

    let notif = data.notification
    makeNotification(notif.title, notif.body, notif.link);

  } else if (data.update_votes) {
    let event = data.update_votes;
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

  } else if (data.edit_message) {
    let edit = data.edit_message;
    // update text of message
    DOM_API.editMessageText(edit.message_id, edit.text, edit.timestamp);
    //show history button
    DOM_API.showHistoryButton(edit.message_id);
  }  else if (data.online_data) {

    let online = data.online_data;
    for (let user of online) {
      DOM_API.updateOnline(user.room_id, user.online);
    }

  } else {
      console.log("Cannot handle message!");  // i.e. empty message
  }
}

WS_API.wsOnConnect = async () => {
  // Request data about who is online
  let response = await WS_API.getOnlineUsers();
  let online = response.online_data;
  for (let user of online) {
    DOM_API.updateOnline(user.room_id, user.online);
  }
}

$(document).on('input', '.notifications-switch', function() {
  let room_id = $(this).data('room-id');
  WS_API.toggleNotifications(room_id, $(this).is(":checked"));
});

$(document).on("change", ".file-input", function(e) {
    let room_id = $(this).data('room-id');
    let files = this.files;
    let preview_container = DOM_API.getPreviewDiv(room_id);
    preview_container.empty();

    for (let i = 0; i < files.length; ++i){
      let file = files.item(i);
      var fr = new FileReader();

      let preview_id = `preview-id-${i}-${room_id}`;

      preview_container.append("<img class='image-preview' id='" + preview_id + "'>");
      fr.onload = function(e) {
        $(`#${preview_id}`)[0].src = this.result;
      };

      fr.readAsDataURL(file);
    }
});
//class='msg-vote' data-event-name="upwote" data-message-id="${data.message_id}"
// Vote button handler
$(document).on("click",".msg-vote", function () {
  let event_type = $(this).data("event-name"); // upvote / downvote
  let message_id = $(this).data("message-id");

  // if is active and pressed it means vote has to be removed
  let is_add = !$(this).hasClass('active');

  // toggle button's state
  $(this).toggleClass('active');

  if (is_add) {
    WS_API.addVote(event_type, message_id);
  } else {
    WS_API.removeVote(event_type, message_id);
  }
});

// Show history button
$(document).on("click",".show-history", async function () {
  let message_id = $(this).data('message-id');
  let history = await WS_API.getMessageHistory(message_id);
});

// Edit button handler
$(document).on("click",".edit-message", function () {
  let message_id = $(this).data("message-id");
  let text = DOM_API.getMessageText(message_id);
  let msg_inp = $(this).closest('.room').find(".message-input");
  msg_inp.val(text);
  msg_inp.data('edit-message', message_id);
});

// Room join/leave
$("li.room-link").click(function () {
    let roomId = $(this).attr("data-room-id");  // Here is  <li class="room-link" data-room-id="{{ room.id }}">{{ room }}</li> used

    if (inRoom(roomId)) {
        // Leave room
        $(this).removeClass("joined");
        WS_API.leaveRoom(roomId);

    } else {
        // Join room
        $(this).addClass("joined");
        WS_API.joinRoom(roomId);

    }
});
$('.room-link').on('click', function() {
  if (!Notification) {
   return;
  }

  if (Notification.permission !== 'granted')
   Notification.requestPermission();
})
