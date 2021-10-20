import { makeNotification } from '../chat/utility.js';

$(document).ready( ()=> {
  let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
  let ws_path = ws_scheme + '://' + window.location.host + "/chat/stream/";
  console.log("Connecting to " + ws_path);

  let socket = new ReconnectingWebSocket(ws_path);

  socket.onmessage = (e) => {
    let data = JSON.parse(e.data);
    console.log("Got websocket message ", data);

    // Handle errors
    if (data.error) {
      console.error(data.error);
      return;
    }

    if (data.notification) {
       let notif = data.notification;
       onReceiveNotification(notif);

    } else if (data.unsee_room) {
       onRoomUnsee(data.unsee_room);

    } else {
         console.log("Cannot handle message!");
    }
  }
});

export function onReceiveNotification(notification) {
  makeNotification(notification);
}

export function onRoomUnsee(room_id) {
  $(".nav-link[data-route='chat']").addClass("chat-has-messages");
}
