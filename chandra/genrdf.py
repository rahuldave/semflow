import chandra.obsids as obsids
import sys
import os, os.path
from urllib import quote_plus

if len(sys.argv)!=4:
    print "Usage: python chandra/genrdf.py obsv|pub|prop|obsids|propids file-with-list outputdir"
    sys.exit(-1)
    
style=sys.argv[1]
typelist=sys.argv[2]
output=sys.argv[3]
#INCDIR="../AstroExplorer/Missions/Chandra/chandra/"


dafunc={
'obsv':(obsids.getObsFile, 'Datum'),
'pub':(obsids.getPubFile, 'Publications'),
'prop':(obsids.getPropFile, 'Proposal'),
'obsids':(obsids.getObsIdsForPubs,'Publications'),
'propids':(obsids.getPropIdsForObs, 'Datum')
}

if not os.path.exists(output+"/"+style):
    os.makedirs(output+"/"+style)

INCDIR=os.path.dirname(typelist)
INCDIR='..'
for line in open(typelist):
    item=line.strip()+".xml"
    if style=='pub':
        item=quote_plus(item)
    fname=INCDIR+"/chandradata/"+dafunc[style][1]+'/'+item
    print "FNAME=", fname
    outstuff=dafunc[style][0](fname)
    #getPubFile(sys.argv[1])
    if style in ['obsv', 'pub', 'prop']:
        #print output
        ofname=output+"/"+style+"/"+item+".rdf"
        print "OFNAME",ofname
        fd=open(ofname, "w")
        fd.write(outstuff)
        fd.close()
        
