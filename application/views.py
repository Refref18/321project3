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
import pandas as pd
from flask import jsonify

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
    print('req ' + str(request))
    if request.method == 'POST':
        mydb = mysql.connector.connect(
            user='root', password='Greenwich82', host='localhost', database='dtbank')
        mycursor = mydb.cursor(buffered=True)
        # RABİA KISMIIIIIIII!!!!!!!!!!!
        if request.form.get('action1') == 'View Drug Table':
            pass
        if request.form.get('action2') == 'Drug Interaction Table':
            pass
        if request.form.get('action3') == 'Side Effect Table':
            pass
        if request.form.get('action4') == 'Interaction Proteins Table':
            pass

        if request.form.get('action5') == 'Find Interacting Drugs':
            # input -> uniprot_id   output -> 'drugbank_id','drugbank_name'
            uniprot_id = request.form.get('uniprot_id') 
            mycursor.execute("SELECT * FROM dtbank.uniprots WHERE uniprot_id = %s", (uniprot_id,))
            if mycursor.fetchall() == [] :
                return render_template('error.html', error='Uniprot ID Not Found')

            mycursor.execute(
             ("SELECT D.drugbank_id, D.name FROM dtbank.reactions R, dtbank.drugbanks D "
              "WHERE uniprot_id = %s AND R.drugbank_id = D.drugbank_id"), (uniprot_id,))
            dbResultsToHtml(mycursor)
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

            mycursor.execute("SELECT * FROM dtbank.siders WHERE umls_cui = %s", (umls_cui,))
            if mycursor.fetchall() == [] :
                return render_template('error.html', error='Umls Cui Not Found')

            mycursor.execute(
             (" SELECT D.drugbank_id, D.name FROM dtbank.hassideeffect H, dtbank.drugbanks D " 
                "WHERE H.umls_cui = %s AND H.drugbank_id = D.drugbank_id"), (umls_cui,))
            dbResultsToHtml(mycursor)
            return redirect(url_for('views.table2'))
            #return jsonify({'columns' : ('drugbank_id','drug_name'), 'rows': mycursor.fetchall()})
        
        if request.form.get('action9') == 'Search Keyword in Description':
            # input -> keyword  output -> 'drugbank_id','drug_name','description'
            keyword = request.form.get('keyword')   
            mycursor.execute(
             " SELECT * FROM dtbank.drugbanks WHERE description LIKE %s", (('%' + keyword + '%'),))
            dbResultsToHtml(mycursor)
            return redirect(url_for('views.table2'))
        
        if request.form.get('action10') == 'Drugs with least side effects':
            # input -> uniprot_id  output -> drugbank_id,drug_name
            uniprot_id = request.form.get('uniprot_id_2') 
            mycursor.execute("SELECT * FROM dtbank.uniprots WHERE uniprot_id = %s", (uniprot_id,))
            if mycursor.fetchall() == [] :
                return render_template('error.html', error='Uniprot ID Not Found')

            mycursor.execute(("SELECT    D.drugbank_id, D.name AS drugname "
                                "FROM 	dtbank.reactions R, dtbank.hassideeffect H, dtbank.drugbanks D "
                                "WHERE  R.uniprot_id = %s AND R.drugbank_id = H.drugbank_id AND H.drugbank_id = D.drugbank_id "
                                "GROUP BY D.drugbank_id "
                                "HAVING   COUNT(*) =  (SELECT MIN(Temp.numOfsideeffects) "
					                                    "FROM (SELECT R.drugbank_id, COUNT(*) numOfsideeffects "
							                                    "FROM dtbank.reactions R, dtbank.hassideeffect H "
			                                                    "WHERE R.uniprot_id = %s AND R.drugbank_id = H.drugbank_id "
						                                        "GROUP BY drugbank_id) Temp)"),(uniprot_id,uniprot_id))
            dbResultsToHtml(mycursor)
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
            mycursor.execute("SELECT * FROM dtbank.drugbanks WHERE drugbank_id = %s", (drugbank_id,))
            if mycursor.fetchall() == [] :
                return render_template('error.html', error='Drugbank ID Not Found')
            measurement_type = request.form.get('measurement_type')
            affinity_min = request.form.get('affinity_min')
            if affinity_min == '' :
                return render_template('error.html', error='Enter Affinity Min')
            affinity_max = request.form.get('affinity_max')
            if affinity_min == '' :
                return render_template('error.html', error='Enter Affinity Max')
            mycursor.execute(
             (" CALL FilterTargets(%s, %s, %s, %s)"), (drugbank_id, measurement_type, affinity_min, affinity_max)) 
            dbResultsToHtml(mycursor)
            return redirect(url_for('views.table2'))


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
            pass
        if request.form.get('action2.1') == 'Delete Drug':
            pass
        if request.form.get('action3') == 'Delete protein':
            pass
        if request.form.get('action4.1') == 'Delete Contributor':
            pass
        if request.form.get('action4.2') == 'Add Contributor':
            pass

    """
     and 
    delete drugs using DrugBank IDs. 
    Database managers shall be able to delete proteins using UniProt IDs.
    Database managers shall be able to update contributors of papers=documents using Reaction IDs.
    Database managers shall be able to separately view all drugs listed in DrugBank, all proteins listed in
    UniProt, all side eects listed in SIDER, all drug - target interactions, all papers and their contributors
listed in BindingDB, and all users in DTBank.
    """
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
    rows = [dict(zip(columns, row)) for row in mycursor.fetchall()]
    df = pd.DataFrame(rows)
    df.to_html('application/templates/table.html')