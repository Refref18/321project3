DROP DATABASE IF EXISTS DTBank;
CREATE DATABASE DTBank;
USE DTBank;
CREATE TABLE DatabaseManagers(username VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL, PRIMARY KEY ( username ));
CREATE TABLE Institutions(institution_name VARCHAR(255) NOT NULL, score REAL, PRIMARY KEY ( institution_name))
CREATE TABLE Users(name VARCHAR(255), username VARCHAR(255) NOT NULL,institution VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL,PRIMARY KEY (name,username,institution));
CREATE TABLE DrugBanks(drugbank_id VARCHAR(255) NOT NULL,name VARCHAR(255),description VARCHAR(5000),PRIMARY KEY (drugbank_id));
CREATE TABLE UniProts(uniprot_id VARCHAR(255) NOT NULL,sequence VARCHAR(5000),PRIMARY KEY (uniprot_id ));
CREATE TABLE SIDERS(umls_cui VARCHAR(255) NOT NULL,side_effect_name VARCHAR(255),PRIMARY KEY (umls_cui));
CREATE TABLE HasSideEffect(drugbank_id VARCHAR(255) NOT NULL, umls_cui VARCHAR(255) NOT NULL,PRIMARY KEY (drugbank_id,umls_cui),FOREIGN KEY(drugbank_id) REFERENCES DrugBanks(drugbank_id) ON DELETE CASCADE,FOREIGN KEY(umls_cui) REFERENCES SIDERS(umls_cui) ON DELETE CASCADE);
CREATE TABLE Papers(doi VARCHAR(255) NOT NULL, institution VARCHAR(255), PRIMARY KEY (doi));
CREATE TABLE Reactions(reaction_id VARCHAR(255) NOT NULL,uniprot_id VARCHAR(255) NOT NULL,drugbank_id VARCHAR(255) NOT NULL,doi VARCHAR(255) NOT NULL,measure_name VARCHAR(255),affinity_nM  REAL,target_name VARCHAR(255),smiles VARCHAR(255), PRIMARY KEY (reaction_id), FOREIGN KEY (uniprot_id) REFERENCES UniProts(uniprot_id) ON DELETE CASCADE,FOREIGN KEY (drugbank_id) REFERENCES DrugBanks(drugbank_id) ON DELETE CASCADE, CONSTRAINT MeasureName CHECK (measure_name = 'Ki' OR measure_name ='Kd' OR measure_name ='IC50'));
CREATE TABLE InteractsWith(drugbank_id_1 VARCHAR(255) NOT NULL,drugbank_id_2 VARCHAR(255) NOT NULL,PRIMARY KEY (drugbank_id_1 , drugbank_id_2), FOREIGN KEY (drugbank_id_1) REFERENCES DrugBanks(drugbank_id) ON DELETE CASCADE,FOREIGN KEY (drugbank_id_2) REFERENCES DrugBanks(drugbank_id) ON DELETE CASCADE)
CREATE TABLE Wrote(doi VARCHAR(255) NOT NULL,author VARCHAR(255) NOT NULL,PRIMARY KEY (doi, author),FOREIGN KEY (author) REFERENCES Users(name) ON DELETE CASCADE);
CREATE TRIGGER update_score_addpaper AFTER INSERT ON dtbank.papers FOR EACH ROW UPDATE dtbank.institutions SET score = score + 5 WHERE institution_name = NEW.institution;
CREATE TRIGGER update_score_addcontributor AFTER INSERT ON dtbank.wrote FOR EACH ROW UPDATE dtbank.institutions SET score = score + 2 WHERE institution_name = (SELECT DISTINCT P.institution FROM dtbank.papers P, dtbank.wrote W WHERE P.doi = W.doi and W.doi = NEW.doi)
CREATE TRIGGER update_score_deletecontributor BEFORE DELETE ON dtbank.wrote FOR EACH ROW UPDATE dtbank.institutions SET score = score - 2 WHERE institution_name = (SELECT DISTINCT P.institution FROM dtbank.papers P, dtbank.wrote W WHERE P.doi = W.doi and W.doi = OLD.doi)
CREATE TRIGGER add_institution BEFORE INSERT ON dtbank.papers FOR EACH ROW BEGIN SET @cnt = (SELECT COUNT(*) FROM dtbank.institutions WHERE institution_name = NEW.institution); IF @cnt=0 THEN INSERT INTO dtbank.institutions(institution_name,score) VALUES (NEW.institution, 0); END IF; END;