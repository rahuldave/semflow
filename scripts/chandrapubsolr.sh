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

runStage "pubsolr aa"    rdf2solarfuncs.py CHANDRA chandra bib ${MISSIONSTORE}/pubsaa.biblist.txt
runStage "pubsolr ab"    rdf2solarfuncs.py CHANDRA chandra bib ${MISSIONSTORE}/pubsab.biblist.txt
runStage "pubsolr ac"    rdf2solarfuncs.py CHANDRA chandra bib ${MISSIONSTORE}/pubsac.biblist.txt
runStage "pubsolr ad"    rdf2solarfuncs.py CHANDRA chandra bib ${MISSIONSTORE}/pubsad.biblist.txt
runStage "pubsolr ae"    rdf2solarfuncs.py CHANDRA chandra bib ${MISSIONSTORE}/pubsae.biblist.txt
runStage "pubsolr af"    rdf2solarfuncs.py CHANDRA chandra bib ${MISSIONSTORE}/pubsaf.biblist.txt
runStage "pubsolr ag"    rdf2solarfuncs.py CHANDRA chandra bib ${MISSIONSTORE}/pubsag.biblist.txt
runStage "pubsolr ah"    rdf2solarfuncs.py CHANDRA chandra bib ${MISSIONSTORE}/pubsah.biblist.txt
runStage "pubsolr ai"    rdf2solarfuncs.py CHANDRA chandra bib ${MISSIONSTORE}/pubsai.biblist.txt
runStage "pubsolr aj"    rdf2solarfuncs.py CHANDRA chandra bib ${MISSIONSTORE}/pubsaj.biblist.txt
runStage "pubsolr ak"    rdf2solarfuncs.py CHANDRA chandra bib ${MISSIONSTORE}/pubsak.biblist.txt
runStage "pubsolr al"    rdf2solarfuncs.py CHANDRA chandra bib ${MISSIONSTORE}/pubsal.biblist.txt
##add stuff for data
echo "# Ending script: `date`" >> $LOGFILE
