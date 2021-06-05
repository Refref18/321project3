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
import json

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
            "SELECT * FROM DatabaseManagers U WHERE U.username= %s", (username,))
        row = (mycursor.fetchall())
        if row == []:
            return redirect(url_for('views.error'))
        if row is not []:
            theUser = row[0]
            thePassword = theUser[1]
            if sha256_crypt.verify(request.form.get('password'), thePassword):
                session['logged'] = True
                session['username'] = request.form.get('username')
                flash("Logged in")
                return redirect(url_for('views.manager'))
            else:
                error = "Invalid"
                flash("Invalid")
                # bunların yerine bir error page!!
                return redirect(url_for('views.error'))
    return render_template("manager_login.html",  user=current_user)


@views.route('/user_page')
def user():
    if request.method == 'POST':
        # RABİA KISMIIIIIIII!!!!!!!!!!!
        if request.form.get('action1') == 'View Drug Table':
            pass
        if request.form.get('action2') == 'Drug Interaction Table':
            pass
        if request.form.get('action3') == 'Side Effect Table':
            pass
        if request.form.get('action4') == 'Interaction Proteins Table':
            pass
        if request.form.get('action5') == 'Interaction Drugs Table':
            pass
        if request.form.get('action6') == 'Add Contributor':
            pass
        if request.form.get('action7') == 'Proteins That Bind the same Drug':
            pass
        if request.form.get('action8') == 'Drugs with spesific side effect':
            pass
        if request.form.get('action9') == 'Keyword in Description':
            pass
        if request.form.get('action10') == 'Drugs with least side effects':
            pass
        if request.form.get('action11') == 'DOI of papers and contributors':
            pass
        if request.form.get('action12') == 'Rank Institutes':
            pass
        if request.form.get('action13') == 'Filter interacting targets of a specific drugs':
            pass
    return render_template("user_page.html",  user=current_user)


@views.route('/manager_page', methods=['GET', 'POST'])
def manager():
    if request.method == 'POST':
        # Database managers shall be able to add new users to the system.
        if request.form.get('action1') == 'Add new user':
            try:
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="Greenwich82",
                    database='dtbank'
                )
                mycursor = mydb.cursor(buffered=True)
                name = request.form.get('name')
                username = request.form.get('username')
                institute = request.form.get('institution')
                password = request.form.get('password')
                hash_pass = sha256_crypt.encrypt((password))
                print(name, username, institute, hash_pass)
                mycursor.execute(
                    "INSERT INTO Users(name,username,institution,password) VALUES(%s,%s,%s,%s)", (name, username, institute, hash_pass))
                mydb.commit()
            except Exception:
                print("error")
        # Database managers shall be able to update affinity values of drugs using Reaction IDs
        if request.form.get('action2') == 'Update affinity values':
            try:
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="Greenwich82",
                    database='dtbank'
                )
                mycursor = mydb.cursor(buffered=True)
                reaction_id = request.form.get('reaction_id')
                affinity_value = request.form.get('affinity_value')
                mycursor.execute(
                    "UPDATE Reactions SET affinity_nM = %s WHERE reaction_id =%s ", (affinity_value, reaction_id))
                mydb.commit()
            except Exception:
                print("error")
        if request.form.get('action2.1') == 'Delete Drug':
            try:
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="Greenwich82",
                    database='dtbank'
                )
                mycursor = mydb.cursor(buffered=True)
                drug_id = request.form.get('drug_id')
                mycursor.execute(
                    "DELETE FROM DrugBanks WHERE drugbank_id=%s", (drug_id,))
                mydb.commit()
            except Exception:
                print("error")
        if request.form.get('action3') == 'Delete protein':
            try:
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="Greenwich82",
                    database='dtbank'
                )
                mycursor = mydb.cursor(buffered=True)
                uniprot_id = request.form.get('uniprot_id')
                mycursor.execute(
                    "DELETE FROM UniProts WHERE uniprot_id=%s", (uniprot_id,))
                mydb.commit()
            except Exception:
                print("error")
        if request.form.get('action4.1') == 'Delete Contributor':
            try:
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="Greenwich82",
                    database='dtbank'
                )
                mycursor = mydb.cursor(buffered=True)
                doi = request.form.get('doi')
                author = request.form.get('author1')
                mycursor.execute(
                    "DELETE FROM Wrote WHERE doi=%s and author=%s ", (doi, author))
                mydb.commit()
            except Exception:
                print("error")
        if request.form.get('action4.2') == 'Add Contributor':
            try:
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="Greenwich82",
                    database='dtbank'
                )
                mycursor = mydb.cursor(buffered=True)
                doi = request.form.get('doi1')
                author = request.form.get('author')
                mycursor.execute(
                    "INSERT INTO Wrote(doi,author) VALUES(%s,%s)", (doi, author))
                mydb.commit()
            except Exception:
                print("error")

        if request.form.get('action5') == 'View Tables':
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Greenwich82",
                database='dtbank'
            )
            mycursor = mydb.cursor(buffered=True)
            mycursor.execute(
                "SELECT * FROM DrugBanks")
            #items = mycursor.fetchall()
            columns = [col[0] for col in mycursor.description]
            rows = [dict(zip(columns, row)) for row in mycursor.fetchall()]
            for row in rows:
                row.pop('description', None)
            print(row)
            headers = 'drugbank_id, name'

            return redirect(url_for('views.table', headers=headers, objects=json.dumps(rows)))

    return render_template("manager_page.html",  user=current_user)


@views.route('/error', methods=['GET', 'POST'])
def error():
    if request.method == 'POST':
        return redirect(url_for('views.home'))
    return render_template("error_page.html",  user=current_user)


@views.route('/table/<headers>/<objects>', methods=['GET', 'POST'])
def table(headers=None, objects=None):
    print(objects)
    items = json.loads(objects)
    head = headers.split(',')
    return render_template('table.html',
                           headers=head,
                           objects=items)
