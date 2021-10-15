export default class DomApi {
  getRoomIcon(room_id) {
    return $(`.room-link[data-room-id="${room_id}"]`);
  }

  createRoomDiv(room_id, title, is_public) {
    let roomdiv = $(  // roomdiv is whole frame with one chat
        "<div class='room' data-room-id='" + room_id + "' id='room-" + room_id + "'>" +
        "<h5>" + title + "</h5>" +
        "<div class='messages'></div>" +
        `<div class='image-preview-container' data-room-id='${room_id}'></div>` +
        "<form class='d-flex' onsubmit='false'>" +
        "<input class='col-12 col-sm message-input'>" +
        `<input type='file' class='file-input' data-room-id='${room_id}' multiple='multiple'>` +
        (is_public ? "<input class='anonymous-switch' type='checkbox' />" : "") +
        "<button class='btn btn-danger btn-sm'>↲</button></form>" +
        "</div>"
    );

    // Here is <div id="chats"></div> used
    $("#chats").append(roomdiv);
    return roomdiv;
  }

  getRoom(room_id) {
    return $(`#room-${room_id}`)
  }

  getMessagesDiv(room_id) {
    return this.getRoom(room_id).find('.messages');
  }

  addMessage(room_id, message_id, username, message, upvotes, downvotes, own, edited, attachments) {
    let type = this.getRoomType(room_id);

    let attachments_html = "<div class='attachment-image-container'>";

    for (let filename of attachments?.images || []) {
      attachments_html += `<img class='attached-image' src='/media/uploads/${filename}'>`
    }
    attachments_html += "</div>"

    let ok_msg = `
    <div class='message' data-message-id=${message_id}>` +
    "<span class='username'>" + username + ": " + "</span>" +
    "<div class='body'>" +
    attachments_html +
    "<span class='text'>" +
    this.formatMessage(message) +
    "</span>" +
    "</div>" +
    (type == "public" ?
    `<i data-event-name="upvote" data-message-id="${message_id}" class="msg-vote fas fa-check"></i>
     <i data-event-name="downvote" data-message-id="${message_id}" class="msg-vote fas fa-times"></i>
     <div class='msg-upvotes'>${upvotes}</div>
     <div class='msg-downvotes'>${downvotes}</div>` : "") +
     (own ? `<div class='edit-message' data-message-id='${message_id}'>edit</div>` : "") +
     `<div class='show-history' ${edited ? "" : "style='display:none'"} data-message-id='${message_id}'>show history</div>` +
    "</div>";
    this.getMessagesDiv(room_id).append(ok_msg);
  }

  addDateBanner(text) {
    getMessagesDiv().append(`<div>${text}</div>`)
  }

  getMessageDiv(message_id) {
    return $(`.message[data-message-id="${message_id}"]`);
  }

  getRoomIcon(room_id) {
    return $(`.room-link[data-room-id="${room_id}"]`);
  }

  getMessageUpvotesCountDiv(message_id) {
    return this.getMessageDiv(message_id).find(".msg-upvotes");
  }

  getMessageDownvotesCountDiv(message_id) {
    return this.getMessageDiv(message_id).find(".msg-downvotes");
  }

  getVoteDiv(message_id, vote) {
    return this.getMessageDiv(message_id).find(`.msg-vote[data-event-name="${vote}"]`)
  }

  editMessageText(message_id, text) {
    let f = this.formatMessage(text)
    return this.getMessageDiv(message_id).find(".text").html(f);
  }

  showHistoryButton(message_id) {
    this.getMessageDiv(message_id).find(".show-history").show();
  }

  getRoomType(room_id) {
    return $(`.room-link[data-room-id="${room_id}"`).attr("data-room-type");
  }

  getLastMessageBanner(room_id) {
    return this.getMessagesDiv(room_id).find('.date-banner');
  }

  getMessageText(message_id) {
    return this.getMessageDiv(message_id).find(".text").text();
  }

  formatMessage(raw_message) {
    let URL_REGEX = /(http(s){0,1}:\/\/){0,1}[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)/g;
    let matches = raw_message.match(URL_REGEX);
    let formatted = raw_message;
    if (matches != null) {
      for (let match of matches) {
        formatted = raw_message.replace(match, `<a href='${match}'>${match}</a>`);
      }
    }
    return formatted;
  }

  getPreviewDiv(room_id) {
    return $(".image-preview-container[data-room-id='" + room_id +"']")
  }
}
