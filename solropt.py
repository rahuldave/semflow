"""
Tell Solr to optimize itself. This is mainly useful to consolidate
the index files so that the number of open files is kept low. It is
not intended as a search optimization, but may have some bearing on
the results.
"""

import pysolr
import sys
#SOLR='http://localhost:8983/solr'

if len(sys.argv)==2:
    execfile(sys.argv[1])
elif len(sys.argv)==1:
    execfile("./default.conf")
else:
    print "Usage: python solropt.py [conffile]"
    sys.exit(-1)
print "SOLR IS", SOLR
conn = pysolr.Solr(SOLR)
conn.optimize()

