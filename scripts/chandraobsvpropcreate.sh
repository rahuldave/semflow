#!/bin/bash

PARENT=Chandra
MISSION=chandra
LOGFILE=../${MISSION}.log
RDFSTORE=../chandra-rdf
MISSIONSTORE=../AstroExplorer/Missions/${PARENT}/${MISSION}/

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

runStage "obsvrdf"      chandra/genrdf.py obsv ${MISSIONSTORE}/global.obsids.txt $RDFSTORE/
runStage "proprdf"      chandra/genrdf.py prop ${MISSIONSTORE}/global.proposals.txt $RDFSTORE/
echo "# Ending script: `date`" >> $LOGFILE
