import { removeNotification, formatTime } from './utility.js';
export default class DomApi {
  getRoomIcon(room_id) {
    return $(`.room-link[data-room-id="${room_id}"]`);
  }

  createRoomDiv(room_id, title, is_public, notifs_enabled) {
    let roomdiv = $(
        `<div class='room' data-room-id='${room_id}' id='room-${room_id}'>

            <div class='d-flex justify-content-between p-3 header'>
              <h5>${title}</h5>
              <div>
                <input type='checkbox'
                       class='notifications-switch'
                       id='notif-switch-${room_id}'
                       ${notifs_enabled ? 'checked="checked"': ''}
                       data-room-id='${room_id}'
                />
                <label for='notif-switch-${room_id}'> Notifications </label>
              </div>
            </div>

            <div class='messages'></div>

            <div style='position: relative'>

              <div class='status-container'
                   data-room-id="${room_id}"
                   style='display:none!important'>

                <div class='status-message'
                     data-room-id='${room_id}'>
                </div>
                <div class='stop-editing' data-room-id='${room_id}'>
                   <i class='fas fa fa-times'></i>
                </div>
              </div>

              <div class='image-preview-container'
                     data-room-id="${room_id}"
                     style='display:none'>

                <div class='preview-images' data-room-id='${room_id}'></div>

                <div class='delete-images-preview' data-room-id='${room_id}'>
                  <i class='fas fa fa-times'></i>
                </div>

              </div>
            </div>



            <div class='chat-controls' class='d-flex'>

              <div class='chat-controls-row'>
                <input data-room-id='${room_id}'
                       class='message-input col-12 col-sm message-input mr-1'>

                <input type='file'
                       id="file-input-${room_id}"
                       style='display:none;'
                       class='file-input'
                       data-room-id='${room_id}' multiple='multiple'
                />

                <label class='btn btn-primary mr-1 chat-control'
                       for="file-input-${room_id}">
                       <i class="fas fa-file-image"></i>
                </label>

              </div>

              <button data-room-id='${room_id}'
                      class='send-message chat-control btn btn-danger btn-sm'>
                        <i class="fas fa-paper-plane"></i>
              </button>

            </div>
            <div class='mt-3'>
              ${is_public ?
                `<input class='anonymous-switch'
                        data-room-id="${room_id}"
                        id="anonymous-switch-id-${room_id}"
                        type='checkbox'
                />
                <label for='anonymous-switch-id-${room_id}'>Anonymous</label>`
              : ""}
            </div>
        </div>`
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

  addMessage(room_id, message_id,
    username, message,
    upvotes, downvotes, vote,
    own, edited,
    attachments,
    original_ts, latest_ts) {
    let type = this.getRoomType(room_id);

    let attachments_html = "<div class='attachment-image-container'>";

    for (let filename of attachments?.images || []) {
      attachments_html += `<img class='attached-image' src='/media/uploads/${filename}'>`
    }
    attachments_html += "</div>"

    let ok_msg = `
    <div class='message ${own ? "own": ""}' data-message-id=${message_id}>

      <div class='header'>
        <span class='username'>${username}</span>

        <div class='message-info'>
          <div class='show-history' ${edited ? "" : "style='display:none'"} data-message-id='${message_id}'>edited</div>
          <div class='message-timestamp ml-1' data-message-id='${message_id}'>${formatTime(latest_ts)}</div>
          ${(own ?
            `<div class='edit-message ml-1'
                  data-message-id='${message_id}'
                  data-room-id='${room_id}'>edit</div>`
          : "")}
        </div>
      </div>


      <div class='body'>
        ${attachments_html}

        <!-- it appears newlines and spaces are prererved, so no nice indents for message here -->
        <span class='text'>${this.formatMessage(message)}</span>
        
      </div>

      <div class='footer'>
        ${(type == "public" ?
        `
          <div class='d-flex'>
           <div data-event-name="upvote" data-message-id="${message_id}" class='msg-vote vote-block'>
            <i class="fas fa-check"></i>
            <div class='msg-upvotes'>${upvotes}</div>
           </div>

           <div data-event-name="downvote" data-message-id="${message_id}" class='msg-vote vote-block'>
            <i class="fas fa-times"></i>
            <div class='msg-downvotes'>${downvotes}</div>
          </div>
        </div>
        ` : "")}
      </div>
    </div>`;
    this.getMessagesDiv(room_id).append(ok_msg);

    // make own vote appear active
    this.getVoteDiv(message_id, vote).addClass('active');
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

  editMessageText(message_id, text, ts) {
    let f = this.formatMessage(text)
    let time = formatTime(ts);
    this.getMessageTimeDiv(message_id).text(time);
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

  // container for images
  getPreviewDiv(room_id) {
    return $(".preview-images[data-room-id='" + room_id +"']")
  }

  // container with all images and close button
  getPreviewContainer(room_id) {
    return $(`.image-preview-container[data-room-id="${room_id}"]`)
  }

  seenChat(room_id) {
    let room_icon = this.getRoomIcon(room_id);
    room_icon.removeClass("room-not-seen");

    // all rooms are seen, change tab icon back
    if ($('.room-not-seen').length == 0) {
      removeNotification();
    }
  }

  updateOnline(room_id, is_online) {
    let room_icon = this.getRoomIcon(room_id);
    if (is_online) {
      room_icon.removeClass('offline').addClass('online');
    } else {
      room_icon.removeClass('online').addClass('offline');
    }
  }
  setRoomNotifs(room_id, enabled) {
    $(`.notifications-switch[data-room-id='${room_id}']`).prop('checked', enabled);
  }

  getMessageTimeDiv(message_id) {
    return $(`.message-timestamp[data-message-id=${message_id}]`);
  }

  getEnteredText(room_id) {
    return $(`.message-input[data-room-id='${room_id}']`).val();
  }

  getAnonymousValue(room_id) {
    return $(`.anonymous-switch[data-room-id="${room_id}"]`).is(":checked");
  }

  getFileInput(room_id) {
    return $(`#file-input-${room_id}`);
  }

  getFiles(room_id) {
    return this.getFileInput(room_id)[0].files;
  }

  clearFiles(room_id) {
    $(`#file-input-${room_id}`).val("");
    this.getPreviewContainer(room_id).hide();
    this.getPreviewDiv(room_id).empty();
  }

  getEditedMessageId(room_id) {
    return this.getMessageInput(room_id).data('edit-message');
  }

  getStatusMessageDiv(room_id){
    return $(`.status-message[data-room-id="${room_id}"`);
  }

  getStatusMessageContainer(room_id){
    return $(`.status-container[data-room-id="${room_id}"`);
  }

  getMessageInput(room_id) {
    return $(`.message-input[data-room-id='${room_id}']`);
  }

  setEditing(room_id, message_id) {
    let text = this.getMessageText(message_id);
    this.getStatusMessageContainer(room_id).show();
    this.getStatusMessageDiv(room_id).text(`editing ${text}`);
    this.getFileInput(room_id).attr('disabled', 'disabled');
    this.getMessageInput(room_id).data('edit-message', message_id)
    .val(text);
    console.log(text);
  }

  stopEditing(room_id) {
    this.getStatusMessageContainer(room_id).hide();
    this.getFileInput(room_id).removeAttr('disabled');
    this.getMessageInput(room_id).removeData('edit-message');
      this.getMessageInput(room_id).val("")
    console.log(this.getMessageInput(room_id));
  }
}
