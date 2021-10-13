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
        var roomdiv = $(  // roomdiv is whole frame with one chat
            "<div class='room' id='room-" + data.join + "'>" +
            "<h5>" + data.title + "</h5>" +
            "<div class='messages'></div>" +
            "<form class='d-flex'><input class='col-12 col-sm'><input class='anonymous-switch' type='checkbox' /><button class='btn btn-danger btn-sm'>↲</button></form>" +
            "</div>"
            );

        // Hook up send button to send a message
        roomdiv.find("form").on("submit", function () {
            socket.send(
                JSON.stringify(
                    {
                        "command": "send",
                        "room": data.join,  // room number
                        "message": roomdiv.find("input").val(),  // value, message to send
                        is_anonymous: roomdiv.find(".anonymous-switch").is(":checked") // get bool from checkbox
            }));

            // Clears input field
            roomdiv.find("input").val(""); // TODO: Here we can plugin edititing old messages (with val)
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
        var msgdiv = $("#room-" + data.room + " .messages");
        var ok_msg = "<div class='message'>" +
                        // "<span class='body'>" + data.time.slice(0,19) + " " + "</span>" +
                        //"<span class='body'>" + data.time + " " + "</span>" +
                        "<span class='body'>" + data.username + ": " + "</span>" +
                        "<span class='username'>" + data.message + "</span>" +
                        "</div>";
        msgdiv.append(ok_msg);
        msgdiv.scrollTop(msgdiv.prop("scrollHeight"));
        if (data.new) {
            alert("New Message");
        }
    } else if (data.online_data) {
      for (let user of data.online_data) {
        let elem = $(`.room-link[data-room-id="${user.room_id}"]`);
        if (user.online) {
          elem.removeClass('offline').addClass('online');
        } else {
          elem.removeClass('online').addClass('offline');
        }
      }
    } else {
        console.log("Cannot handle message!");  // i.e. empty message
    }
};

// Says if we joined a room or not by if there's a div for it
inRoom = function (roomId) {
    return $("#room-" + roomId).length > 0;
};

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
