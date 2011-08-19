#!/bin/bash

PARENT=MAST
MISSION=hpol
LOGFILE=${MISSION}.log
RDFSTORE=../mast-rdf
MISSIONSTORE=../AstroExplorer/Missions/${PARENT}/${MISSION}
BIBLIST=${MISSIONSTORE}/${MISSION}.biblist.txt
CONF=default2.conf

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

runStage "adsrdf"     adsclassic2rdf.py $RDFSTORE $BIBLIST
runStage "simbadrdf"  simbad2rdf.py ${MISSIONSTORE}/${MISSION}.simbad.dict $RDFSTORE
runStage "obsvrdf"    newmast/mast_obsvrdf.py $MISSION ${MISSIONSTORE}/obscore.${MISSION}.psv 	
runStage "pubrdf"     newmast/mast_pubrdf.py $MISSION ${MISSIONSTORE}/map.${MISSION}.txt
# runStage "proprdf"   
runStage "adsload"    loadfiles.py $BIBLIST $CONF
runStage "simbadload" loadfiles-simbad.py $BIBLIST $CONF
runStage "obsvload"   newmast/mast_obsvload.py $MISSION
runStage "pubload"    newmast/mast_pubload.py $MISSION
# runStage "propload"
runStage "pubsolr"    rdf2solr5.py $PARENT $MISSION $BIBLIST

echo "# Ending script: `date`" >> $LOGFILE
