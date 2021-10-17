import {
  onSubmitMessage,
  onUpdateVote,
  onRoomTryLeave,
  onRoomTryJoin,
  onToggleNotifications,
  onMessageHistory,
  onRoomJoin,
  onRoomLeave,
  onReceiveMessages,
  onRoomUnsee,
  onReceiveVotes,
  onReceiveEdit,
  onReceiveOnlineUpdates,
} from './chat.js';

import { inRoom } from './utility.js';

import DomApi from './domapi.js';

const DOM_API = new DomApi();

export async function onSocketMessage(data) {
  if (data.join) {
    onRoomJoin(data.join, data.title, data.public, data.slow_mode_delay, data.notifications);
  } else if (data.leave) {
    onRoomLeave(data.leave);
  } else if (data.messages) {
    onReceiveMessages(data.messages);
  } else if (data.unsee_room) {
    onRoomUnsee(data.unsee_room);
  } else if (data.notification) {
    let notif = data.notification
    makeNotification(notif.title, notif.body, notif.link);
  } else if (data.update_votes) {
    let event = data.update_votes;
    onReceiveVotes(event);
  } else if (data.edit_message) {
    let edit = data.edit_message;
    onReceiveEdit(edit);
  }  else if (data.online_data) {
    onReceiveOnlineUpdates(data.online_data);
  } else {
      console.log("Cannot handle message!");
  }
}

// Hook up send button to send a message
$(document).on("click", ".send-message", function() {
  let room_id = $(this).data('room-id');
  let edit_message_id = DOM_API.getEditedMessageId(room_id);
  let message = DOM_API.getEnteredText(room_id);
  onSubmitMessage(room_id, message, edit_message_id);
});

$(document).on("keydown", ".message-input", function(e) {
  if (e.keyCode == 13) {
    let room_id = $(this).data('room-id');
    let edit_message_id = DOM_API.getEditedMessageId(room_id);
    let message = DOM_API.getEnteredText(room_id);
    onSubmitMessage(room_id, message, edit_message_id);
  }
  if (e.key == "ArrowUp") {
    let room_id = $(this).data('room-id');
    let message = DOM_API.getLatestOwnMessage(room_id);
    let message_id = message.data('message-id');
    if (!DOM_API.isEditing(room_id)) {
      DOM_API.setEditing(room_id, message_id);
    }
  }
});

$(document).on('click', '.attached-image', function(e) {
  DOM_API.openBigImage($(this).attr('src'));
});

$(document).on('click', '#big-image img', function(e){
  e.stopPropagation();
});

$(document).on('click', '.close-big-image', function() {
  DOM_API.closeBigImage();
});

$(document).on('keydown', function() {
  DOM_API.closeBigImage();
});

$(document).on('click', '#big-image', function(e) {
  DOM_API.closeBigImage();
});

$(document).on('input', '.notifications-switch', function() {
  let room_id = $(this).data('room-id');
  onToggleNotifications(room_id, $(this).is(":checked"));
});

$(document).on('click', ".stop-editing", function(e) {
  let room_id = $(this).data("room-id");
  DOM_API.stopEditing(room_id);
});

$(document).on('click', ".delete-images-preview", function(e) {
  let room_id = $(this).data("room-id");
  DOM_API.clearFiles(room_id);
});

$(document).on("change", ".file-input", function(e) {
    let room_id = $(this).data('room-id');
    let files = this.files;
    let preview_container = DOM_API.getPreviewDiv(room_id);
    preview_container.empty();

    DOM_API.getPreviewContainer(room_id).show();

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

// Vote button handler
$(document).on("click",".msg-vote", function () {
  let event_type = $(this).data("event-name"); // upvote / downvote
  let message_id = $(this).data("message-id");

  // if is active and pressed it means vote has to be removed
  let is_add = !$(this).hasClass('active');

  onUpdateVote(event_type, message_id, is_add);
});

// Show history handler
$(document).on("click",".show-history", async function () {
  let message_id = $(this).data('message-id');
  onMessageHistory(message_id);
});

// Edit button handler
$(document).on("click",".edit-message", function () {
  let message_id = $(this).data("message-id");
  let room_id = $(this).data('room-id');
  DOM_API.setEditing(room_id, message_id);
});

// Room join/leave
$("li.room-link").click(function () {
    let room_id = $(this).attr("data-room-id");  // Here is  <li class="room-link" data-room-id="{{ room.id }}">{{ room }}</li> used

    if (inRoom(room_id)) {
        // Leave room
        onRoomTryLeave(room_id);

    } else {
        // Join room
        onRoomTryJoin(room_id);
    }
});
$('.room-link').on('click', function() {
  if (!Notification) {
   return;
  }

  if (Notification.permission !== 'granted')
   Notification.requestPermission();
})
