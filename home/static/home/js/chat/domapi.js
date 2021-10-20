import { removeNotification, formatTime, escapeHtml, getImageSize } from './utility.js';

const room_template = `
  <div class='room' id='room'>

      <div class='messages'>
        <div class='room-empty-banner empty-chat-message'>
          This room is empty, be the first one to write something.
        </div>
      </div>

      <div style='position: relative'>

        <div class='status-container'
             style='display:none!important'>

          <div class='status-message'>
          </div>
          <div class='stop-editing'>
             <i class='fas fa fa-times'></i>
          </div>
        </div>

        <div class='image-preview-container'
               style='display:none'>

          <div class='preview-images'></div>

          <div class='delete-images-preview'>
            <i class='fas fa fa-times'></i>
          </div>

        </div>
      </div>



      <div class='chat-controls' class='d-flex'>

        <div class='chat-controls-row'>
          <input
                 class='message-input col-12 col-sm message-input mr-1'>

          <button
                  class='send-message chat-control btn btn-primary btn-sm'>
                    <i class="fas fa-paper-plane"></i>
          </button>


        </div>

        <!-- Those two have to go one after another for some CSS trickery -->
        <input type='file'
               id="file-input"
               style='display:none;'
               class='file-input'
               multiple='multiple'
        />

        <label class='btn btn-primary ml-1 file-input-label chat-control'
               for="file-input">
               <i class="fas fa-file-image"></i>
        </label>
        <!-- Those two-->

      </div>
      <div class='mt-3'>


      <% if (is_public) { %>

          <input class='anonymous-switch'
                  id="anonymous-switch-id"
                  type='checkbox'
          />
          <label for='anonymous-switch-id'>Anonymous</label>

      <% } %>


      <% if (slow_mode_delay) { %>

          <div class='d-flex justify-content-between'>
            <div class='slow-mode-hint'></div>
            <span
                  style='align-self: center; display: none;'
                  class="slow-mode-timer badge badge-primary badge-pill">0
            </span>
          </div>

      <% } %>

      </div>
  </div>
`;

const message_template = `<div class='message <% if (own) { %> own <% } %>' data-message-id=<%-message_id%>>

    <div class='message-header'>
      <span class='username'><%=username%></span>

      <div class='message-info'>
        <div class='show-history' <% if (!edited) { %> style='display:none' <% } %>
             data-message-id='<%-message_id%>'> edited
        </div>

        <% if (own) { %>
          <div class='edit-message ml-1'>edit</div>
        <% } %>

        <div class='message-timestamp ml-1' data-message-id='<%-message_id%>'><%- latest_ts %></div>

      </div>
    </div>


    <div class='body'>
      <div class='attachment-image-container'>
        <% for (let filename of attachments?.images || []) { %>
          <img class='attached-image' src='/media/uploads/<%-filename %>'>
        <% } %>
      </div>

      <span class='text'><%-message%></span>

    </div>

    <div class='footer'>
      <% if (type == "public") { %>
        <div class='d-flex'>

         <div data-event-name="upvote" data-message-id="<%-message_id%>" class='msg-vote vote-block'>
          <i class="fas fa-check"></i>
          <div class='msg-upvotes'><%-upvotes%></div>
         </div>

         <div data-event-name="downvote" data-message-id="<%-message_id%>" class='msg-vote vote-block'>
          <i class="fas fa-times"></i>
          <div class='msg-downvotes'><%-downvotes%></div>
         </div>

       </div>
      <% } %>

      </div>
  </div>`

const ROOM_TEMPLATE = ejs.compile(room_template);
const MESSAGE_TEMPLATE = ejs.compile(message_template)

export default class DomApi {
  getRoomIcon(room_id) {
    return $(`.room-link[data-room-id="${room_id}"]`);
  }

  createRoomDiv(room_id, title, is_public, slow_mode_delay, notifs_enabled) {
    let roomdiv = $(ROOM_TEMPLATE({room_id, title, is_public, slow_mode_delay, notifs_enabled}));
    $("#chats").empty().append(roomdiv);
    return roomdiv;
  }

  getRoom() {
    return $(`#room`)
  }

  getMessagesDiv() {
    return this.getRoom().find('.messages');
  }

  addMessage(room_id, message_id,
    username, message,
    upvotes, downvotes, vote,
    own, edited,
    attachments,
    original_ts, latest_ts) {

    let type = this.getRoomType(room_id);

    let html = MESSAGE_TEMPLATE({room_id, message_id,
      username,
      message: this.formatMessage(message),
      upvotes, downvotes, vote,
      own, edited,
      attachments,
      original_ts,
      latest_ts: formatTime(latest_ts),
      type,
    });

    this.getMessagesDiv().append(html);

    // make own vote appear active
    this.getVoteDiv(message_id, vote).addClass('active');
  }

  addDateBanner(text) {
    this.getMessagesDiv().append(`<div>${text}</div>`)
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

  getLastMessageBanner() {
    return this.getMessagesDiv().find('.date-banner');
  }

  getMessageText(message_id) {
    return this.getMessageDiv(message_id).find(".text").text();
  }

  formatMessage(raw_message) {
    let escaped = escapeHtml(raw_message);
    let URL_REGEX = /(http(s){0,1}:\/\/){0,1}[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)/g;
    let formatted = escaped;

    let matches = escaped.match(URL_REGEX);
    if (matches != null) {
      for (let match of matches) {
        formatted = raw_message.replace(match, `<a href='${match}'>${match}</a>`);
      }
    }
    return formatted;
  }

  // container for images
  getPreviewDiv() {
    return $(".preview-images")
  }

  // container with all images and close button
  getPreviewContainer() {
    return $(`.image-preview-container`)
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

  getMessageTimeDiv(message_id) {
    return $(`.message-timestamp[data-message-id=${message_id}]`);
  }

  getEnteredText() {
    return $(`.message-input`).val();
  }

  getAnonymousValue() {
    return $(`.anonymous-switch`).is(":checked");
  }

  getFileInput() {
    return $(`#file-input`);
  }

  getFiles() {
    return this.getFileInput()[0].files;
  }

  clearFiles() {
    $(`#file-input`).val("");
    this.getPreviewContainer().hide();
    this.getPreviewDiv().empty();
  }

  getEditedMessageId() {
    return this.getMessageInput().data('edit-message');
  }

  getStatusMessageDiv(){
    return $(`.status-message`);
  }

  getStatusMessageContainer(){
    return $(`.status-container`);
  }

  getMessageInput() {
    return $(`.message-input`);
  }

  setEditing(message_id) {
    let text = this.getMessageText(message_id);
    this.getStatusMessageContainer().show();
    this.getStatusMessageDiv().text(`editing ${text}`);
    this.getFileInput().attr('disabled', 'disabled');
    this.getMessageInput().data('edit-message', message_id)
    .val(text);
  }

  stopEditing() {
    this.getStatusMessageContainer().hide();
    this.getFileInput().removeAttr('disabled');
    this.getMessageInput().removeData('edit-message');
      this.getMessageInput().val("")
  }

  async openBigImage(srcs) {
    var pswpElement = document.querySelectorAll('.pswp')[0];
    let items = [];
    for (let src of srcs) {

      let size = await getImageSize(src);

      items.push({
        src,
        w: size.w,
        h: size.h
      })
    }

    var options = {
        index: 0, // start at first slide
        closeOnScroll: false,
    };

    var gallery = new PhotoSwipe( pswpElement, PhotoSwipeUI_Default, items, options);
    gallery.init();
  }

  closeBigImage() {
    $("#big-image").remove();
    $('body').removeClass('modal-open');
  }

  setSlowMode(delay) {
    if (delay == 0) return;
    $(`.slow-mode-hint`).html(`⚠ slow mode is active. you can send messages once in ${delay} seconds.`)
  }

  setSlowModeTimeLeft(seconds) {
    if (seconds == 0) {
      $('.slow-mode-timer').hide();
      return;
    }
    $('.slow-mode-timer').show().text(""+seconds);
  }

  getLatestOwnMessage() {
    return this.getMessagesDiv().find('.message.own').last();
  }

  isEditing() {
    return this.getEditedMessageId() ? true : false;
  }

  removeNoMessagesBanner() {
    $('.room-empty-banner').remove();
  }

  setRoomTitle(title) {
    $("#room-title").text(title);
  }

  setRoomNotifications(room_id, is_enabled) {
    $(".notif-switch[data-room-id='"+room_id+"']").prop("disabled", false).prop('checked', is_enabled);
  }

  clearRoomData() {
      this.getMessagesDiv().empty();
      this.getMessageInput().val("");
      this.clearFiles();
      this.stopEditing();
      this.getMessagesDiv().append(
        "<p class='empty-chat-message'>Select a chat to start messaging.</p>"
      );
  }

  showHistoryModal(title, body) {
    let modal = $("#message-history-modal").modal('show');
    modal.find(".modal-body").html(body)
    modal.find(".modal-title").html(title);
  }

  showNotificationPermModal(title, body) {
    let modal = $("#message-permission-modal").modal('show');
    modal.find(".modal-body").html(body)
    modal.find(".modal-title").html(title);
  }

  addPermissionBanner() {
    $('.room-header').append("<button class='permission-banner btn btn-success'> <i class='far fa-bell'></i> Manage notifications </button>")
  }
}
