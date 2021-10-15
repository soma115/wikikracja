import WsApi from './wsapi.js';
import DomApi from './domapi.js';

let WS_API = new WsApi();
let DOM_API = new DomApi();

// Says if we joined a room or not by if there's a div for it
function inRoom (roomId) {
    return $("#room-" + roomId).length > 0;
};

function formatDate(someDateTimeStamp) {
    let fulldays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    let dt = new Date(someDateTimeStamp),
        date = dt.getDate(),
        month = months[dt.getMonth()],
        timeDiff = someDateTimeStamp - Date.now(),
        diffDays = new Date().getDate() - date,
        diffMonths = new Date().getMonth() - dt.getMonth(),
        diffYears = new Date().getFullYear() - dt.getFullYear();

    if (diffYears === 0 && diffDays === 0 && diffMonths === 0) {
      return "Today";
    } else if(diffYears === 0 && diffDays === 1) {
      return "Yesterday";
    } else if(diffYears === 0 && diffDays === -1) {
      return "Tomorrow";
    } else if(diffYears === 0 && (diffDays < -1 && diffDays > -7)) {
      return fulldays[dt.getDay()];
    } else if(diffYears >= 1) {
      return month + " " + date + ", " + new Date(someDateTimeStamp).getFullYear();
    } else {
        return month + " " + date;
    }
}

// global handler for sync WS messages used by wsapi.js
WS_API.receiveSync = (data) => {
  // Handle joining
  if (data.join) {
      console.log("Joining room " + data.join);

      // TODO: send seen confirmation to server after a little while
      WS_API.seenRoom(data.join);

      let room_icon = DOM_API.getRoomIcon(data.join);
      room_icon.addClass('seen');
      let roomdiv = DOM_API.createRoomDiv(data.join, data.title, data.public);

      // Hook up send button to send a message
      roomdiv.find("form").on("submit", function () {
          let edit_message_id = roomdiv.find("input.message-input").data('edit-message');
          let to_send;

          // message being edited
          if (edit_message_id) {
            let message = roomdiv.find("input.message-input").val();
            WS_API.editMessage(edit_message_id, message);
          } else {
            to_send = {
                "command": "send",
                "room": data.join,  // room number
                "message": roomdiv.find("input.message-input").val(),  // value, message to send
                is_anonymous: roomdiv.find(".anonymous-switch").is(":checked") // get bool from checkbox
            }
            let message = roomdiv.find("input.message-input").val();
            let is_anonymous = roomdiv.find(".anonymous-switch").is(":checked");
            WS_API.sendMessage(data.join, message, is_anonymous)
          }


          // remove data about editing message
          roomdiv.find("input.message-input").removeData('edit-message');

          // Clears input field
          roomdiv.find("input.message-input").val(""); // TODO: Here we can plugin edititing old messages (with val)
          return false;
      });

  // Handle leaving
  } else if (data.leave) {
      console.log("Leaving room " + data.leave);
      getRoom(data.leave).remove();

  // Handle getting a message
} else if (data.message) {
      let type = DOM_API.getRoomType(data.room_id);
      DOM_API.addMessage(
        data.room_id, data.message_id,
        data.username, data.message,
        data.upvotes, data.downvotes,
        data.own, data.edited
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
          alert("New Message");
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
    room_icon.removeClass("seen");
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
    DOM_API.editMessageText(edit.message_id, edit.text);
    //show history button
    DOM_API.showHistoryButton(edit.message_id);
  }  else {
      console.log("Cannot handle message!");  // i.e. empty message
  }
}

WS_API.wsOnConnect = async () => {
  // Request data about who is online
  let response = await WS_API.getOnlineUsers();
  let online = response.online_data;
  for (let user of online) {
    let room_icon = DOM_API.getRoomIcon(user.room_id);
    if (user.online) {
      room_icon.removeClass('offline').addClass('online');
    } else {
      room_icon.removeClass('online').addClass('offline');
    }
  }
}

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
