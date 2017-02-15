#!/usr/bin/python2
#-*- encoding: Utf-8 -*-
import sqlite3
import xlrd
import csv
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# -----------------------------------------------------------

print 'Création de la base de données...'

if os.path.exists('whoistel.sqlite3'):
	os.remove('whoistel.sqlite3')

sqlite = sqlite3.connect('whoistel.sqlite3')
c = sqlite.cursor()

c.execute('''
CREATE TABLE PlagesNumerosGeographiques(
	PlageTel INTEGER,
	CodeOperateur TEXT,
	CodeInsee INTEGER
);
''')

c.execute('''
CREATE TABLE PlagesNumeros(
	PlageTel TEXT,
	CodeOperateur TEXT
);
''')

c.execute('''
CREATE TABLE Operateurs(
	CodeOperateur TEXT,
	NomOperateur TEXT,
	TypeOperateur TEXT,
	MailOperateur TEXT,
	SiteOperateur TEXT
);
''')

c.execute('''
CREATE TABLE Communes(
	CodeInsee INTEGER,
	NomCommune TEXT,
	CodePostal INTEGER,
	NomDepartement TEXT
);
''')

c.execute('''
CREATE TABLE CommunesZNE(
	CodeZNE INTEGER,
	CodeInsee INTEGER
);
''')

# -----------------------------------------------------------

print 'Lecture du fichier Excel des numéros géographiques...'

xls_geo = xlrd.open_workbook('arcep/ZABPQ-ZNE.xls')
sheet = xls_geo.sheet_by_index(0)
geo = []
nums1ereListe = []
nongeo = []

for rownum in xrange(1, sheet.nrows):
	row = sheet.row_values(rownum)
	
	# Ne garder que les numéros géographiques /^0[1-5]/,
	# la BDD suivante s'occupera du reste.
	
	if row[0] >= 60000:
		break
	
	nums1ereListe.append('0'+str(int(row[0])))
	
	if row[2] == '':
		nongeo.append(('0'+str(int(row[0])), str(row[1])))
	else:
		geo.append((int(row[0]), str(row[1]), int(row[2])))

c.executemany("INSERT INTO PlagesNumerosGeographiques (PlageTel, CodeOperateur, CodeInsee) VALUES (?, ?, ?);", geo)

del xls_geo
del sheet
del geo

# -----------------------------------------------------------

print 'Lecture du fichier Excel des numéros non-géographiques...'

xls_nongeo = xlrd.open_workbook('arcep/wopnum.xls')
sheet = xls_nongeo.sheet_by_index(0)

for rownum in xrange(1, sheet.nrows):
	row = sheet.row_values(rownum)
	
	# Vérifier les doublons avec la liste des numéros géographiques
	
	if row[0][0] == '0' and row[0][1] in '12345':
		doublon = False
		for num2 in nums1ereListe[:100]: # Ne va pas au-delà de 99 avec la liste du 27 juin 2013
			if num2.startswith(row[0]):
				doublon = True
				nums1ereListe = nums1ereListe[nums1ereListe.index(num2)+1:]
				break
		if doublon is True:
			continue
	
	nongeo.append((str(row[0]), str(row[2])))

c.executemany("INSERT INTO PlagesNumeros (PlageTel, CodeOperateur) VALUES (?, ?);", nongeo)

del xls_nongeo
del sheet
del nongeo

# -----------------------------------------------------------

print 'Lecture du fichier Excel des codes opérateur...'

xls_ops = xlrd.open_workbook('arcep/liste-operateurs-declares.xls')
sheet = xls_ops.sheet_by_index(0)
ops = []

for rownum in xrange(1, sheet.nrows):
	row = sheet.row_values(rownum)
	
	if type(row[0]) == float:
		row[0] = str(int(row[0]))
	
	if type(row[1]) == float:
		row[1] = str(int(row[1]))
	
	ops.append((
		row[1].strip(),
		row[0].strip(),
		row[3].strip(),
		row[4].strip(),
		row[5].strip()
		))

c.executemany("INSERT INTO Operateurs(CodeOperateur, NomOperateur, TypeOperateur, MailOperateur, SiteOperateur) VALUES (?, ?, ?, ?, ?);", ops)

del xls_ops
del sheet
del ops

# -----------------------------------------------------------

print 'Lecture du fichier CSV des codes communes...'

file_insee = open('arcep/insee.csv', 'rb')
csv_insee = csv.DictReader(file_insee, delimiter=';')
insee = []

for row in csv_insee:
	if row['Codepos'] == '':
		continue
	
	insee.append((
		int(row['INSEE'].decode('cp1252').strip()),
		row['Commune'].decode('cp1252').strip(),
		int(row['Codepos'].decode('cp1252').strip()),
		row['Departement'].decode('cp1252').strip()
		))

c.executemany("INSERT INTO Communes(CodeInsee, NomCommune, CodePostal, NomDepartement) VALUES (?, ?, ?, ?);", insee)

file_insee.close()

del csv_insee
del insee

# -----------------------------------------------------------

print 'Lecture du fichier CSV des zones géographiques...'

xls_zne = xlrd.open_workbook('arcep/liste-zne.xls')
sheet = xls_ops.sheet_by_index(1)
zne = []

for rownum in xrange(1, sheet.nrows):
	row = sheet.row_values(rownum)
	
	zne.append((
		int(row[0]),
		int(row[1])
		))

c.executemany("INSERT INTO CommunesZNE(CodeZNE, CodeINSEE) VALUES (?, ?);", zne)

del xls_zne
del sheet
del zne

# -----------------------------------------------------------

print 'Sauvegarde de la base de données...'

sqlite.commit()
sqlite.close()
