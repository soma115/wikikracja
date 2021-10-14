$(function () {

// Correctly decide between ws:// and wss://
var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var ws_path = ws_scheme + '://' + window.location.host + "/chat/stream/";
console.log("Connecting to " + ws_path);
var socket = new ReconnectingWebSocket(ws_path);


// Handle incoming messages
socket.onmessage = function (message) {
    // Decode the JSON
    var data = JSON.parse(message.data);
    console.log("Got websocket message ", data);
    // Handle errors
    if (data.error) {
        alert(data.error);
        return;
    }

    // Handle joining
    if (data.join) {
        console.log("Joining room " + data.join);

        // TODO: send seen confirmation to server after a little while
        socket.send(JSON.stringify({
            "command": "room-seen",
            "room_id": data.join
        }));

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
              to_send = {
                "command": "edit-message",
                "message_id": edit_message_id,
                "message": roomdiv.find("input.message-input").val()
              }
            } else {
              to_send = {
                  "command": "send",
                  "room": data.join,  // room number
                  "message": roomdiv.find("input.message-input").val(),  // value, message to send
                  is_anonymous: roomdiv.find(".anonymous-switch").is(":checked") // get bool from checkbox
              }
            }
            socket.send(JSON.stringify(to_send));

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
        let type = $(`.room-link[data-room-id="${data.room}"`).attr("data-room-type");
        var msgdiv = $("#room-" + data.room + " .messages");
        var ok_msg = `<div class='message' data-message-id=${data.message_id}>` +
                        // "<span class='body'>" + data.time.slice(0,19) + " " + "</span>" +
                        //"<span class='body'>" + data.time + " " + "</span>" +
                        "<span class='username'>" + data.username + ": " + "</span>" +
                        "<span class='body'>" + data.message + "</span>" +
                        (type == "public" ?
                        `<i data-event-name="upvote" data-message-id="${data.message_id}" class="msg-vote fas fa-check"></i>
                         <i data-event-name="downvote" data-message-id="${data.message_id}" class="msg-vote fas fa-times"></i>
                         <div class='msg-upvotes'>${data.upvotes}</div>
                         <div class='msg-downvotes'>${data.downvotes}</div>` : "") +
                         `<div class='edit-message' data-message-id='${data.message_id}'>edit</div>` +
                         `<div class='show-history' ${data.edited ? "" : "style='display:none'"} data-message-id='${data.message_id}'>show history</div>` +
                        "</div>";
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
    } else if (data.online_data) {
      for (let user of data.online_data) {
        let room_icon = $(`.room-link[data-room-id="${user.room_id}"]`);
        if (user.online) {
          room_icon.removeClass('offline').addClass('online');
        } else {
          room_icon.removeClass('online').addClass('offline');
        }
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

      console.log(message_div, event);
      message_div.find(".msg-upvotes").text(event.upvotes);
      message_div.find(".msg-downvotes").text(event.downvotes);

      if (data.your_vote /* vote type e.g. upvote or downvote or null if it wasn't you who triggered */ ) {
        // find vote button you pressed
        let active_btn = message_div.find(`.msg-vote[data-event-name="${data.your_vote}"]`);

        // make all vote buttons appear incative
        message_div.find('.msg-vote').removeClass('active');

        // vote was added
        if (data.add) {
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

    } else {
        console.log("Cannot handle message!");  // i.e. empty message
    }
};

// Says if we joined a room or not by if there's a div for it
inRoom = function (roomId) {
    return $("#room-" + roomId).length > 0;
};

//class='msg-vote' data-event-name="upwote" data-message-id="${data.message_id}"
// Vote button handler
$(document).on("click",".msg-vote", function () {
  let event_type = $(this).data("event-name"); // upvote / downvote
  let message_id = $(this).data("message-id");
  // if is active and pressed it means vote has to be removed
  let is_add = !$(this).hasClass('active');

  // toggle button's state
  $(this).toggleClass('active');

  socket.send(JSON.stringify({
    "command": (is_add ? "message-add-vote" : "message-remove-vote"),
    "event": event_type,
    "message_id": message_id,
  }))
});

// Show history button
$(document).on("click",".show-history", function () {
  socket.send(JSON.stringify({
    "get-message-history": $(this).data('message-id')
  }))
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
        roomId = $(this).attr("data-room-id");  // Here is  <li class="room-link" data-room-id="{{ room.id }}">{{ room }}</li> used

    if (inRoom(roomId)) {
        // Leave room
        $(this).removeClass("joined");
        socket.send(JSON.stringify({
            "command": "leave",
            "room": roomId
        }));
    } else {
        // Join room
        $(this).addClass("joined");
        socket.send(JSON.stringify({
            "command": "join",
            "room": roomId
        }));
    }
});

// Helpful debugging
socket.onopen = function () {
    console.log("Connected to chat socket");

    // Request data about who is online
    socket.send(JSON.stringify({
      command: "get-online-users",
    }));
};
socket.onclose = function () {
    console.log("Disconnected from chat socket");
}

});
