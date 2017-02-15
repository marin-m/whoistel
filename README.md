whoistel, a whois program for french telephone numbers
======================================================

This is a work from 2013, written in Python 2.

The program uses the following information sources:

* Databases from [ARCEP](http://arcep.fr/)/INSEE, converted to SQLite format and then fetched locally
* [Annu.com's API](http://v3.annu.com/cgi-bin/srch.cgi?j=1&s=0xxxxxxxxx&n=10). Annu.com is Iliad's reverse telephone directory
* The [ADSL eligibility test](https://www.ovhtelecom.fr/adsl/eligibilite.xml) of OVH Telecom

Using whoistel
--------------

    ./whoistel.py <french telephone number> [--no-annu] [--no-ovh]

You need Python 2.7 to run this script.

ARCEP's databases
-----------------

* [Database that links geographic phone numbers to operators and city codes](http://www.arcep.fr/fileadmin/reprise/dossiers/numero/ZABPQ-ZNE.xls)
* [Database that links phone numbers ranges to operators](http://www.arcep.fr/fileadmin/wopnum.xls)
* [Database that links city codes to city names (from INSEE)](http://www.galichon.com/codesgeo/data/insee.zip)
* [Database that links operator codes to operator names](http://www.arcep.fr/fileadmin/operateurs/liste-operateurs-declares.xls)

Annu.com's API
--------------

[http://v3.annu.com/cgi-bin/srch.cgi](http://v3.annu.com/cgi-bin/srch.cgi)

GET parameters:

* ```j```: ```1``` (removing this parameter sets the Content-Type header to text/html instead of text/plain)
* ```s```: the phone number
* ```n```: the maximum number of results
* ```i```: ```062C706C-A373-402E-B62A-89994449CD16``` (this parameter apparently may be removed or modified without difference)
* ```lat```/```long```: user's position? These parameters aren't mandatory and looks useless, that's maybe for Iliad's statistics

OVH's AJAX eligibility check
----------------------------

[https://www.ovhtelecom.fr/cgi-bin/ajax/ajaxEligibilityCheck.cgi](https://www.ovhtelecom.fr/cgi-bin/ajax/ajaxEligibilityCheck.cgi)

GET parameters:

* ```number```: the phone number
* ```lightRequest```: ```yes``` if you want less informations
* ```fromIndexBar```: ```yes``` if the content is loaded from ovhtelecom.fr's homepage. This parameter looks useless
* ```callback```: a function name if you want to use JSONP, otherwise don't send this parameter

Useful Wikipedia pages
----------------------

* [Plan de numérotation téléphonique en France](http://fr.wikipedia.org/wiki/Plan_de_num%C3%A9rotation_t%C3%A9l%C3%A9phonique_en_France)
* [Numéros de téléphone français en 08](http://fr.wikipedia.org/wiki/Num%C3%A9ros_de_t%C3%A9l%C3%A9phone_fran%C3%A7ais_en_08)
* [Indicatif téléphonique local en France](http://fr.wikipedia.org/wiki/Indicatif_t%C3%A9l%C3%A9phonique_local_en_France)
* [Liste des préfixes des opérateurs de téléphonie par internet en France](http://fr.wikipedia.org/wiki/Liste_des_pr%C3%A9fixes_des_op%C3%A9rateurs_de_t%C3%A9l%C3%A9phonie_par_internet_en_France)
* [Liste des préfixes des opérateurs de téléphonie mobile en France](http://fr.wikipedia.org/wiki/Liste_des_pr%C3%A9fixes_des_op%C3%A9rateurs_de_t%C3%A9l%C3%A9phonie_mobile_en_France)

Informations about surcharged calls
-----------------------------------

* ARCEP: [Les numéros 08 et les numéros courts](http://www.telecom-infoconso.fr/les-numeros-08-et-les-numeros-courts/)
* Orange: [Le service téléphonique](http://boutique.orange.fr/vf/tel_maison/pdf/tarifs_fixe_ft.pdf)
* SFR: [Tarifs et conditions générales d'inscription](http://static.s-sfr.fr/media/brochure_box.pdf)
* Free: [Tarifs France métropolitaine mobiles et numéros spéciaux](http://www.free.fr/pdf/tarifs-mobiles-numeros-speciaux_07042011.pdf)
* 118XYZ: [Les principaux tarifs des services 118](http://www.appel118.fr/detail.php)

TODO
----

* Use [this database](http://www.arcep.fr/fileadmin/reprise/dossiers/numero/liste-zne.xls) to show all cities composing a ZNE, not only the chief town
* Maybe add a backend for a [website](http://www.annuaire-inverse-france.com/) allowing to access the data of the [G'NUM database](http://www.arcep.fr/index.php?id=8765)
* Create a database about the surcharge of four-digits numbers
* Choose a language for the script and the README between French, English, or Frenglish
* Find a INSEE database that contains the name of cities with normal case
* Build packages for various distributions
