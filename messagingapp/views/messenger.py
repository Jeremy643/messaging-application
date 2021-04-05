from flask import render_template, Blueprint, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_socketio import join_room, leave_room
from messagingapp import db, socketio
from messagingapp.forms import NewMessageForm
from messagingapp.models import User, Conversation, Message
from messagingapp.constants import INFO
from datetime import datetime
from sqlalchemy import or_

messenger = Blueprint('messenger', __name__, static_folder='static', template_folder='template')


@messenger.route('/conversations/', methods=["POST", "GET"])
@login_required
def conversations():
    form = NewMessageForm()
    if form.validate_on_submit():
        recipient = User.query.filter_by(username=form.recipient.data).first()

        # check if current user already has a conversation with the recipient
        conv = current_user.conversations.intersection(recipient.conversations)
        if not conv:
            # doesn't exist - create one
            conv = Conversation.create(users=[current_user, recipient])
        else:
            conv = conv.pop()
        Message.create(message=form.message.data, date_sent=datetime.utcnow(), sender_id=current_user.id, recipient_id=recipient.id, conversation_id=conv.id)

        return redirect(url_for('messenger.conversation', conv_id=conv.id))
    
    conv = list(current_user.conversations)
    conv.sort(reverse=True, key=lambda c: c.messages[-1].date_sent)
    context = {'time_now': datetime.utcnow(), 'conversations': conv}

    return render_template('messenger/conversation-list.html', form=form, context=context)

@messenger.route('/conversation/<conv_id>/', methods=["POST", "GET"])
@login_required
def conversation(conv_id):
    conv = Conversation.query.filter_by(id=conv_id).first()

    # limit access to users in the conversation
    if current_user not in conv.users:
        flash("That's not your conversation!", category=INFO)
        return redirect(url_for('messenger.conversations'))
    
    context = {'messages': conv.messages, 'from': conv.get_recipient(current_user.id)[0].username}
    return render_template('messenger/conversation.html', context=context)

@socketio.on('connect_user', namespace='/messenger/conversation')
def handle_connection(conv_id):
    print(f'USER CONNECTED')
    join_room(conv_id)

# @socketio.on('disconnect', namespace='/messenger/conversation')
# def handle_disconnection():
#     print(f'USER DISCONNECTED')
#     # user_sessions.pop(current_user.id)
#     # print(user_sessions)
#     leave_room(current_user.id)

@socketio.on('user send message', namespace='/messenger/conversation')
def handle_messages(data):
    msg = data.get('msg')
    conv_id = data.get('id')
    print(f'MESSAGE RECEIVED in conversation {conv_id}\nFROM {current_user.username}: {msg}')

    conv = Conversation.query.filter_by(id=conv_id).first()
    sender_id = current_user.id
    recipient = conv.get_recipient(sender_id)[0]

    # pass data to form and validate
    # form = NewMessageForm()
    # form.message.data = msg
    # form.recipient.data = recipient.username

    # print(form.validate())
    # if form.validate():
    #     # the data entered is valid - create and save the new message
    #     message = Message.create(message=msg, date_sent=datetime.utcnow(), sender_id=sender_id, recipient_id=recipient.id, conversation_id=conv.id)
    #     message_json = jsonify(message.to_dict())
    #     print(message_json.id, message_json.message)
    # else:
    #     print(form.message.errors)
    #     print(form.recipient.errors)
    #     print(form.send.errors)

    message = Message.create(message=msg, date_sent=datetime.utcnow(), sender_id=sender_id, recipient_id=recipient.id, conversation_id=conv.id)

    data = {'msg': msg, 'date_sent': str(message.date_sent.strftime('%X %x')), 'from': current_user.username}
    socketio.emit('user receive message', data, room=conv_id, namespace='/messenger/conversation', include_self=False)