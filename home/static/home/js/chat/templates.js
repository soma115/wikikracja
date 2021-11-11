import { _, formatTime } from './utility.js';

const room_template = `
<div class='room' id='room'>

  <div class='messages'>
    <div class='room-empty-banner empty-chat-message'>
      ${_("This room is empty, be the first one to write something.")}
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

    <div class='image-preview-container' style='display:none'>
      <div class='preview-images'>
      </div>
      <div class='delete-images-preview'>
        <i class='fas fa fa-times'></i>
      </div>
    </div>
  </div>















  <div class='chat-controls fixed-bottom'>

    <div id='c1'>
      <div id='c2'>
        <% if (is_public) { %>
          <input class='anonymous-switch' id="anonymous-switch-id" type='checkbox'
          />
          <label for='anonymous-switch-id'>${_("Anonymous")}</label>
        <% } %>
      </div>
      <div id='c3'>
        <% if (slow_mode_delay) { %>
          <div class='slow-mode-hint' style="display:contents;"></div>
          <span style='display: none;' class="slow-mode-timer">0</span>
        <% } %>
      </div>
    </div>

    <div id='c4'>
      <div id='c5'>
        <!-- Those two have to go one after another for some CSS trickery -->
          <input type='file' id="file-input" style='display:none;' class='file-input' multiple='multiple'/>
          <label class='btn btn-primary chat-control'
            for="file-input">
              <i class="fas fa-image"></i>
          </label>
        <!-- Those two-->
      </div>

      <div class='chat-controls-row id='c6''>
        <input class='message-input' id='c7'>
        <button class='send-message chat-control btn btn-primary id='c8''>
          <i class="fas fa-paper-plane"></i>
        </button>
      </div>
    </div>

  </div>





</div>
`;

const message_template = `
<div class='message <% if (own) { %> own <% } %>' data-message-id=<%-message_id%>>

  <div class='message-content'>

    <div class='message-header'>
      <span class='username'><%=username%></span>
      <div class='message-info'>
        <div class='show-history' <% if (!edited) { %> style='display:none' <% } %>
          data-message-id='<%-message_id%>'> ${_("edited")}
        </div>
        <% if (own) { %>
          <div class='edit-message ml-1' data-message-id="<%-message_id%>" >${_("edit")}</div>
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
        <div class='d-flex d-flex justify-content-end'>
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

  </div>
</div>
`;

const history_template = `
<table class='table' style='border-bottom: 1px solid #dee2e6;'>
<% for (let [i, entry] of Object.entries(history)) { %>
  <tr>
    <td style='width: 0'><%- parseInt(i) + 1 %>.</td>
    <td> <%- entry.text %> </td>
    <td style='text-align: end; font-size: smaller; color: gray;'>
      <%- entry.formattedTime %>
    </td>
  </tr>
<% } %>
</table>
`;

export const Room = ejs.compile(room_template);
export const Message = ejs.compile(message_template);
export const MessageHistory = ejs.compile(history_template);