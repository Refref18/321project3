from flask import Blueprint
from flask.wrappers import Response
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

from flask import jsonify

import json
import pandas as pd

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


@views.route('/user_page', methods=['GET', 'POST'])
def user():

    if request.method == 'POST':

        mydb = mysql.connector.connect(
            user='root', password='Greenwich82', host='localhost', database='dtbank')
        mycursor = mydb.cursor(buffered=True)

        if request.form.get('action1') == 'View Drug Table':
            mycursor.execute(
                "SELECT * FROM DrugBanks")
            # items = mycursor.fetchall()
            columns = [col[0] for col in mycursor.description]
            rows = [dict(zip(columns, row)) for row in mycursor.fetchall()]
            for row in rows:
                mycursor.execute(
                    "SELECT R.smiles FROM Reactions R WHERE R.drugbank_id=%s ", (row['drugbank_id'],))
                smiles = mycursor.fetchall()
                if smiles != []:
                    # smiles is added to the dictionary
                    row['smiles'] = smiles[0]
                else:
                    row['smiles'] = ""
                mycursor.execute(
                    "SELECT R.target_name FROM Reactions R WHERE R.drugbank_id=%s ", (row['drugbank_id'],))
                target = mycursor.fetchall()
                if target != []:
                    # target name is added to dictionary
                    row['target_names'] = target
                else:
                    row['target_names'] = ""
                mycursor.execute(
                    "SELECT S.side_effect_name FROM Siders S, HasSideEffect H WHERE H.umls_cui=S.umls_cui and H.drugbank_id=%s ", (row['drugbank_id'],))
                side_effect = mycursor.fetchall()
                if side_effect != []:
                    # target name is added to dictionary
                    row['side_effect_names'] = side_effect
                else:
                    row['side_effect_names'] = ""

            print(rows)
            rowdict = {}
            for row in rows:
                rowdict[row['drugbank_id']] = row
            headers = 'drugbank_id, drug_name,smiles,description,target_names,side_effect_names'

            df = pd.DataFrame(rowdict)
            df.to_html('application/templates/table.html')
            return redirect(url_for('views.table2'))
            # redirect(url_for('views.table', headers=headers, objects=json.dumps(rows)))

        if request.form.get('action2') == 'Drug Interaction Table':
            drugbank_id = request.form.get('drugbank_id')
            mycursor.execute(
                "SELECT * FROM dtbank.drugbanks WHERE drugbank_id = %s", (drugbank_id,))
            if mycursor.fetchall() == []:
                return render_template('error.html', error='Drugbank ID Not Found')

            mycursor.execute(
                "SELECT I.drugbank_id_2, D2.name FROM InteractsWith I , Drugbanks D, Drugbanks D2 WHERE I.drugbank_id_1=D.drugbank_id and I.drugbank_id_2=D2.drugbank_id and D.drugbank_id=%s ", (drugbank_id,))
            columns = [col[0] for col in mycursor.description]
            rows = [dict(zip(columns, row)) for row in mycursor.fetchall()]
            print(rows)
            rowdict = {}
            for row in rows:
                rowdict[row['drugbank_id_2']] = row
            # input: drugbank_id
            # output: interacted drugbank_id's and names of them
            return rowdict

        if request.form.get('action3') == 'Side Effect Table':
            drugbank_id = request.form.get('drugbank_id2')
            mycursor.execute(
                "SELECT * FROM dtbank.drugbanks WHERE drugbank_id = %s", (drugbank_id,))
            if mycursor.fetchall() == []:
                return render_template('error.html', error='Drugbank ID Not Found')

            mycursor.execute(
                "SELECT S.side_effect_name,S.umls_cui FROM Siders S, HasSideEffect H WHERE H.umls_cui=S.umls_cui and H.drugbank_id=%s ", (drugbank_id,))
            columns = [col[0] for col in mycursor.description]
            rows = [dict(zip(columns, row)) for row in mycursor.fetchall()]
            print(rows)
            rowdict = {}
            for row in rows:
                rowdict[row['umls_cui']] = row
            # input: drugbank_id
            # output: side effects and names of them
            return rowdict

        if request.form.get('action4') == 'Interaction Proteins Table':
            drugbank_id = request.form.get('drugbank_id3')
            mycursor.execute(
                "SELECT * FROM dtbank.drugbanks WHERE drugbank_id = %s", (drugbank_id,))
            if mycursor.fetchall() == []:
                return render_template('error.html', error='Drugbank ID Not Found')

            mycursor = mydb.cursor(buffered=True)
            mycursor.execute(
                "SELECT R.uniprot_id, R.target_name FROM Reactions R WHERE R.drugbank_id=%s ", (drugbank_id,))
            columns = [col[0] for col in mycursor.description]
            rows = [dict(zip(columns, row)) for row in mycursor.fetchall()]
            print(rows)
            rowdict = {}
            for row in rows:
                rowdict[row['uniprot_id']] = row
            # input: drugbank_id
            # output: uniprot_ids and their names
            return rowdict

        if request.form.get('action5') == 'Find Interacting Drugs':
            # input -> uniprot_id   output -> 'drugbank_id','drugbank_name'
            uniprot_id = request.form.get('uniprot_id')
            mycursor.execute(
                "SELECT * FROM dtbank.uniprots WHERE uniprot_id = %s", (uniprot_id,))
            if mycursor.fetchall() == []:
                return render_template('error.html', error='Uniprot ID Not Found')

            mycursor.execute(
                ("SELECT D.drugbank_id, D.name FROM dtbank.reactions R, dtbank.drugbanks D "
                 "WHERE uniprot_id = %s AND R.drugbank_id = D.drugbank_id"), (uniprot_id,))

            result = dbResultsToHtml(mycursor)
            if result == 'No Result Found':
                return render_template('error.html', error='No Results Found')

            return redirect(url_for('views.table2'))

        if request.form.get('action6') == 'Drugs That Effect Same Protein':
            # input ->    output -> 'uniprot_id','drugbank_ids'
            mycursor.execute(
                (" SELECT uniprot_id, GROUP_CONCAT(DISTINCT drugbank_id SEPARATOR ', ') AS drugbank_ids "
                 "FROM dtbank.reactions R GROUP BY uniprot_id "
                 "UNION "
                 "SELECT U.uniprot_id, '' FROM dtbank.uniprots U "
                 "WHERE U.uniprot_id NOT IN (SELECT uniprot_id FROM dtbank.reactions R)"))
            dbResultsToHtml(mycursor)
            return redirect(url_for('views.table2'))

        if request.form.get('action7') == 'Proteins That Bind the same Drug':
            # input ->    output -> 'drugbank_id', 'uniprot_ids'
            mycursor.execute(
                (" SELECT drugbank_id, GROUP_CONCAT(DISTINCT uniprot_id SEPARATOR ', ') AS uniprot_ids "
                 "FROM dtbank.reactions R GROUP BY drugbank_id "
                 "UNION "
                 "SELECT D.drugbank_id, '' FROM dtbank.drugbanks D "
                 "WHERE D.drugbank_id NOT IN (SELECT drugbank_id FROM dtbank.reactions R)"))
            dbResultsToHtml(mycursor)
            return redirect(url_for('views.table2'))

        if request.form.get('action8') == 'Drugs with spesific side effect':
            # input -> umls_cui  output -> 'drugbank_id','drug_name'
            umls_cui = request.form.get('umls_cui')  # 'C0002792'

            mycursor.execute(
                "SELECT * FROM dtbank.siders WHERE umls_cui = %s", (umls_cui,))
            if mycursor.fetchall() == []:
                return render_template('error.html', error='Umls Cui Not Found')

            mycursor.execute(
                (" SELECT D.drugbank_id, D.name FROM dtbank.hassideeffect H, dtbank.drugbanks D "
                 "WHERE H.umls_cui = %s AND H.drugbank_id = D.drugbank_id"), (umls_cui,))

            result = dbResultsToHtml(mycursor)
            if result == 'No Result Found':
                return render_template('error.html', error='No Results Found')

            return redirect(url_for('views.table2'))

        if request.form.get('action9') == 'Search Keyword in Description':
            # input -> keyword  output -> 'drugbank_id','drug_name','description'
            keyword = request.form.get('keyword')
            mycursor.execute(
                " SELECT * FROM dtbank.drugbanks WHERE description LIKE %s", (('%' + keyword + '%'),))

            result = dbResultsToHtml(mycursor)
            if result == 'No Result Found':
                return render_template('error.html', error='No Results Found')

            return redirect(url_for('views.table2'))

        if request.form.get('action10') == 'Drugs with least side effects':
            # input -> uniprot_id  output -> drugbank_id,drug_name
            uniprot_id = request.form.get('uniprot_id_2')
            mycursor.execute(
                "SELECT * FROM dtbank.uniprots WHERE uniprot_id = %s", (uniprot_id,))
            if mycursor.fetchall() == []:
                return render_template('error.html', error='Uniprot ID Not Found')

            mycursor.execute(("SELECT    D.drugbank_id, D.name AS drugname "
                              "FROM 	dtbank.reactions R, dtbank.hassideeffect H, dtbank.drugbanks D "
                              "WHERE  R.uniprot_id = %s AND R.drugbank_id = H.drugbank_id AND H.drugbank_id = D.drugbank_id "
                              "GROUP BY D.drugbank_id "
                              "HAVING   COUNT(*) =  (SELECT MIN(Temp.numOfsideeffects) "
                              "FROM (SELECT R.drugbank_id, COUNT(*) numOfsideeffects "
                              "FROM dtbank.reactions R, dtbank.hassideeffect H "
                              "WHERE R.uniprot_id = %s AND R.drugbank_id = H.drugbank_id "
                              "GROUP BY drugbank_id) Temp)"), (uniprot_id, uniprot_id))

            result = dbResultsToHtml(mycursor)
            if result == 'No Result Found':
                return render_template('error.html', error='No Results Found')

            return redirect(url_for('views.table2'))

        if request.form.get('action11') == 'DOI of papers and contributors':
            # input ->      output -> doi, contributors
            mycursor.execute(
                " SELECT W.doi, GROUP_CONCAT(author SEPARATOR '; ') AS contributors FROM dtbank.wrote W GROUP BY W.doi")
            dbResultsToHtml(mycursor)
            return redirect(url_for('views.table2'))

        if request.form.get('action12') == 'Rank Institutes':
            mycursor.execute(
                " SELECT * FROM dtbank.institutions ORDER BY score DESC")
            dbResultsToHtml(mycursor)
            return redirect(url_for('views.table2'))

        if request.form.get('action13') == 'Filter interacting targets of a specific drugs':
            # input -> drugbank_id, 'measurement_type', 'affinity_min', 'affinity_max'
            # output -> 'uniprot_id','target_name'
            drugbank_id = request.form.get('drugbank_id_4')
            mycursor.execute(
                "SELECT * FROM dtbank.drugbanks WHERE drugbank_id = %s", (drugbank_id,))
            if mycursor.fetchall() == []:
                return render_template('error.html', error='Drugbank ID Not Found')
            measurement_type = request.form.get('measurement_type')
            affinity_min = request.form.get('affinity_min')
            if affinity_min == '':
                return render_template('error.html', error='Enter Affinity Min')
            affinity_max = request.form.get('affinity_max')
            if affinity_min == '':
                return render_template('error.html', error='Enter Affinity Max')
            mycursor.execute(
                (" CALL FilterTargets(%s, %s, %s, %s)"), (drugbank_id, measurement_type, affinity_min, affinity_max))

            result = dbResultsToHtml(mycursor)
            if result == 'No Result Found':
                return render_template('error.html', error='No Results Found')

            return redirect(url_for('views.table2'))

    return render_template("user_page.html",  user=current_user)


@views.route('/manager_page', methods=['GET', 'POST'])
def manager():
    if request.method == 'POST':
        # Database managers shall be able to add new users to the system.
        if request.form.get('action1') == 'Add new user':
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
            try:
                mycursor.execute(
                    "INSERT INTO dtbank.users(name,username,institution,password) VALUES(%s,%s,%s,%s)", (name, username, institute, hash_pass))
                mydb.commit()
            except Exception:
                return render_template('error.html', error="Couldn't add the User")
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
                return render_template('error.html', error="Couldn't update the affinity value")
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
                    "SELECT * FROM DrugBanks WHERE drugbank_id=%s", (drug_id,)
                )
                k = mycursor.fetchall()
                if(k == []):
                    return render_template('error.html', error="No such Drug!")
                mycursor.execute(
                    "DELETE FROM DrugBanks WHERE drugbank_id=%s", (drug_id,))
                mydb.commit()
            except Exception:
                return render_template('error.html', error="No such Drug!")
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
                    "SELECT * FROM UniProts WHERE uniprot_id=%s", (uniprot_id,)
                )
                k = mycursor.fetchall()
                if(k == []):
                    return render_template('error.html', error="No such Protein!")
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
                username = request.form.get('username3')
                ins = request.form.get('ins3')
                author = request.form.get('author1')
                print(author, username, ins)
                mycursor.execute(
                    "SELECT Users.username, Users.institution FROM Users WHERE name=%s", (
                        author, )
                )
                k = mycursor.fetchall()
                print(k)
                if(k != [] and k[0][0] == username and k[0][1] == ins):
                    mycursor.execute(
                        "DELETE FROM Wrote WHERE doi=%s and author=%s ", (doi, author))
                    mydb.commit()
                else:
                    return render_template('error.html', error="No such User!")

            except Exception:
                print("error")
        if request.form.get('action4.2') == 'Add Contributor':

            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Greenwich82",
                database='dtbank'
            )
            mycursor = mydb.cursor(buffered=True)
            doi = request.form.get('doi1')
            author = request.form.get('author')
            username = request.form.get('username4')
            ins = request.form.get('ins4')

            mycursor.execute(
                "SELECT Users.username, Users.institution ,Users.name FROM Users WHERE name=%s", (
                    author, )
            )
            k = mycursor.fetchall()
            # if user already exists:
            if(k != [] and k[0][0] == username and k[0][1] == ins and k[0][2] == author):
                pass
            elif(k != [] and k[0][0] == username and k[0][1] == ins and k[0][2] != author):
                # illegal user we cannot add
                return render_template('error.html', error="No such User can exist!")
            else:
                try:
                    hash_pass = sha256_crypt.encrypt(("1234"))
                    mycursor.execute(
                        "INSERT INTO dtbank.users(name,username,institution,password) VALUES(%s,%s,%s,%s)", (author, username, ins, hash_pass))
                    mydb.commit()
                except Exception:
                    return render_template('error.html', error="Couldn't add the User")
            try:
                mycursor.execute(
                    "SELECT * FROM Wrote WHERE doi= %s", (doi,)
                )
                m = mycursor.fetchall()
                print(m)
                if(m != []):
                    mycursor.execute(
                        "INSERT INTO Wrote(doi,author) VALUES(%s,%s)", (doi, author))
                    mydb.commit()
                else:
                    return render_template('error.html', error="No such DOI")

            except Exception:
                print(doi, author)
                print("error")

        if request.form.get('action5') == 'View All Drugs':
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Greenwich82",
                database='dtbank'
            )
            mycursor = mydb.cursor(buffered=True)
            mycursor.execute(
                "SELECT * FROM DrugBanks")
            # items = mycursor.fetchall()
            columns = [col[0] for col in mycursor.description]
            rows = [dict(zip(columns, row)) for row in mycursor.fetchall()]
            for row in rows:
                row.pop('description', None)
            print(row)
            headers = 'drugbank_id, name'

            return redirect(url_for('views.table', headers=headers, objects=json.dumps(rows)))

        if request.form.get('action6') == 'View All Proteins':
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Greenwich82",
                database='dtbank'
            )
            mycursor = mydb.cursor(buffered=True)
            mycursor.execute(
                "SELECT * FROM UniProts")
            # items = mycursor.fetchall()
            columns = [col[0] for col in mycursor.description]
            rows = [dict(zip(columns, row)) for row in mycursor.fetchall()]
            headers = 'uniprot_id, sequence'

            return redirect(url_for('views.table', headers=headers, objects=json.dumps(rows)))

        if request.form.get('action7') == 'View All Side Effects':
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Greenwich82",
                database='dtbank'
            )
            mycursor = mydb.cursor(buffered=True)
            mycursor.execute(
                "SELECT * FROM UniProts")
            # items = mycursor.fetchall()
            columns = [col[0] for col in mycursor.description]
            rows = [dict(zip(columns, row)) for row in mycursor.fetchall()]
            headers = 'umls_cui,side_effect_name'
            return redirect(url_for('views.table', headers=headers, objects=json.dumps(rows)))

        if request.form.get('action8') == 'View All Drug-Target-Interactions':
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Greenwich82",
                database='dtbank'
            )
            mycursor = mydb.cursor(buffered=True)
            mycursor.execute(
                "SELECT R.drugbank_id, R.target_name FROM Reactions R")
            # items = mycursor.fetchall()
            columns = [col[0] for col in mycursor.description]
            rows = [dict(zip(columns, row)) for row in mycursor.fetchall()]
            df = pd.DataFrame(rows)
            df.to_html('application/templates/table.html')
            return redirect(url_for('views.table2'))

        if request.form.get('action9') == 'View All Papers':
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Greenwich82",
                database='dtbank'
            )
            mycursor = mydb.cursor(buffered=True)
            mycursor.execute('SELECT DISTINCT doi FROM Wrote')
            dois = mycursor.fetchall()
            dic = {}
            for doi in dois:
                mycursor.execute(
                    'SELECT author FROM Wrote')
                authors = mycursor.fetchall()
                dic[doi] = authors
            print(dic)
            df = pd.DataFrame(dic)
            df.to_html('application/templates/table.html')
            return redirect(url_for('views.table2'))

        if request.form.get('action10') == 'View All Users':
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Greenwich82",
                database='dtbank'
            )
            mycursor = mydb.cursor(buffered=True)
            mycursor.execute(
                "SELECT * FROM Users")
            # items = mycursor.fetchall()
            columns = [col[0] for col in mycursor.description]
            rows = [dict(zip(columns, row)) for row in mycursor.fetchall()]
            for row in rows:
                del row["password"]
            df = pd.DataFrame(rows)
            df.to_html('application/templates/table.html')
            return redirect(url_for('views.table2'))

    return render_template("manager_page.html",  user=current_user)


@views.route('/tables/', methods=['GET', 'POST'])
def table2():
    return render_template('table.html')


@views.route('/error', methods=['GET', 'POST'])
def error():
    if request.method == 'POST':
        return redirect(url_for('views.home'))
    return render_template("error_page.html",  user=current_user)


def dbResultsToHtml(mycursor):
    columns = [col[0] for col in mycursor.description]
    results = mycursor.fetchall()
    if results == []:
        return 'No Result Found'
    rows = [dict(zip(columns, row)) for row in results]
    df = pd.DataFrame(rows)
    df.to_html('application/templates/table.html')
    return 'Success'


@views.route('/table/<headers>/<objects>', methods=['GET', 'POST'])
def table(headers=None, objects=None):
    print(objects)
    items = json.loads(objects)
    head = headers.split(',')
    return render_template('tab.html',
                           headers=head,
                           objects=items)
