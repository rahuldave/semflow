#loadfiles
__version__="0.1"
from pysesame import connection
from urllib import quote_plus, urlencode, quote
import os.path, sys, os, glob
import uuid

#c=connection('http://localhost:8081/openrdf-sesame/')
#c.use_repository('testads4')
#context=None
testcodeuristart='<http://ads.harvard.edu/sem/context#'
#DATA="../mast_hut-rdf"

if len(sys.argv)==2:
    execfile("./default.conf")
    execfile("./newmast/default.conf")
elif len(sys.argv)==3:
    execfile(sys.argv[2])
else:
    print "Usage: python mast_propload.py mastmission [conffile]"
    sys.exit(-1)
#c.addnamespace('fb','http://rdf.freebase.com/ns/')
#c.addnamespace('dc','http://purl.org/dc/elements/1.1/')
c=connection(SESAME)
c.use_repository(REPOSITORY)

identifier="prop-"+__file__+"-"+__version__

context=quote_plus(testcodeuristart+identifier+">")
mastmission=sys.argv[1]
filename=DATA+"/"+mastmission+"/proposals."+mastmission+".rdf"
if not os.path.exists(filename):
    print "Path not found: "+filename
    sys.exit(-1)


if os.path.isfile(filename):
    print "PROPLODING", filename
    c.postfile(filename, context)
else:
    "FILE not found: ", filename
