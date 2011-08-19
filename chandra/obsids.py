#reading chandra observation files

#Bug: we should have test asserts for the data files in our workflow to make sure they follow some logic

import getopt
import re
import sys 
from namespaces import *
from urllib import quote_plus
from rdflib import URIRef, Namespace, Literal, BNode
from rdflib import ConjunctiveGraph
import uuid
try:
    from lxml import etree as ElementTree
except:
    from xml.etree import ElementTree
import HTMLParser


#DATA="../chandra-rdf"

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


def getObsURI(obsid, fragment=None):
    if fragment:
        return uri_obs['CHANDRA/obsid/'+obsid+"/"+fragment]
    return uri_obs['CHANDRA/obsid/'+obsid]
    
def getDatURI(obsid, fragment=None):
    if fragment:
        return uri_dat['CHANDRA/obsid/'+obsid+"/"+fragment]
    return uri_dat['CHANDRA/obsid/'+obsid]
    
def getPropURI(propid):
    return uri_prop['CHANDRA/propid/'+propid]
    
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
    trec['created_time']=xobj.public_avail
    #Bug: in some of Sherry's stuff this is null
    #print "Created",trec['created_time']
    trec['date']=xobj.start_date
    trec['ra']=xobj.ra
    trec['dec']=xobj.dec
    trec['proposal_id']=xobj.elementAttribute('proposal', 'id')
    #print trec
    obsuri=getObsURI(trec['obsid'])
    daturi=getDatURI(trec['obsid'], fragment="I")
    daturi2=getDatURI(trec['obsid'], fragment="S")
    gadd(g, daturi, a, adsobsv.Datum)
    gadd(g, daturi2, a, adsobsv.Datum)
    gadd(g, obsuri, a, adsobsv.SimpleObservation)
    #Connect the data product and the observation
    access_url="http://cda.harvard.edu/chaser/ocatList.do?obsid="+trec['obsid']
    gdadd(g, daturi, [
            adsobsv.dataProductId, Literal(trec['obsid']+"/I"),
            adsobsv.forSimpleObservation, obsuri,
            adsobsv.dataURL, URIRef(access_url)
        ]
    )
    gdadd(g, daturi2, [
            adsobsv.dataProductId, Literal(trec['obsid']+"/S"),
            adsobsv.forSimpleObservation, obsuri,
            adsobsv.dataURL, URIRef(access_url)
        ]
    )
    addVals(g, daturi,
            [
                
                adsobsv.calibLevel, 2, asInt,

                adsbase.dataType, "image", Literal,
            ]
    )
    #These are untrue anyway: creation time is not public time, but we are using it now.
    if trec['created_time']!=None:
        addVals(g, daturi, [pav.createdOn, trec['created_time'], asDateTime('%b %d %Y %H:%M%p')])
        addVals(g, daturi2, [pav.createdOn, trec['created_time'], asDateTime('%b %d %Y %H:%M%p')])
    addVals(g, daturi2,
            [
                adsobsv.calibLevel, 2, asInt,

                adsbase.dataType, "spectra", Literal,
            ]
    )
    tname = trec['obsname'].strip()
    gdadd(g, obsuri, [
            adsobsv.observationId, Literal(trec['obsid']),
            adsobsv.observationType, Literal(trec['obsvtype']),
            adsbase.atObservatory, uri_infra['observatory/CHANDRA'],
            adsobsv.atTelescope,   uri_infra['telescope/CHANDRA'],
            adsbase.usingInstrument, uri_infra['instrument/CHANDRA_'+trec['instrument_name']],
            adsobsv.hasDatum, daturi,
            adsobsv.hasDatum, daturi2,
            adsbase.title, Literal(tname),
            adsbase.asAResultOfProposal, getPropURI(trec['proposal_id'])
        ]
    )
    #fstring: Sep 17 2000  8:01PM %b %d %Y %H:%M%p
    emmin=0.1e-10
    emmax=100e-10
    addVals(g, obsuri, [
            adsbase.atTime, trec['date'], asDateTime('%b %d %Y %H:%M%p'),
            adsobsv.observedTime, float(trec['time'])*1000, asDuration,
            adsobsv.tExptime, float(trec['time'])*1000, asDouble,
            adsobsv.wavelengthStart, emmin, asDouble,
            adsobsv.wavelengthEnd, emmax, asDouble,
        ]
    )
    
    
    if tname != '':
        tnameuri = uri_target["CHANDRA/"+quote_plus(tname)]

        gadd(g, obsuri, adsbase.target, tnameuri)
        addVals(g, tnameuri,
                [
                    a, adsobsv.AstronomicalSourceName, None,
                    adsbase.name, tname, Literal,
                    ])
                    
    for domain in getEMDomains(float(emmin), float(emmax)):
        addVal(g, obsuri, adsobsv.wavelengthDomain, domain)
    
    print "RA?DEC", trec['ra'], trec['dec']
    if trec['ra'] !=None and trec['dec'] != None:    
        gdbnadd(g, obsuri, adsobsv.associatedPosition, [
            a, adsobsv.Pointing,
            adsobsv.ra, asDouble(trec['ra']),
            adsobsv.dec, asDouble(trec['dec'])
            ]
        )
    
    
    #should this be under uri_agents or collaboration instead?
    #the typing for this should be done in a conf file
    cnameuri = uri_conf["project/CHANDRA"]
    gadd(g, obsuri, adsobsv.observationMadeBy, cnameuri)
#    gdadd(graph, cnameuri, [ This stuff is thought off as configuration
#            a, adsbase.Project,
#            agent.fullName, Literal(cname)
#    ])
    serializedstuff=g.serialize(format='xml')
    return serializedstuff
    
def getPubFile(fname):

    # Do we really need to create one per file? Could be
    # cached/made global but leave that for later if it
    # ever is determined to be a problem.
    #
    hparser = HTMLParser.HTMLParser()
    
    g = ConjunctiveGraph(identifier=URIRef(ads_baseurl))
    bindgraph(g)
    recordstree=ElementTree.parse(fname)
    rootnode=recordstree.getroot()
    xobj=XMLObj(recordstree)
    trec={}
    trec['bibcode']=xobj.bibcode

    # Change by Doug:
    # It looks like the bibcode elements have been percent encoded
    # in the input XML files - e.g.
    #
    #cat ../chandradata/Publications/2000A%26A...359..489C.xml
    # <paper>
    #  <bibcode>2000A%26A...359..489C</bibcode>
    #  <classified_by>CDA</classified_by>
    #  <paper_type>science</paper_type>
    #  <flags>
    #      <data_use>indirect</data_use>
    #      <multi_observatory />
    #      <followup />
    #  </flags>
    # </paper>
    #
    # so we have to decode it here.
    #
    trec['bibcode'] = hparser.unescape(trec['bibcode'])
    
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
    gadd(g, bibcode_uri, adsbib.paperType, Literal(trec['paper_type']))
    print bibcode_uri
    if len(trec['obsids'])>0:
        gadd(g, bibcode_uri, adsobsv.datum_p, Literal(str(boolobsids).lower()))
    for obsid in trec['obsids']:
        obsuri=getObsURI(obsid)
        daturi=getDatURI(obsid)
        #obsuri=uri_obs['CHANDRA_'+obsid]
        #daturi=uri_dat['CHANDRA_'+obsid]
        gadd(g, bibcode_uri, adsbase.aboutScienceProcess, obsuri)
        gadd(g, bibcode_uri, adsbase.aboutScienceProduct, daturi)
        
        #This is temporary. must map papertype to scienceprocesses and use those ones exactly
        
        
    serializedstuff=g.serialize(format='xml')
    return serializedstuff

def getObsIdsForPubs(fname):
    recordstree=ElementTree.parse(fname)
    rootnode=recordstree.getroot()
    xobj=XMLObj(recordstree)
    trec={}
    trec['bibcode']=xobj.bibcode
    raise NotImplementedError("Unsure whether bibcode={0} needs to be HTML unescaped here so exiting.".format(xobj.bibcode))

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
    propuri=getPropURI(trec['propid'])
    #This is FALSE. TODO..fix to ads normed name or lookitup How? Blanknode? WOW.
    qplabel=trec['pi'][0]+'_'+trec['pi'][1]
    fullname=trec['pi'][0]+', '+trec['pi'][1]
    auth_uri = uri_agents["PersonName/"+qplabel+"/"+str(uuid.uuid4())]
    gdadd(g, auth_uri, [
            a, agent.PersonName,
            agent.fullName, Literal(fullname)
            ])
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
    if len(sys.argv)==3 or len(sys.argv)==4 and sys.argv[2] in dafunc.keys():
        #getObsFile(sys.argv[1])
        import os.path
        fname=sys.argv[1]
        bname=os.path.basename(fname)
        style=sys.argv[2]
        if len(sys.argv)==4:
            execfile(sys.argv[3])
        else:
            execfile("./chandra/default.conf")
        ofname=DATA+"/"+style+"/"+bname+".rdf"
        print "----------------------"
        output=dafunc[style](fname)
        print "OFNAME",ofname
        #getPubFile(sys.argv[1])
        if style in ['obsv', 'pub', 'prop']:
            #print output
            fd=open(ofname, "w")
            fd.write(output)
            fd.close()
    else:
        print "Usage: python obsids.py xmlfile obsv|pub|prop|obsids|propids [conffile]"
        sys.exit(-1)
