from flask import render_template, url_for, Blueprint, redirect, request, flash
from flask_login import login_user, current_user, logout_user, login_required
from messagingapp.models import User
from messagingapp.constants import SUCCESS, ERROR
from messagingapp.forms import RegistrationForm, LoginForm
from messagingapp import db, bcrypt

home = Blueprint(name="home", import_name=__name__)

@home.route("/")
@home.route("/home/")
def index():
    return render_template("home/index.html")

@home.route("/register/", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        User.create(username=form.username.data, email=form.email.data, password=hashed_password)

        flash('Your account has been created! You can now login.', category=SUCCESS)
        return redirect(url_for('home.login'))

    return render_template('home/register.html', form=form)

@home.route("/login/", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Login successful!', category=SUCCESS)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home.index'))
        else:
            flash('Login unsuccessful! Check your email and/or password.', category=ERROR)

    return render_template("home/login.html", form=form)

@home.route("/logout/")
def logout():
    logout_user()
    flash('Logout successful!', category=SUCCESS)
    return redirect(url_for('home.login'))

@home.route("/account/")
@login_required
def account():
    return render_template('home/account.html')