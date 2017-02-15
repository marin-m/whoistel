#!/bin/sh

cd "$(dirname "$0")"
mkdir -p arcep
cd arcep

wget -N http://www.arcep.fr/fileadmin/reprise/dossiers/numero/ZABPQ-ZNE.xls
wget -N http://www.arcep.fr/fileadmin/wopnum.xls
wget -N http://www.galichon.com/codesgeo/data/insee.zip
wget -N http://www.arcep.fr/fileadmin/operateurs/liste-operateurs-declares.xls
wget -N http://www.arcep.fr/fileadmin/reprise/dossiers/numero/liste-zne.xls

unzip -o insee.zip
rm -f insee.zip

cd ..
echo
./generatedb.py
