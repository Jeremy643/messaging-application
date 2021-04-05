from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from .constants import INFO
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://postgres:{os.environ.get('DB_PASSWORD')}@localhost:5432/messaging_app"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'home.login'
login_manager.login_message_category = INFO
socketio = SocketIO(app)

from .views import home, messenger
app.register_blueprint(home.home, url_prefix="")
app.register_blueprint(messenger.messenger, url_prefix="/messenger/")