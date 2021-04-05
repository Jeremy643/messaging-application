$(document).ready(function(){
    var socket = io.connect('http://127.0.0.1:5000/messenger/conversation');
    var conv_id = getConversationID();

    updateScroll();

    function updateScroll() {
        var display = document.getElementById('message-display');
        display.scrollTop = display.scrollHeight;
    };

    function getConversationID() {
        var linkItems = window.location.href.split('/');
        var index = linkItems.indexOf('conversation');
        index += 1;  // add 1 because the conversation id will always come after 'conversation'

        return linkItems[index];
    }
    
    socket.emit('connect_user', conv_id);

    $('#submitMessage').click(function() {
        var msg = $('#messageInput').val();
        if (msg !== '') {
            var data = {'msg': msg, 'id': conv_id};
            socket.emit('user send message', data);
        }
    });

    socket.on('user receive message', function(data) {
        console.log(`${data['from']}> ${data['msg']}`);
        var template = $('#newMessageDisplay');
        var node = template.prop('content');
        var from = $(node).find('#fromTemplate');
        from.text(data['from']);
        var dateSent = $(node).find('#dateSentTemplate');
        dateSent.text(data['date_sent']);
        var message = $(node).find('#messageTemplate');
        message.text(data['msg']);
        $('#message-display').append(template.html());
        updateScroll();
    });
});