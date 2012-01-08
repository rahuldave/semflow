#!/bin/bash

PARENT=Chandra
MISSION=chandra
LOGFILE=../${MISSION}.log
RDFSTORE=../chandra-rdf
MISSIONSTORE=../AstroExplorer/Missions/${PARENT}/${MISSION}/transferdata

# run the stage, logging start and end time, as well as
# the status, to $LOGFILE
#
# Arguments:
#    label  - used for logging
#    python script
#    arguments to script
#
runStage() {
    if [ $# -gt 1 ]; then
	lbl=$1
	shift
	echo "START  ${lbl} `date`" >> $LOGFILE
	python $@
	if [ $? -eq 0 ]; then
	    echo "END    ${lbl} `date`" >> $LOGFILE
	else
	    echo "FAILED ${lbl} `date`" >> $LOGFILE
	fi
    fi
}

echo "# Logging to $LOGFILE"
touch $LOGFILE
echo "######################################" >> $LOGFILE
echo "# Starting script: `date`" >> $LOGFILE

runStage "adsrdf aa"     adsclassic2rdf.py $RDFSTORE ${MISSIONSTORE}/pubsaa.biblist.txt
runStage "simbadrdf aa"  simbad2rdf.py ${MISSIONSTORE}/cleaned.pubsaa.dict $RDFSTORE
runStage "pubrdf aa"     chandra/genrdf.py pub ${MISSIONSTORE}/pubsaa.biblist.txt $RDFSTORE/
runStage "adsrdf ab"     adsclassic2rdf.py $RDFSTORE ${MISSIONSTORE}/pubsab.biblist.txt
runStage "simbadrdf ab"  simbad2rdf.py ${MISSIONSTORE}/cleaned.pubsab.dict $RDFSTORE
runStage "pubrdf ab"     chandra/genrdf.py pub ${MISSIONSTORE}/pubsab.biblist.txt $RDFSTORE/
runStage "adsrdf ac"     adsclassic2rdf.py $RDFSTORE ${MISSIONSTORE}/pubsac.biblist.txt
runStage "simbadrdf ac"  simbad2rdf.py ${MISSIONSTORE}/cleaned.pubsac.dict $RDFSTORE
runStage "pubrdf ac"     chandra/genrdf.py pub ${MISSIONSTORE}/pubsac.biblist.txt $RDFSTORE/
runStage "adsrdf ad"     adsclassic2rdf.py $RDFSTORE ${MISSIONSTORE}/pubsad.biblist.txt
runStage "simbadrdf ad"  simbad2rdf.py ${MISSIONSTORE}/cleaned.pubsad.dict $RDFSTORE
runStage "pubrdf ad"     chandra/genrdf.py pub ${MISSIONSTORE}/pubsad.biblist.txt $RDFSTORE/
runStage "adsrdf ae"     adsclassic2rdf.py $RDFSTORE ${MISSIONSTORE}/pubsae.biblist.txt
runStage "simbadrdf ae"  simbad2rdf.py ${MISSIONSTORE}/cleaned.pubsae.dict $RDFSTORE
runStage "pubrdf ae"     chandra/genrdf.py pub ${MISSIONSTORE}/pubsae.biblist.txt $RDFSTORE/
runStage "adsrdf af"     adsclassic2rdf.py $RDFSTORE ${MISSIONSTORE}/pubsaf.biblist.txt
runStage "simbadrdf af"  simbad2rdf.py ${MISSIONSTORE}/cleaned.pubsaf.dict $RDFSTORE
runStage "pubrdf af"     chandra/genrdf.py pub ${MISSIONSTORE}/pubsaf.biblist.txt $RDFSTORE/
runStage "adsrdf ag"     adsclassic2rdf.py $RDFSTORE ${MISSIONSTORE}/pubsag.biblist.txt
runStage "simbadrdf ag"  simbad2rdf.py ${MISSIONSTORE}/cleaned.pubsag.dict $RDFSTORE
runStage "pubrdf ag"     chandra/genrdf.py pub ${MISSIONSTORE}/pubsag.biblist.txt $RDFSTORE/
runStage "adsrdf ah"     adsclassic2rdf.py $RDFSTORE ${MISSIONSTORE}/pubsah.biblist.txt
runStage "simbadrdf ah"  simbad2rdf.py ${MISSIONSTORE}/cleaned.pubsah.dict $RDFSTORE
runStage "pubrdf ah"     chandra/genrdf.py pub ${MISSIONSTORE}/pubsah.biblist.txt $RDFSTORE/
runStage "adsrdf ai"     adsclassic2rdf.py $RDFSTORE ${MISSIONSTORE}/pubsai.biblist.txt
runStage "simbadrdf ai"  simbad2rdf.py ${MISSIONSTORE}/cleaned.pubsai.dict $RDFSTORE
runStage "pubrdf ai"     chandra/genrdf.py pub ${MISSIONSTORE}/pubsai.biblist.txt $RDFSTORE/
runStage "adsrdf aj"     adsclassic2rdf.py $RDFSTORE ${MISSIONSTORE}/pubsaj.biblist.txt
runStage "simbadrdf aj"  simbad2rdf.py ${MISSIONSTORE}/cleaned.pubsaj.dict $RDFSTORE
runStage "pubrdf aj"     chandra/genrdf.py pub ${MISSIONSTORE}/pubsaj.biblist.txt $RDFSTORE/
runStage "adsrdf ak"     adsclassic2rdf.py $RDFSTORE ${MISSIONSTORE}/pubsak.biblist.txt
runStage "simbadrdf ak"  simbad2rdf.py ${MISSIONSTORE}/cleaned.pubsak.dict $RDFSTORE
runStage "pubrdf ak"     chandra/genrdf.py pub ${MISSIONSTORE}/pubsak.biblist.txt $RDFSTORE/
runStage "adsrdf al"     adsclassic2rdf.py $RDFSTORE ${MISSIONSTORE}/pubsal.biblist.txt
runStage "simbadrdf al"  simbad2rdf.py ${MISSIONSTORE}/cleaned.pubsal.dict $RDFSTORE
runStage "pubrdf al"     chandra/genrdf.py pub ${MISSIONSTORE}/pubsal.biblist.txt $RDFSTORE/
echo "# Ending script: `date`" >> $LOGFILE
