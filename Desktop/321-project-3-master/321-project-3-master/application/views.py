from flask import Blueprint
from .database import mysql
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, flash, redirect, url_for
import os
from flask import Flask, render_template, flash, request, url_for, redirect, session
from passlib.hash import sha256_crypt
from flask import Blueprint
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user


views = Blueprint('views', __name__)


@views.route('', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form.get('action1') == 'Login as User':
            return redirect(url_for('views.login'))
        elif request.form.get('action2') == 'Login as Manager':
            return redirect(url_for('views.login_m'))
    return render_template("home.html")


@views.route('/user_login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username')
        institute = request.form.get('institution')
        password = request.form.get('password')
        mydb = mysql.connector.connect(
            user='root', password='Greenwich82', host='localhost', database='dtbank')
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute(
            "SELECT * FROM Users U WHERE U.username=%s and U.institution= %s", (username, institute))
        row = (mycursor.fetchall())
        if row == []:
            return redirect(url_for('views.error'))
        if row is not []:
            theUser = row[0]
            thePassword = theUser[3]

            if sha256_crypt.verify(request.form.get('password'), thePassword):
                session['logged'] = True
                session['username'] = request.form.get('username')
                session['institute'] = request.form.get('institute')
                flash("Logged in")
                return redirect(url_for('views.user'))
            else:
                error = "Invalid"
                flash("Invalid")
                return redirect(url_for('views.error'))

    return render_template("user_login.html",  user=current_user)


@views.route('/manager_login', methods=['GET', 'POST'])
def login_m():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username')
        mydb = mysql.connector.connect(
            user='root', password='Greenwich82', host='localhost', database='dtbank')
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute(
            "SELECT * FROM DatabaseManagers M WHERE M.username=%s", username)  # BURDA HATA VERİYORRRRRRRRRR
        row = (mycursor.fetchall())
        print(row)
        if row == []:
            return redirect(url_for('views.error'))
        if row is not []:
            theUser = row[0]
            thePassword = theUser[1]
            if sha256_crypt.verify(request.form.get('password'), thePassword):
                session2['logged'] = True
                session2['username'] = request.form.get('username')
                flash("Logged in")
                return redirect(url_for('views.user'))
            else:
                error = "Invalid"
                flash("Invalid")
                # bunların yerine bir error page!!
                return redirect(url_for('views.error'))

    return render_template("manager_login.html",  user=current_user)


@views.route('/user_page')
def user():
    return render_template("user_page.html",  user=current_user)


@views.route('/manager_page')
def manager():
    return "manager page"


@views.route('/error', methods=['GET', 'POST'])
def error():
    if request.method == 'POST':
        return redirect(url_for('views.home'))

    return render_template("error_page.html",  user=current_user)
