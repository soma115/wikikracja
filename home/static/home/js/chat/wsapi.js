
export default class WsApi {

  constructor() {
    this.promises = {}

    // Correctly decide between ws:// and wss://
    let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    let ws_path = ws_scheme + '://' + window.location.host + "/chat/stream/";
    console.log("Connecting to " + ws_path);

    this.socket = new ReconnectingWebSocket(ws_path);

    this.socket.onmessage = (e) => {
      let data = JSON.parse(e.data);
      console.log("Got websocket message ", data);

      // Handle errors
      if (data.error) {
          alert(data.error);
          return;
      }

      if (data.__TRACE_ID) {
        this.receiveAsync(data);
      } else {
        this.receiveSync(data);
      }
    }

    // Helpful debugging
    this.socket.onopen = function () {
        console.log("Connected to chat socket");
        this.wsOnConnect();
    }.bind(this);

    this.socket.onclose = function () {
        console.log("Disconnected from chat socket");
        this.wsOnDisconnect();
    }.bind(this)
  }

  async wsOnConnect() {

  }

  async wsOnDisconnect() {

  }

  sendJson(obj) {
    this.socket.send(JSON.stringify(obj));
  }

  async sendJsonAsync(obj) {
    let ID = Math.floor(Math.random() * 1000000) + 1;
    obj.__TRACE_ID = ID;
    console.log(this, this.promises);
    let promises = this.promises;

    let promise = new Promise(
      (resolve, reject) => {
        promises[ID] = {
          resolve, reject
        }
      }
    )

    this.sendJson(obj);
    return promise;
  }

  receiveAsync(obj) {
    let ID = obj.__TRACE_ID;
    this.promises[ID].resolve(obj);
    delete this.promises[ID];
  }



  joinRoom(room_id) {
    this.sendJson({
        "command": "join",
        "room_id": room_id
    });
  }

  seenRoom(room_id) {
    this.sendJson({
      "command": "room-seen",
      "room_id": room_id
    });
  }

  sendMessage(room_id, message, is_anonymous) {
    this.sendJson({
        "command": "send",
        "room_id": room_id,  // room number
        "message": message,  // value, message to send
        is_anonymous: is_anonymous // get bool from checkbox
    });
  }

  editMessage(message_id, message) {
      this.sendJson({
        "command": "edit-message",
        "message_id": message_id,
        "new_message": message
      });
  }

  addVote(vote, message_id) {
    this.sendJson({
      "command": "message-add-vote",
      "vote": vote,
      "message_id": message_id
    });
  }

  removeVote(vote, message_id) {
    this.sendJson({
      "command": "message-remove-vote",
      "vote": vote,
      "message_id": message_id
    });
  }

  leaveRoom(room_id) {
    this.sendJson({
      "command": "leave",
      "room_id": room_id
    });
  }

  async getOnlineUsers() {
    return await this.sendJsonAsync({
      command: "get-online-users"
    });
  }

  async getMessageHistory(message_id) {
    return await this.sendJsonAsync({
      "command": "get-message-history",
      "message_id": message_id,
    });
  }
}
