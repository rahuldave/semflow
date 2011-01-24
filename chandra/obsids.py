#reading chandra observation files

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

def _xmlcharref_encode(unicode_data, encoding="ascii"):
    """Emulate Python 2.3's 'xmlcharrefreplace' encoding error handler."""
    chars = []
    # Step through the unicode_data string one character at a time in
    # order to catch unencodable characters:
    for char in unicode_data:
        try:
            chars.append(char.encode(encoding, 'strict'))
        except UnicodeError:
            chars.append('\u%04X' % ord(char))
    return ''.join(chars)


class XMLObj:
    def __init__(self, rec):
        self.rec = rec

    def __getitem__(self, key):
        return self.elementText(key)

    def __getattr__(self, key):
        return self.elementText(key)

    def elementText(self, elem, node=None):
        if not node:
            node = self.rec
        try:
            return node.find(elem).text 
        except:
            print >>sys.stderr, "%s not found" % elem

    def elementAttribute(self, elem, attr, node=None):
        if not node:
            node = self.rec
        try:
            return node.find(elem).attrib[attr]
        except:
            print >>sys.stderr, \
            "failed to get %s attribute value from %s element" % (attr, elem)


def getObsFile(fname):
    g = ConjunctiveGraph(identifier=URIRef(ads_baseurl))
    bindgraph(g)
    recordstree=ElementTree.parse(fname)
    rootnode=recordstree.getroot()
    xobj=XMLObj(recordstree)
    trec={}
    trec['obsname']=rootnode.attrib['name']
    trec['obsid']=rootnode.attrib['obsid']
    trec['instrument_name']=xobj.elementAttribute('instrument', 'name')
    trec['obsvtype']=xobj.type
    trec['time']=xobj.observed_time
    trec['date']=xobj.start_date
    trec['ra']=xobj.ra
    trec['dec']=xobj.dec
    trec['proposal_id']=xobj.elementAttribute('proposal', 'id')
    #print trec
    obsuri=uri_obs['CHANDRA_'+trec['obsid']]
    daturi=uri_dat['CHANDRA_'+trec['obsid']]
    gadd(g, daturi, a, adsobsv.Datum)
    gadd(g, obsuri, a, adsobsv.SimpleObservation)
    gdadd(g, obsuri, [
            adsobsv.observationId, Literal(trec['obsid']),
            adsobsv.observationType, Literal(trec['obsvtype']),
            adsbase.atTime, Literal(trec['date']),
            adsobsv.observedTime, Literal(trec['time']),
            adsbase.atObservatory, uri_conf['OBSERVATORY_CHANDRA'],
            adsobsv.atTelescope,   uri_conf['TELESCOPE_CHANDRA'],
            adsbase.usingInstrument, uri_conf['INSTRUMENT_CHANDRA_'+trec['instrument_name']],
            adsobsv.hasDatum, daturi,
            adsbase.asAResultOfProposal, uri_prop['CHANDRA_'+trec['proposal_id']]
        ]
    )
    gdadd(g, daturi, [
            adsobsv.dataProductId, Literal(trec['obsid']),
            adsobsv.forSimpleObservation, obsuri
        ]
    )
    gdbnadd(g, obsuri, adsobsv.associatedPosition, [
            a, adsobsv.Pointing,
            adsobsv.ra, Literal(trec['ra']),
            adsobsv.dec, Literal(trec['dec'])
        ]
    )
    serializedstuff=g.serialize(format='xml')
    return serializedstuff
    
def getPubFile(fname):
    g = ConjunctiveGraph(identifier=URIRef(ads_baseurl))
    bindgraph(g)
    recordstree=ElementTree.parse(fname)
    rootnode=recordstree.getroot()
    xobj=XMLObj(recordstree)
    trec={}
    trec['bibcode']=xobj.bibcode
    trec['classified_by']=xobj.classified_by
    #this above coild also be figured by bibgroup
    #shouldnt this be a curated statement. But what is the curation. Not a source curation
    #later.
    trec['paper_type']=xobj.paper_type
    #trec['obsids']=[e.text for e in xobj.rec.findall('data')[0].findall('obsid')]
    boolobsids=False
    if len(xobj.rec.findall('data'))> 0:
        if len(xobj.rec.findall('data')[0].findall('obsid'))> 0:
            print "1"
            trec['obsids']=[e.text for e in xobj.rec.findall('data')[0].findall('obsid')]
            boolobsids=True
    else:
        print "2"
        trec['obsids']=[]
    #print trec
    bibcode_uri = uri_bib[trec['bibcode']]
    print bibcode_uri
    for obsid in trec['obsids']:
        obsuri=uri_obs['CHANDRA_'+obsid]
        daturi=uri_dat['CHANDRA_'+obsid]
        gadd(g, bibcode_uri, adsbase.aboutScienceProcess, obsuri)
        gadd(g, bibcode_uri, adsbase.aboutScienceProduct, daturi)
        gadd(g, bibcode_uri, adsobsv.datum_p, Literal(str(boolobsids).lower()))
        #This is temporary. must map papertype to scienceprocesses and use those ones exactly
        gadd(g, bibcode_uri, adsbib.paperType, Literal(trec['paper_type']))
        
    serializedstuff=g.serialize(format='xml')
    return serializedstuff

def getObsIdsForPubs(fname):
    recordstree=ElementTree.parse(fname)
    rootnode=recordstree.getroot()
    xobj=XMLObj(recordstree)
    trec={}
    trec['bibcode']=xobj.bibcode
    #print trec['bibcode']
    
    if len(xobj.rec.findall('data'))> 0:
        if len(xobj.rec.findall('data')[0].findall('obsid'))> 0:
            trec['obsids']=[e.text for e in xobj.rec.findall('data')[0].findall('obsid')]
            for ele in trec['obsids']:
                print trec['bibcode'], ele
    else:
        print trec['bibcode'], "NOTHING"
    
def getPropFile(fname):
    g = ConjunctiveGraph(identifier=URIRef(ads_baseurl))
    bindgraph(g)
    recordstree=ElementTree.parse(fname)
    rootnode=recordstree.getroot()
    xobj=XMLObj(recordstree)
    trec={}
    trec['propname']=rootnode.attrib['name']
    trec['propid']=rootnode.attrib['id']
    trec['title']=xobj.title
    trec['category']=xobj.category
    #we used a proposalType here, as this is somewhat different from justscienceprocess. add to ontology
    trec['abstract']=xobj.abstract
    trec['pi']=[xobj.elementAttribute('pi', 'last'),xobj.elementAttribute('pi', 'first')]
    #print trec
    propuri=uri_prop['CHANDRA_'+trec['propid']]
    #This is FALSE. TODO..fix to ads normed name or lookitup How? Blanknode? WOW.
    qplabel=trec['pi'][0]+'_'+trec['pi'][1]
    auth_uri = uri_agents[qplabel]
    gadd(g, propuri, a, adsbase.ObservationProposal)
    gdadd(g, propuri, [
            adsobsv.observationProposalId, Literal(trec['propid']),
            adsobsv.observationProposalType, Literal("CHANDRA/"+trec['category']),
            adsbase.principalInvestigator, auth_uri,
            adsbase.title, Literal(trec['title'])
        ]
    )
    serializedstuff=g.serialize(format='xml')
    return serializedstuff

def getPropIdsForObs(fname):
    recordstree=ElementTree.parse(fname)
    rootnode=recordstree.getroot()
    xobj=XMLObj(recordstree)
    trec={}
    trec['obsid']=rootnode.attrib['obsid']
    trec['proposal_id']=xobj.elementAttribute('proposal', 'id')
    print trec['obsid'],trec['proposal_id']
    
dafunc={
'obsv':getObsFile,
'pub':getPubFile,
'prop':getPropFile,
'obsids':getObsIdsForPubs,
'propids':getPropIdsForObs
}    
if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[2] in dafunc.keys():
        #getObsFile(sys.argv[1])
        import os.path
        fname=sys.argv[1]
        bname=os.path.basename(fname)
        style=sys.argv[2]
        ofname="tests/chandrastart/"+style+"/"+bname+".rdf"
        output=dafunc[style](fname)
        #getPubFile(sys.argv[1])
        if style in ['obsv', 'pub', 'prop']:
            fd=open(ofname, "w")
            fd.write(output)
            fd.close()
    else:
        print "Worong usage", sys.argv
        sys.exit(-1)
