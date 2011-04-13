#loadfiles
__version__="0.1"
from pysesame import connection
from urllib import quote_plus, urlencode, quote
import os.path, sys, os, glob
import uuid
import rdflib
#c=connection('http://localhost:8081/openrdf-sesame/')
#c.use_repository('testads4')
#context=None
testcodeuristart='<http://ads.harvard.edu/sem/context#'
#DATA="../mast_hut-rdf"

if len(sys.argv)==2:
    execfile("./default.conf")
    execfile("./mast/default.conf")
elif len(sys.argv)==3:
    execfile(sys.argv[2])
else:
    print "Usage: python loadfiles-hut-obsv.py obsvfilepatternfile[conffile]"
    sys.exit(-1)
#c.addnamespace('fb','http://rdf.freebase.com/ns/')
#c.addnamespace('dc','http://purl.org/dc/elements/1.1/')
c=connection(SESAME)
c.use_repository(REPOSITORY)

identifier=str(uuid.uuid4())+"-"+__file__+"-"+__version__

context=quote_plus(testcodeuristart+identifier+">")
obstr=open(sys.argv[1]).read()
obsdict=eval(obstr).keys()
obsfiles=[str(k).split("/")[-1] for k in obsdict]
print obsfiles
for ele in obsfiles:
    filename=DATA+"/obscore.hut.psv."+ele+".rdf"
    #print filename
    if os.path.isfile(filename):
        print filename
        c.postfile(filename, context)
    else:
        "FILE not found: ", filename
