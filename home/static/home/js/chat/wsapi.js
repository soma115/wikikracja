import { onSocketMessage } from './handlers.js';

export default class WsApi {

    constructor() {
        this.promises = {}

        // Correctly decide between ws:// and wss://
        let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
        let ws_path = ws_scheme + '://' + window.location.host + "/chat/stream/";
        console.log("Connecting to " + ws_path);

        this.socket = new ReconnectingWebSocket(ws_path);

        $(window).on('unload', () => {
            this.socket.close();
        });

        this.socket.onmessage = (e) => {
            let data = JSON.parse(e.data);

            // Handle errors
            if (data.error) {
                alert(data.error);
                return;
            }

            if (data.__TRACE_ID) {
                this.receiveAsync(data);
            } else {
                onSocketMessage(data);
            }
        }

        // Helpful debugging
        this.socket.onopen = function() {
            console.log("Connected to chat socket");
            this.wsOnConnect();
        }.bind(this);

        this.socket.onclose = function() {
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
        let promises = this.promises;

        let promise = new Promise(
            (resolve, reject) => {
                promises[ID] = {
                    resolve,
                    reject
                }
            }
        )

        this.sendJson(obj);
        return promise;
    }

    receiveAsync(obj) {
        let ID = obj.__TRACE_ID;
        if (this.promises[ID] === undefined) {
            console.warn("received __TRACE_ID of " + ID + " that does not exist locally. Was it already resolved? Server should return only one message from this kind of responding handlers");
            return;
        }
        this.promises[ID].resolve(obj);
        delete this.promises[ID];
    }



    async joinRoom(room_id) {
        return await this.sendJsonAsync({
            command: "join",
            room_id: room_id
        });
    }

    seenRoom(room_id) {
        this.sendJson({
            command: "room-seen",
            room_id: room_id
        });
    }

    sendMessage(room_id, message, is_anonymous, attachments) {
        this.sendJson({
            command: "send",
            room_id, // room number
            message, // value, message to send
            is_anonymous,
            attachments
        });
    }

    editMessage(message_id, message) {
        this.sendJson({
            command: "edit-message",
            message_id: message_id,
            new_message: message
        });
    }

    addVote(vote, message_id) {
        this.sendJson({
            command: "message-add-vote",
            vote: vote,
            message_id: message_id
        });
    }

    removeVote(vote, message_id) {
        this.sendJson({
            command: "message-remove-vote",
            vote: vote,
            message_id: message_id
        });
    }

    async leaveRoom(room_id) {
        return await this.sendJsonAsync({
            command: "leave",
            room_id: room_id
        });
    }

    async getOnlineUsers() {
        return await this.sendJsonAsync({
            command: "get-online-users"
        });
    }

    async getMessageHistory(message_id) {
        return await this.sendJsonAsync({
            command: "get-message-history",
            message_id: message_id,
        });
    }

    async getNotificationData() {
        return await this.sendJsonAsync({
            command: 'get-notifications-data'
        })
    }

    async uploadFiles(files) {
        if (files.length == 0) {
            return new Promise((r, _) => r({ 'filenames': [] }));
        }

        let xhr = new XMLHttpRequest();
        let formData = new FormData();

        let promise_funcs = {};

        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4 && xhr.status == 200) {
                promise_funcs.resolve(JSON.parse(xhr.responseText))
            }
        }

        let promise = new Promise((resolve, reject) => {
            promise_funcs.resolve = resolve;
            promise_funcs.reject = reject;
        });

        xhr.open("POST", "upload/", true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        for (let i = 0; i < files.length; ++i) {
            let file = files.item(i);
            let name = file.name;
            let size = file.size;
            if (size > 10000000) {
                alert("file is too big");
                continue;
            }
            formData.append("images", file);
        }
        xhr.send(formData);
        return promise;
    }

    toggleNotifications(room_id, enabled) {
        this.sendJson({
            command: 'toggle-notifications',
            room_id,
            enabled
        });
    }
}