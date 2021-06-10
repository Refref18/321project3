from flask import Blueprint
from .models import User
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

views = Blueprint('views', __name__)


@views.route('')
def hello():
    return "<h2>im asdfsfds cat</h2>"


@views.route('home')
def home():
    return "<h2>im cat</h2>"


@views.route('/user_login')
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        institute = request.form.get('institute')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.user'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('User does not exist.', category='error')
    return render_template("user_login.html", user=current_user)


@views.route('/manager_login')
def login_m():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.manager'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('User does not exist.', category='error')
    return render_template("manager_login.html", user=current_user)


@views.route('/user_page')
def user():
    return "user page"


@views.route('/manager_page')
def manager():
    return "manager page"
