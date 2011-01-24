import getopt
import re
import sys 
from namespaces import *
from urllib import quote_plus
from rdflib import URIRef, Namespace, Literal, BNode
from rdflib import ConjunctiveGraph
import uuid
from lxml import etree as ElementTree
import HTMLParser

import os.path
filetoread=sys.argv[1]
fd=open(filetoread)
stuff=fd.read()
fd.close()

simbad=eval(stuff)
DATA="/home/rdave/semflow/tests/chandrastart"


#file to read is output of simad1.py and assumes bibcode.simbad

for bibcode in simbad.keys():
    listOfObjectsForBibcode=simbad[bibcode]
    for aobject in listOfObjectsForBibcode:
        #print bibcode, aobject['id']
        g = ConjunctiveGraph(identifier=URIRef(None))
        bindgraph(g)
        euri=uri_bib[bibcode]
        eleid=quote_plus("_".join(aobject['id'].split()))
        gadd(g,euri, adsbase.hasAstronomicalSource, uri_base[eleid])
        gadd(g,uri_base[eleid], a, adsbase.AstronomicalSource)
        gadd(g,uri_base[eleid], adsobsv.curatedAt, uri_conf['SIMBAD'])
        gadd(g,uri_base[eleid], adsbase.hasMetadataString, Literal(str(aobject)))
        serializedstuff=g.serialize()
        fd=open(DATA+"/data/rdf/simbad."+quote_plus(bibcode)+".rdf", "w")
        fd.write(serializedstuff)
        fd.close()


