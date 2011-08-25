#!/bin/bash

PARENT=Chandra
MISSION=chandra
LOGFILE=../${MISSION}.log
RDFSTORE=../chandra-rdf
MISSIONSTORE=../AstroExplorer/Missions/${PARENT}/${MISSION}
BIBLISTA=${MISSIONSTORE}/sherry.p.a.biblist.txt
BIBLISTB=${MISSIONSTORE}/hutoverlap.biblist.txt

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

runStage "adsrdf a"     adsclassic2rdf.py $RDFSTORE ${BIBLISTA}
runStage "adsrdf b"     adsclassic2rdf.py $RDFSTORE ${BIBLISTB}
runStage "simbadrdf a"  simbad2rdf.py ${MISSIONSTORE}/sherry.p.a.simbad.dict $RDFSTORE
runstage "simbadrdf b"  simbad2rdf.py ${MISSIONSTORE}/hutoverlap.simbad.dict $RDFSTORE
runStage "pubrdf a"     chandra/genrdf.py pub ${MISSIONSTORE}/sherry.p.a.linkedpubs.txt $RDFSTORE/
runStage "pubrdf b"     chandra/genrdf.py pub ${MISSIONSTORE}/hutoverlap.linkedpubs.txt $RDFSTORE/
runStage "obsvrdf"      chandra/genrdf.py obsv ${MISSIONSTORE}/global.obsids.txt $RDFSTORE/
runStage "proprdf"      chandra/genrdf.py prop ${MISSIONSTORE}/global.proposals.txt $RDFSTORE/
runStage "adsload a"    loadfiles.py ${BIBLISTA}
runStage "adsload b"    loadfiles.py ${BIBLISTB}
runStage "simbadload a" loadfiles-simbad.py ${BIBLISTA}
runStage "simbadload b" loadfiles-simbad.py ${BIBLISTB}
runStage "pubload a"    chandra/loadfiles.py ${MISSIONSTORE}/sherry.p.a.linkedpubs.txt pub
runStage "pubload b"    chandra/loadfiles.py ${MISSIONSTORE}/hutoverlap.linkedpubs.txt pub
runStage "obsvload"     chandra/loadfiles.py ${MISSIONSTORE}/global.obsids.txt obsv
runStage "propload"     chandra/loadfiles.py ${MISSIONSTORE}/global.proposals.txt prop

#We had to produce a cut file below due to some linkage probs in Chandra
runStage "pubsolr a"    rdf2solr5.py CHANDRA chandra ${BIBLISTA}.cut 
runStage "pubsolr b"    rdf2solr5.py CHANDRA chandra ${BIBLISTB}

echo "# Ending script: `date`" >> $LOGFILE
