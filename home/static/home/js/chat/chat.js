import WsApi from './wsapi.js';

let WS_API = new WsApi();

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

      let room_icon = $(`.room-link[data-room-id="${data.join}"]`);
      room_icon.addClass('seen');

      var roomdiv = $(  // roomdiv is whole frame with one chat
          "<div class='room' data-room-id='" + data.join + "' id='room-" + data.join + "'>" +
          "<h5>" + data.title + "</h5>" +
          "<div class='messages'></div>" +
          "<form class='d-flex'>" +
          "<input class='col-12 col-sm message-input'>" +
          (data.public ? "<input class='anonymous-switch' type='checkbox' />" : "") +
          "<button class='btn btn-danger btn-sm'>↲</button></form>" +
          "</div>"
      );

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

      // Here is <div id="chats"></div> used
      $("#chats").append(roomdiv);

  // Handle leaving
  } else if (data.leave) {
      console.log("Leaving room " + data.leave);
      $("#room-" + data.leave).remove();

  // Handle getting a message
} else if (data.message) {
      // TODO: handle links in edit updates too
      let URL_REGEX = /(http(s){0,1}:\/\/){0,1}[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)/g;
      let raw_message = data.message
      let matches = raw_message.match(URL_REGEX);
      let formatted = raw_message;
      if (matches != null) {
        for (let match of matches) {
          formatted = raw_message.replace(match, `<a href='${match}'>${match}</a>`);
        }
      }

      let type = $(`.room-link[data-room-id="${data.room_id}"`).attr("data-room-type");

      var msgdiv = $("#room-" + data.room_id + " .messages");
      var ok_msg = `<div class='message' data-message-id=${data.message_id}>` +
                      // "<span class='body'>" + data.time.slice(0,19) + " " + "</span>" +
                      //"<span class='body'>" + data.time + " " + "</span>" +
                      "<span class='username'>" + data.username + ": " + "</span>" +
                      "<span class='body'>" + formatted + "</span>" +
                      (type == "public" ?
                      `<i data-event-name="upvote" data-message-id="${data.message_id}" class="msg-vote fas fa-check"></i>
                       <i data-event-name="downvote" data-message-id="${data.message_id}" class="msg-vote fas fa-times"></i>
                       <div class='msg-upvotes'>${data.upvotes}</div>
                       <div class='msg-downvotes'>${data.downvotes}</div>` : "") +
                       (data.own ? `<div class='edit-message' data-message-id='${data.message_id}'>edit</div>` : "") +
                       `<div class='show-history' ${data.edited ? "" : "style='display:none'"} data-message-id='${data.message_id}'>show history</div>` +
                      "</div>";

      let current_banner = formatDate(data.timestamp);

      let previous_banner = $('.date-banner').length ? $('.date-banner').last().text() : null;

      if (previous_banner != current_banner) {
        msgdiv.append(`<div class='date-banner'>${current_banner}</div>`);
      }

      msgdiv.append(ok_msg);

      msgdiv.scrollTop(msgdiv.prop("scrollHeight"));

      if (data.new) {
          alert("New Message");
      }
      if (data.your_vote /* You voted for this message e.g. 'upvote' or 'downvote' */) {
          // find message div and make button appear active
          let message_div = $(`.message[data-message-id="${data.message_id}"]`);
          let active_btn = message_div.find(`.msg-vote[data-event-name="${data.your_vote}"]`);
          active_btn.addClass('active');
      }
  } else if (data.unsee_room) {
    // room is seen if we are in it
    if ( inRoom(data.unsee_room) ) {
      return;
    }
    let room_icon = $(`.room-link[data-room-id="${data.unsee_room}"]`);
    room_icon.removeClass("seen");
  } else if (data.update_votes) {
    let event = data.update_votes;
    // find message on page by id and update counters
    let message_div = $(`.message[data-message-id="${event.message_id}"]`);

    message_div.find(".msg-upvotes").text(event.upvotes);
    message_div.find(".msg-downvotes").text(event.downvotes);

    if (event.your_vote /* vote type e.g. upvote or downvote or null if it wasn't you who triggered */ ) {
      // find vote button you pressed
      let active_btn = $(`.msg-vote[data-event-name="${event.your_vote}"][data-message-id="${event.message_id}"]`);
      console.log("make all inactive");
      // make all vote buttons appear incative
      message_div.find('.msg-vote').removeClass('active');

      // vote was added
      if (event.add) {
        console.log("activate my vote", active_btn);
        active_btn.addClass('active');
      } /* vote was removed */ else {
        // do nothing, all buttons are inactive
      }

    }

  } else if (data.edit_message) {
    let edit = data.edit_message;
    let message_div = $(`.message[data-message-id="${edit.message_id}"]`);
    // update text of message
    message_div.find("span.body").text(edit.text);
    //show history button
    message_div.find(".show-history").show();

  } else if (data.message_history) {
    // do something with history [{text: '', date: '163423...'}, ...]
  } else {
      console.log("Cannot handle message!");  // i.e. empty message
  }
}

WS_API.wsOnConnect = async () => {
  // Request data about who is online
  online = await WS_API.getOnlineUsers();
  for (let user of online) {
    let room_icon = $(`.room-link[data-room-id="${user.room_id}"]`);
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
  let text = $(`.message[data-message-id="${message_id}"]`).find("span.body").text();
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
