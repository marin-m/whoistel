#!/usr/bin/python2
#-*- encoding: Utf-8 -*-
from urllib import quote_plus
from urllib2 import urlopen
from sqlite3 import connect
from socket import timeout
from os.path import exists
from sys import argv, exit
from datetime import date
from json import loads
import os

# Se mettre dans le même dossier que le script

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Variables globales

tel = None
useAnnu = True
useOVH = True

is_EZABPQMCDU = False
is_special = False

urlAnnu = 'http://v3.annu.com/cgi-bin/srch.cgi?j=1&n=10&s='
urlOVH = 'https://www.ovhtelecom.fr/cgi-bin/ajax/ajaxEligibilityCheck.cgi?lightRequest=yes&number='

# Interpréter les arguments

for arg in argv[1:]:
	arg = arg.replace('-','')
	arg = arg.replace(' ','')
	arg = arg.replace('.','')
	arg = arg.replace('+33(0)','0')
	arg = arg.replace('+330','0')
	arg = arg.replace('+33','0')
	arg = arg.strip().lower()
	
	if arg.isdigit() and tel is None:
		tel = arg
	
	elif arg == 'noannu':
		useAnnu = False
	
	elif arg == 'noovh':
		useOVH = False
	
	else:
		tel = None
		break

# Message d'utilisation

if tel is None:
	print 'Utilisation : %s <numéro de téléphone français> [--no-annu] [--no-ovh]' % argv[0]
	exit()

# Fonctions d'information

def section(text):
	print
	print '+-' + '-' * len(text) + '-+'
	print '| ' + text + ' |'
	print '+-' + '-' * len(text) + '-+'
	print

def erreur(text):
	print '[Erreur] ' + text
	print
	exit()

# Se connecter à la base de données de l'ARCEP en local

if not exists('whoistel.sqlite3'):
	erreur('Vous devez générer le fichier "whoistel.sqlite3" avec generatedb.py.')

conn = connect('whoistel.sqlite3')
c = conn.cursor()

# Fonctions pour l'ARCEP

def getInfosINSEE(codeINSEE):
	c.execute('SELECT * FROM Communes WHERE CodeInsee=?', (codeINSEE,))
	infos = c.fetchone()
	
	print
	"""
	print u'Commune : ' + infos[1]
	print u'Département : ' + infos[3]
	print u'Code postal : ' + str(infos[2]).zfill(5)
	print u'Code INSEE : ' + str(codeINSEE).zfill(5)
	"""

def getInfosOperateur(codeOperateur):
	c.execute('SELECT * FROM Operateurs WHERE CodeOperateur=?', (codeOperateur,))
	infos = c.fetchone()
	
	print
	print u'Opérateur : ' + infos[1]
	print u'Code opérateur : ' + codeOperateur
	print u'Type : ' + infos[2][0].upper() + infos[2][1:]
	
	if infos[3] != u'':
		print u'Courriel : ' + infos[3]
	
	if infos[4] != u'':
		url = infos[4].lower()
		
		if not url.startswith('http'):
			url = 'http://' + url
		
		if '/' not in infos[4][8:]:
			url += '/'
		
		print u'Site web : ' + url

def getGeographicNumberARCEP():
	c.execute('SELECT * FROM PlagesNumerosGeographiques WHERE PlageTel=?', (int(tel[1:6]),))
	infos = c.fetchone()
	
	print infos
	
	if infos is None:
		getNonGeographicNumberARCEP()
	
	else:
		getInfosINSEE(infos[2])
		getInfosOperateur(infos[1])

def getNonGeographicNumberARCEP():
	for lenTel in xrange(min(6, len(tel)), 0, -1):
		c.execute('SELECT * FROM PlagesNumeros WHERE PlageTel=?', (tel[:lenTel],))
		infos = c.fetchone()
		
		if infos is not None:
			break
	
	if infos is None:
		erreur('Numéro inconnu.')
	
	else:
		getInfosOperateur(infos[1])

# Fonctions pour les numéros spéciaux

def getSurtax():
	print
	newRates = (date.today().year >= 2015)
	
	if len(tel) == 10:
		type08 = int(tel[2:4])
		
		if type08 >= 90:
			print 'Dénomination commerciale : Numéro Audiotel'
		
		if (newRates and type08 <= 5) or (type08 in (1, 2, 3, 4, 8)):
			print 'Dénomination commerciale : Numéro Vert'
			print 'Prix : Entièrement gratuit'
		
		elif type08 <= 9:
			print 'Dénomination commerciale : Numéro Vert'
			print 'Surtaxe : Non'
		
		elif 10 <= type08 <= 19 or type08 == 84:
			print 'Dénomination commerciale : Numéro Azur'
			print 'Surtaxe par appel : 0,078 €'
			print 'Surtaxe par minute : 0,014 € en heures creuses, ou 0,028 € en heures pleines'
		
		elif type08 == 20 or type08 == 21:
			print 'Dénomination commerciale : Numéro Indigo'
			print 'Surtaxe maximum par appel : 0,112 €'
			print 'Surtaxe maximum par minute après 56s : 0,118 €'
		
		elif type08 == 25 or type08 == 26:
			print 'Dénomination commerciale : Numéro Indigo'
			print 'Surtaxe par appel : 0,112 €'
			print 'Surtaxe par minute après 45s : 0,15 €'
		
		elif type08 == 36:
			print 'Prix : Variable (services divers)'
		
		elif 40 <= type08 <= 43:
			print "Utilisation : Numéro technique destiné à l'acheminement des communications," +\
				  "ne doit pas être appelé directement (cf décision n°2006-0452)"
		
		elif 50 <= type08 <= 58:
			print 'Prix : Variable (accès VPN RPC)'
		
		elif 60 <= type08 <= 68:
			print 'Prix : Variable (accès RTC)'
				
		elif type08 == 90:
			print 'Surtaxe : Dépend du numéro et du FAI.'
			print '          - Orange : Maximum de 0,112 € toutes les 45s'
			
			if tel[4:6] == '64':
				print '          - SFR : 0,112 € toutes les 60s'
			elif tel[4:6] == '71':
				print '          - SFR : 0,15 € par minute, paliers de 45s'
			else:
				print '          - SFR : Inconnu'
			
			print '          - Free : 0,11 € puis, après 45s, 0,15€ par minute'
		
		elif type08 == 91:
			print 'Surtaxe par appel (Free) : 0,09 €'
			print 'Surtaxe toutes les 30s : 0,112 €'
			print 'Durée maximale : 30 minutes'
		
		elif type08 == 92:
			print 'Surtaxe par appel (Free) : 0,09 €'
			print 'Surtaxe toutes les 20s : 0,112 €'
			print 'Durée maximale : 30 minutes'
		
		elif type08 == 93:
			print 'Surtaxe : inconnue'
		
		elif type08 == 97:
			print 'Surtaxe par appel : 0,562 €'
		
		elif type08 == 99:
			print 'Surtaxe par appel : Dépend du FAI.'
			print '                    - Orange : 12s gratuites puis 1,349 €'
			print '                    - Free : 1,35 €'
			print '                    - SFR : 1,462 €'
			print 'Surtaxe toutes les 20s : 0,112 €'
		
		else:
			erreur('Numéro inconnu.')
	
	elif tel == '1044':
		print 'Surtaxe par appel : 0,078 €'
		print 'Surtaxe par minute : 0,014 € en heures creuses, ou 0,028 € en heures pleines'
	
	elif tel.startswith('10'):
		print 'Surtaxe : Non'

def getSurtax118():
	surtax118 = {
		  0: '1,46 € / appel, 1,46 € les 2 premières min puis 0,90 € à partir 3ème min',
		  6: '1,35 €/appel + 0,34 €/min',
		  7: '1,35 €/appel + 0,34 €/min',
		  8: '1,46 €/appel + 0,45 €/min',
		218: '0,90 €/appel + 0,90 €/min',
		222: '0,90 €/appel + 0,90 €/min',
		318: '0,90 €/appel + 0,90 €/min',
		612: '1,01 €/appel',
		700: '3 €/appel',
		710: '0 €',
		711: '0,79 €/appel + 0,225 €/min',
		712: '1,35 €/appel + 0,225 €/min',
		713: '0 €',
		777: '1,20 €/appel (SFR uniquement)',
		888: '1,12 €/appel + 1,11 €/min',
	}
	
	if int(tel[3:]) in surtax118:
		print 'Surtaxe : ' + surtax118[int(tel[3:])]
	
	else:
		erreur('Numéro inconnu.')

def getSpecial():
	special = {
		15: 'SAMU',
		17: 'Police et gendarmerie',
		18: 'Pompiers',
		110: 'Collecte de dons',
		112: "Numéro d'urgence européen",
		115: 'SAMU social',
		116000: 'SOS enfants disparus'
	}
	
	if int(tel) in special:
		print 'Type : Spécial'
		print 'Fonction : ' + special[int(tel)]
	
	else:
		erreur('Numéro inconnu.')

# Fonctions pour Annu.com

def getAnnu():
	section('Informations Annu.com')
	
	try:
		infos = loads(urlopen(urlAnnu + tel, timeout=15).read().decode('cp1252'))
		goodResults = False
		
		# Avons-nous au moins un résultat ?
		
		if 'liste_part' in infos:
			infos = infos['liste_part'] + infos['liste_pro']
			
			if len(infos) > 0:
				for people in infos:
					# Vérifier qu'au moins un des numéros de téléphone
					# est celui que nous cherchons, sinon c'est un
					# faux-positif.
					
					numeroOk = False
					
					for numero in people['numeros']:
						if numero.replace(' ','') == tel:
							numeroOk = True
							break
					
					if not numeroOk:
						continue
					
					# Afficher les informations
					
					if goodResults:
						print
					
					goodResults = True
					
					if people['firstname'] != '':
						print u'Prénom : ' + people['firstname']
					
					if people['name'] != '':
						print u'Nom : ' + people['name']
					
					if people['name'] != '' or people['firstname'] != '':
						print
					
					print u'Adresse : ' + people['address']
					print u'Commune : ' + people['city']
					print u'Code postal : ' + people['zipcode']
					
					if people['email'] != '':
						print u'Courriel : ' + people['email']
					
					if people['activite'] != '':
						print u'Activité : ' + people['activite'][0].upper() + people['activite'][1:]
					
					if len(people['numeros']) > 1:
						printAutreNumero = False
						
						for num in people['numeros']:
							if printAutreNumero:
								print u'          - ' + num
							
							else:
								print u'Numéros : - ' + num
								printAutreNumero = True
					
					if people['lat'] != '':
						print u'Position : %s, %s' % (
							people['lat'],
							people['long']
						)
						print u'Google Maps : https://maps.google.com/maps?q=%s,%s&hl=fr' % (
							people['lat'],
							people['long']
						)
					
					else:
						print u'Google Maps : https://maps.google.com/maps?q=%s&hl=fr' % \
							quote_plus(
								(
									u'%s, %s %s' % (
										people['address'],
										people['zipcode'],
										people['city']
									)
								).encode('utf8')
							)
		
		if not goodResults:
			print "Pas d'informations disponibles."
	
	except timeout:
		erreur('Impossible de se connecter à Annu.com (timeout : 15 secondes).')

# Fonctions pour OVH Telecom

def getOVH():
	section('Informations OVH Telecom')
	
	try:
		infos = loads(urlopen(urlOVH + tel, timeout=15).read())
		
		if 'line' in infos and 'active' in infos['line']:
			infos = infos['line']['active']
			
			if infos['address']['additionnalInfos']['porte'] != '':
				print u'Porte : ' + infos['address']['additionnalInfos']['porte']
			
			if infos['address']['additionnalInfos']['etage'] != '':
				print u'Étage : ' + infos['address']['additionnalInfos']['etage']
			
			if infos['address']['additionnalInfos']['escalier'] != '':
				print u'Escalier : ' + infos['address']['additionnalInfos']['escalier']
			
			if infos['address']['additionnalInfos']['batiment'] != '':
				print u'Bâtiment : ' + infos['address']['additionnalInfos']['batiment']
			
			if infos['address']['additionnalInfos']['residence'] != '':
				print u'Résidence : ' + infos['address']['additionnalInfos']['residence']
			
			print u'Adresse : ' + infos['address']['addressFull']
			
			print u'Commune : ' + infos['address']['city']
			print u'Code postal : ' + infos['address']['postalCode']
			print u'Code INSEE : ' + infos['address']['inseeCode']
			
			print
			print u'NRA : ' + infos['line']['nra']

			c.execute('SELECT * FROM Communes WHERE CodeInsee=?', (infos['line']['nraInfo']['codeInsee'],))
			insee = c.fetchone()
			print u'Commune du NRA : %d %s' % (insee[2], insee[1])
			print u'Lignes du NRA : ' + str(infos['line']['nraLines'])
			
			if 'nraGpsInfo' in infos['line']:
				print u'Position du NRA : %s, %s' % (
					infos['line']['nraGpsInfo']['latitude'],
					infos['line']['nraGpsInfo']['longitude'])
				
				print u'NRA sur Google Maps : https://maps.google.com/maps?q=%s,%s&hl=fr' % (
					infos['line']['nraGpsInfo']['latitude'],
					infos['line']['nraGpsInfo']['longitude'])
			
			if infos['line']['distance'] > 0:
				print u'Distance du NRA : %d mètres' % infos['line']['distance']
		
		else:
			print "Pas d'informations disponibles."
	
	except timeout:
		erreur('Impossible de se connecter à OVHTelecom.fr (timeout : 15 secondes).')

# Déterminer le type de numéro de téléphone

section('Informations ARCEP')

print 'Numéro : ' + tel

if tel[0] == '0' and len(tel) == 10: # EZABPQMCDU
	print 'Type : EZABPQMCDU'
	
	is_EZABPQMCDU = True

elif len(tel) == 4 or (len(tel) == 6 and tel.startswith('118')): # 3BPQ, 10XY, 16XY
	if tel[0] == '3':
		print 'Type : 3BPQ'
	
	elif tel.startswith('118'):
		print 'Type : 118XYZ'
		getSurtax118()
	
	else:
		print 'Type : ' + tel[:2] + 'XY'

elif len(tel) == 2 or len(tel) == 3 or len(tel) == 6:
	is_special = True
	getSpecial()

else:
	erreur('Numéro inconnu.')

# Afficher les informations de l'ARCEP

if is_EZABPQMCDU and '1' <= tel[1] <= '5':
	getGeographicNumberARCEP()

elif not is_special:
	getNonGeographicNumberARCEP()

if (is_EZABPQMCDU and tel[1] == '8') or tel.startswith('10'):
	getSurtax()

# Afficher les informations d'Annu.com

if useAnnu and is_EZABPQMCDU and tel[1] != '8':
	getAnnu()

# Afficher les informations d'OVH

if useOVH and is_EZABPQMCDU and '1' <= tel[1] <= '5':
	getOVH()

# Fermer la connexion à la base de données de l'ARCEP

print
conn.close()
