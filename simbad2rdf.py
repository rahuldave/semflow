import getopt
import re
import sys 
from namespaces import *
from urllib import quote_plus
from rdflib import URIRef, Namespace, Literal, BNode
from rdflib import ConjunctiveGraph
import uuid
#from lxml import etree as ElementTree
import HTMLParser
import os.path


"""
{
    '1999ApJ...522..718Q': [
        {'mtype': '~,~,~', 'otype': 'LINER ~', 'refcode': '1999ApJ...522..718Q', 'ra': '184.84673421', '_raw': 'NGC  4261|184.84673421|+05.82491522|LINER ~|~,~,~|E...,D,~', 'dec': '+05.82491522', 'id': 'NGC  4261'}, 
        {'mtype': '~,~,~', 'otype': 'Seyfert_2 ~', 'refcode': '1999ApJ...522..718Q', 'ra': '186.26559721', '_raw': 'M  84|186.26559721|+12.88698314|Seyfert_2 ~|~,~,~|E...,D,~', 'dec': '+12.88698314', 'id': 'M  84'}, 
        {'mtype': '~,~,~', 'otype': 'GinGroup ~', 'refcode': '1999ApJ...522..718Q', 'ra': '193.092133', '_raw': 'NGC  4753|193.092133|-01.199689|GinGroup ~|~,~,~|I...,D,~', 'dec': '-01.199689', 'id': 'NGC  4753'}, 
        {'mtype': '~,~,~', 'otype': 'Seyfert_2 ~', 'refcode': '1999ApJ...522..718Q', 'ra': '201.36506279', '_raw': 'NGC  5128|201.36506279|-43.01911258|Seyfert_2 ~|~,~,~|E,D,~', 'dec': '-43.01911258', 'id': 'NGC  5128'}
    ]
}
"""
if len(sys.argv)<2 or len(sys.argv)> 3:
    print "Usage: python simbad2rdf.py dictfile [targetdir]"
    sys.exit(-1)

filetoread=sys.argv[1]
fd=open(filetoread)
stuff=fd.read()
fd.close()

simbad=eval(stuff)

if len(sys.argv)==3:
    DATA=sys.argv[2]
else:
    DATA="../chandra-rdf"
    
    
#DATA="../mast_hut-rdf"

#dabib='2005ApJ...629..700N'

##file to read is output of simad1.py and assumes bibcode.simbad
#print "SIMBAD", simbad[dabib]
#sys.exit(-1)

#Issue, some sources will come again and again and have multiple metadata strings. I think this is fine
#as the triplestore will kill repeated triples. But what if they come in different contexts. Wont we #have multiple statements then. I think we can deal with that but it is something to remember.

for bibcode in simbad.keys():
    listOfObjectsForBibcode=simbad[bibcode]
    g = ConjunctiveGraph(identifier=URIRef(None))
    bindgraph(g)
    for aobject in listOfObjectsForBibcode:
        #print bibcode, aobject['id']
        euri=uri_bib[bibcode]
        eleid=quote_plus("_".join(aobject['id'].split()))
        gadd(g,euri, adsbase.hasAstronomicalSource, uri_source[eleid])
        gadd(g,uri_source[eleid], a, adsbase.AstronomicalSource)
        gadd(g,uri_source[eleid], adsbase.name , Literal(aobject['id']))
        gadd(g,uri_source[eleid], adsobsv.curatedAt, uri_conf['SIMBAD'])
        gadd(g,uri_source[eleid], adsbase.hasMetadataString, Literal(str(aobject)))
        
    serializedstuff=g.serialize()
    fd=open(DATA+"/data/rdf/simbad."+quote_plus(bibcode)+".rdf", "w")
    fd.write(serializedstuff)
    fd.close()


