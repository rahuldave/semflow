#loadfiles
__version__="0.1"
from pysesame import connection
from urllib import quote_plus, urlencode, quote
import os.path, sys
import uuid

#c=connection('http://localhost:8081/openrdf-sesame/')
#c.use_repository('testads4')
#context=None
testcodeuristart='<http://ads.harvard.edu/sem/context#'
#DATA="../chandra-rdf"
#DATA="../mast_hut-rdf"

#c.addnamespace('fb','http://rdf.freebase.com/ns/')
#c.addnamespace('dc','http://purl.org/dc/elements/1.1/')
import os.path, sys, os, glob

#identifier=str(uuid.uuid4())+"-"+__file__+"-"+__version__
if len(sys.argv)==2:
    execfile("./default.conf")
elif len(sys.argv)==3:
    execfile(sys.argv[2])
else:
    print "Usage: python loadfiles-simbad.py biblist [conffile]"
    sys.exit(-1)
    
c=connection(SESAME)
c.use_repository(REPOSITORY)
identifier='publications-'+__file__    
context=quote_plus(testcodeuristart+identifier+">")
bibcodes=[quote_plus(ele.strip()) for ele in open(sys.argv[1]).readlines()]
print bibcodes
if not os.path.exists(DATA+"/data/rdf"):
    print "Path not found"
    sys.exit(-1)
for ele in bibcodes:
    filename=DATA+"/data/rdf"+"/"+ele+".xml"
    if os.path.isfile(filename):
        print filename
        c.postfile(filename, context)
    else:
        "FILE not found: ", filename
