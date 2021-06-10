# dummy code
import pandas as pd
import mysql.connector
import pandas as pd
from passlib.hash import sha256_crypt

user_df = pd.read_excel('excelData\DTBank.xlsx',
                        sheet_name='User', engine='openpyxl')
manager_df = pd.read_excel('excelData\DTBank.xlsx',
                           sheet_name='Database Manager', engine='openpyxl')
drug_df = pd.read_excel('excelData\DTBank.xlsx',
                        sheet_name='DrugBank', engine='openpyxl')
sider_df = pd.read_excel('excelData\DTBank.xlsx',
                         sheet_name='SIDER', engine='openpyxl')
binding_df = pd.read_excel('excelData\DTBank.xlsx',
                           sheet_name='BindingDB', engine='openpyxl')
protein_df = pd.read_excel('excelData\DTBank.xlsx',
                           sheet_name='UniProt', engine='openpyxl')

# create df s for our tables

drugbanks_df = drug_df.drop('drug_interactions', axis=1, inplace=False)
# print(drugbanks_df)
hasSideEffect_df = sider_df.drop('side_effect_name', axis=1, inplace=False)

interaction_data = {'drugbank_id_1':  [], 'drugbank_id_2': [], }
for index, row in drug_df.iterrows():
    interacting_drugs = row['drug_interactions'][:-1].split(",")
    for interacting_drug in interacting_drugs:
        interaction_data['drugbank_id_1'].append(row['drugbank_id'])
        interaction_data['drugbank_id_2'].append(interacting_drug[2:-1])

interacts_with_df = pd.DataFrame(interaction_data, columns=[
                                 'drugbank_id_1', 'drugbank_id_2'])
# print(interacts_with_df)

reactions_df = binding_df.drop(
    ['authors', 'institution'], axis=1, inplace=False)
# print(reactions_df)

wrote_data = {'doi':  [], 'author': [], }
for index, row in binding_df.iterrows():
    authors = (" " + row['authors']).split(";")
    for author in authors:
        wrote_data['doi'].append(row['doi'])
        wrote_data['author'].append(author[1:])

wrote_df = pd.DataFrame(wrote_data, columns=['doi', 'author'])
# print(papers_df)

SIDERS_df = sider_df.drop('drugbank_id', axis=1, inplace=False)


# db connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Greenwich82"
)

mycursor = mydb.cursor()

# create db and tables
for line in open(".\excelData\createtables.sql"):
    mycursor.execute(line)

# insert Users
for i, row in user_df.iterrows():
    # name,user_name,inst,password
    # sha256 should be done for the password ->row[3]
    password = sha256_crypt.encrypt((row[3]))
    row[3] = password
    mycursor.execute(
        "INSERT INTO Users(name,username,institution,password) VALUES(%s,%s,%s,%s)", tuple(row))
    mydb.commit()


# insert Managers
for i, row in manager_df.iterrows():
    # sha256 should be done
    password = sha256_crypt.encrypt((row[1]))
    row[1] = password
    mycursor.execute(
        "INSERT INTO DatabaseManagers(username,password) VALUES(%s,%s)", tuple(row))
    mydb.commit()


# insert Managers
for i, row in drugbanks_df.iterrows():
    mycursor.execute(
        "INSERT INTO DrugBanks(drugbank_id,name,description) VALUES(%s,%s,%s)", tuple(row))
    mydb.commit()

for i, row in protein_df.iterrows():
    mycursor.execute(
        "INSERT INTO UniProts(uniprot_id,sequence) VALUES(%s,%s)", tuple(row))
    mydb.commit()

for i, row in SIDERS_df.iterrows():
    row['umls_cui_update'] = row['umls_cui']
    row['side_effect_name_update'] = row['side_effect_name']
    mycursor.execute(
        "INSERT INTO SIDERS(umls_cui,side_effect_name) VALUES(%s,%s) ON DUPLICATE KEY UPDATE umls_cui=%s, side_effect_name=%s", tuple(row))
    mydb.commit()

# insert Managers
for i, row in hasSideEffect_df.iterrows():
    mycursor.execute(
        "INSERT INTO HasSideEffect(umls_cui,drugbank_id) VALUES(%s,%s)", tuple(row))
    mydb.commit()

# insert Managers
for i, row in interacts_with_df.iterrows():
    if row['drugbank_id_2'] != "":
        mycursor.execute(
            "INSERT INTO InteractsWith(drugbank_id_1,drugbank_id_2) VALUES(%s,%s)", tuple(row))
        mydb.commit()

for i, row in reactions_df.iterrows():
    mycursor.execute(
        "INSERT INTO Reactions(reaction_id,drugbank_id,uniprot_id,target_name,smiles,measure_name,affinity_nM,doi) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", tuple(row))
    mydb.commit()

for i, row in wrote_df.iterrows():
    row['doi_update'] = row['doi']
    row['author_update'] = row['author']
    mycursor.execute(
        "INSERT INTO Wrote(doi,author) VALUES(%s,%s) ON DUPLICATE KEY UPDATE doi=%s, author=%s", tuple(row))
    mydb.commit()
