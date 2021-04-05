from messagingapp import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

conversations = db.Table('conversations',
            db.Column('conversation_id', db.Integer, db.ForeignKey('conversation.id'), primary_key=True),
            db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True))


class BaseMixin(object):
    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()
        return obj


class User(db.Model, UserMixin, BaseMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    conversations = db.relationship('Conversation', secondary=conversations, back_populates='users', lazy='subquery', collection_class=set)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __str__(self):
        return self.email
    
    def __repr__(self):
        return f"{type(self).__name__}({self.username}, {self.email})"


class Conversation(db.Model, BaseMixin):

    id = db.Column(db.Integer, primary_key=True)
    users = db.relationship('User', secondary=conversations, back_populates='conversations', collection_class=set)
    messages = db.relationship('Message', backref='conversation', lazy=True)

    def __init__(self, users, messages=[]):
        self.users = self.users.union(set(users))
        self.messages.extend(list(messages))

    def __repr__(self):
        return f'{type(self).__name__}({self.users})'
    
    def get_recipient(self, sender_id):
        """ Return the user that receives the message from a user given that sender's id. """
        recipients = [user for user in self.users if user.id != sender_id]
        return recipients


class Message(db.Model, BaseMixin):

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)

    def __init__(self, message, date_sent, sender_id, recipient_id, conversation_id):
        self.message = message
        self.date_sent = date_sent
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.conversation_id = conversation_id

    def __repr__(self):
        return f'{type(self).__name__}({self.date_sent})'
    
    def to_dict(self) -> dict:
        """
        Generates a dictionary representation of the Message object, valid for flask.jsonify.
        Returns:
            Dictionary representation of the Message object.
        """

        return {
            'id':                   self.id,
            'message':              self.message,
            'date_sent':            self.date_sent,
            'sender_id':            self.sender_id,
            'recipient_id':         self.recipient_id,
            'conversation_id':      self.conversation_id
        }