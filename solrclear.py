import pysolr
import sys
#SOLR='http://localhost:8983/solr'

if len(sys.argv)==2:
    execfile(sys.argv[1])
elif len(sys.argv)==1:
    execfile("./default.conf")
else:
    print "Usage: python solrclear.py [conffile]"
    sys.exit(-1)
print "SOLR IS", SOLR
conn = pysolr.Solr(SOLR)
conn.delete(q='*:*')
