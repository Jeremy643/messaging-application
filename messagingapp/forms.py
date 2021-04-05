from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import email_validator
from messagingapp.models import User


class RegistrationForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired(), Length(5, 20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken!')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken.')


class LoginForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class NewMessageForm(FlaskForm):

    recipient = StringField('Recipient', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    send = SubmitField('Send')

    def validate_recipient(self, recipient):
        user = User.query.filter_by(username=recipient.data).first()
        if not user:
            raise ValidationError("User doesn't exist!")
        else:
            return True