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
#DATA="../chandra-rdf"

if len(sys.argv)==3:
    execfile("./default.conf")
    execfile("./chandra/default.conf")
elif len(sys.argv)==4:
    execfile(sys.argv[3])
else:
    print "Usage: python loadfiles-prop.py bibfile proprdfdir [conffile]"
    sys.exit(-1)
#c.addnamespace('fb','http://rdf.freebase.com/ns/')
#c.addnamespace('dc','http://purl.org/dc/elements/1.1/')
c=connection(SESAME)
c.use_repository(REPOSITORY)

identifier=str(uuid.uuid4())+"-"+__file__+"-"+__version__

context=quote_plus(testcodeuristart+identifier+">")
propids=[ele.strip() for ele in open(sys.argv[1]).readlines()]
print propids
if not os.path.exists(DATA+sys.argv[2]):
    print "Path not found"
    sys.exit(-1)
for ele in propids:
    filename=DATA+sys.argv[2]+"/"+ele+".xml.rdf"
    if os.path.isfile(filename):
        print filename
        c.postfile(filename, context)
    else:
        "FILE not found: ", filename
