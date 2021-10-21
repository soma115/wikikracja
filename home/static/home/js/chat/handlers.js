import {
  onSubmitMessage,
  onUpdateVote,
  onRoomTryLeave,
  onRoomTryJoin,
  onToggleNotifications,
  onMessageHistory,
  onReceiveMessages,
  onRoomUnsee,
  onReceiveVotes,
  onReceiveEdit,
  onReceiveOnlineUpdates,
  onReceiveNotification,
} from './chat.js';

import { _ } from './utility.js';

import DomApi from './domapi.js';

const DOM_API = new DomApi();

export async function onSocketMessage(data) {
  if (data.join) {
    console.warn("deprecated");
  } else if (data.leave) {
    console.warn("deprecated");
  } else if (data.messages) {
    onReceiveMessages(data.messages);
  } else if (data.unsee_room) {
    onRoomUnsee(data.unsee_room);
  } else if (data.notification) {
    let notif = data.notification
    onReceiveNotification(notif);
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
  let edit_message_id = DOM_API.getEditedMessageId();
  let message = DOM_API.getEnteredText();
  onSubmitMessage(message, edit_message_id);
});

$(document).on("keydown", ".message-input", function(e) {
  if (e.keyCode == 13) {
    let edit_message_id = DOM_API.getEditedMessageId();
    let message = DOM_API.getEnteredText();
    onSubmitMessage(message, edit_message_id);
  }
  if (e.key == "ArrowUp") {
    let message = DOM_API.getLatestOwnMessage();
    let message_id = message.data('message-id');
    if (!DOM_API.isEditing()) {
      DOM_API.setEditing(message_id);
    }
  }
});

$(document).on('click', '.attachment-image-container', function(e) {
  let srcs = []
  for (let img of $(this).find("img")) {
    srcs.push(img.src);
  }
  DOM_API.openBigImage(srcs);
});

$(document).on('input', '.notif-switch', function() {
  onToggleNotifications($(this).data("room-id"), $(this).is(":checked"));
});

$(document).on('click', ".stop-editing", function(e) {
  DOM_API.stopEditing();
});

$(document).on('click', ".delete-images-preview", function(e) {
  let room_id = $(this).data("room-id");
  DOM_API.clearFiles(room_id);
});

$(document).on("change", ".file-input", function(e) {
    let files = this.files;
    let preview_container = DOM_API.getPreviewDiv();
    preview_container.empty();

    DOM_API.getPreviewContainer().show();

    for (let i = 0; i < files.length; ++i){
      let file = files.item(i);
      let fr = new FileReader();

      let preview_id = `preview-id-${i}`;

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
  DOM_API.setEditing(message_id);
});

// Room join/leave
$(".room-link").click(function () {
    let room_id = $(this).attr("data-room-id");

    if ($(this).hasClass("joined")) {
      // ignore second click on active room
      //onRoomTryLeave(true);
    } else {
      // Join room
      onRoomTryJoin(room_id);
    }
});

$(document).on('click', '.permission-banner', ()=> {
  DOM_API.showNotificationPermModal(
    _("Enable Notifications"),
    `<div>
    ${_("Chat works better with notifications. You can allow them to see new messages even beyond chat room.")}
    </div>
     <p class='mt-3'>${_("Do you want to receive notifications?")}</p>
     <small class='text-muted'>${_("If nothing happens, you may have ignored permission prompt too many times. check your browser settings to enable them.")}"</small>`
 );
})

$(function() {
  if (!Notification) {
   return;
  }

  if (Notification.permission !== 'granted' && localStorage.notifications !== "No") {
   DOM_API.addPermissionBanner();
 }

})
