#!/usr/bin/env python

__version__=0.01

"""Module docstring....
Usage: adsclassic2rdf.py bibcodefile [format]
"""

import getopt
import re
import sys
import os, os.path
from namespaces import *
from urllib import quote_plus
from rdflib import URIRef, Namespace, Literal, BNode
from rdflib import ConjunctiveGraph
import uuid
import getuuid4bibcode
try:
    from lxml import etree as ElementTree
except:
    from xml.etree import ElementTree
import HTMLParser

DATA="../mast_hut-rdf"
DATA="../chandra-rdf"
SORTEDYEARLIST='../AstroExplorer/filebibs/sortedyearlist.txt'

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


class RecordObj:
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

    def getauthors(self):
        return self.rec.findall('author')

    def getreferences(self):
        return self.rec.findall('reference')

    def getlinks(self):
        return self.rec.findall('link')

    #make faster by cacheing affiliations
    def getaffiliations(self, authornode):
        afillist=[]
        for node in authornode.findall('affiliations'):#only 1 per author
            afilnodes=node.findall('affiliation')
            for n in afilnodes:
                afillist.append(n.text)
        return afillist
        
    #make faster by cacheing affiliations
    def getemails(self, authornode):
        afillist=[]
        for node in authornode.findall('emails'):#only 1 per author
            afilnodes=node.findall('email')
            for n in afilnodes:
                afillist.append(n.text)
        return afillist

    def getkeywords(self):
        for node in self.rec.findall('keywords'):
            if node.attrib['type'] == 'Normalized':
                return node.findall('keyword')
        return []
                
    def getarxivchannel(self):
        "this is called when there is only an arxiv record and not anything else"
        for node in self.rec.findall('keywords'):
            if node.attrib['type'] == 'arXiv':
                achan=node.findall('keyword')[0]
                return achan.attrib['channel']
        return []


        

#stuff like ADS should be inited from the database.
def record_meta(g, incuuid, record):
    import datetime
    thetime=datetime.datetime.today().isoformat()
    theuuid=incuuid
    #meta_uri = uri_meta[record.bibcode]
    meta_uri = uri_meta[theuuid]
    bibcode_uri = uri_bib[record.bibcode]
    #ads='ADS'
    #ads_uri = uri_conf['ADS']
    adsrdfagent_uri = uri_agents["Software/"+__file__+"-"+str(__version__)]
    #gadd(g, ads_uri, a, adsbib.Aggregator)
    gadd(g, meta_uri, a, fabio.BibliographicMetadata)
    gadd(g, meta_uri, a, fabio.EntityMetadata)
    gadd(g, meta_uri, pav.importedFromSource, uri_conf['ADS'])
    gadd(g, meta_uri, pav.importedBy, adsrdfagent_uri)
    gadd(g, meta_uri, pav.importedOn, Literal(thetime,datatype="xsd:dateTime"))
    gadd(g, meta_uri, pav.lastUpdateOn, Literal(thetime,datatype="xsd:dateTime"))
    return theuuid

def work_meta(g,record, theuuid):
    #bibcode_uri = uri_bib[record.bibcode]
    #Replace above by uuid
    print "????", record.bibcode
    work_uri=uri_bib[theuuid]
    ads_uri = uri_conf['ADS']
    gbuild(g,   [work_uri, a, fabio.ResearchPaper,
                work_uri, a, adsbase.WrittenProduct,
                work_uri, adsbase.title, Literal(record.title),
	            work_uri, adsbase.languageIn, Literal("en")#is this in records?
	            ]
    )
    if int(record.rec.attrib['refereed'])==1:
        gadd(g, work_uri, cito.peerReviewed, Literal(True, datatype='xsd:boolean'))
    else:
        gadd(g, work_uri, cito.peerReviewed, Literal(False, datatype='xsd:boolean'))
        
    gadd(g, work_uri, adsbib.citeMeAs, Literal(record.journal))
    gadd(g, work_uri, adsbib.workIdentifier, Literal(record.bibcode))
    #gdadd(g, bibcode_uri,[
    #    cito.peerReviewed, Literal(True, datatype='xsd:boolean') , # peer review status  
	#    adsbib.workIdentifier, Literal(record.bibcode)
    #])
    gdbnadd(g, work_uri, adsbib.hasAbstract,[
        a, fabio.Abstract,
        adsbib.abstractText, Literal(record['abstract'])
    ])
    
    #gadd(g, work_uri, adsbib.citeMeAs, Literal(record.journal))


def expr_meta(g, record, theuuid):
    work_uri=uri_bib[theuuid]
    bibcode_uri = uri_bib[record.bibcode]
    #need to handle more possibilities here, like at the arxiv stage only
#    if record['DOI']:
#        #expression_uri = quote_plus(uri_bib[record.DOI])
#        expression_uri =  '_'.join(uri_bib[record.DOI].split('/'))
#    else:
#        expression_uri=bibcode_uri
    expression_uri=bibcode_uri
    #hardcoded AJ until we have the publication finder ready
    if int(record.rec.attrib['refereed'])==1:
        endnum=record.bibcode[4:9].find('.')
        if endnum==-1:
            endnum=5
        jsource=record.bibcode[4:4+endnum]#giovanni method
        #will fail on monographs
        gdadd(g, expression_uri, [
            a, fabio.JournalArticle,
            adsbib.publishedIn, uri_conf[jsource],
            adsbib.volume, Literal(record.volume),
            adsbib.pageStart, Literal(record.page),
            fabio.isRealizationOf, work_uri,
        ])
    else:#either we are arxiv or we are something like ADASS or AAS.
        print "For "+record.bibcode+ " expression is EPRINT"
        channel=record.getarxivchannel()
        if len(channel) >0:
            gdadd(g, expression_uri, [
                a, cito.Eprint,
                adsbib.publishedIn, uri_conf['ARXIV'],
                adsbib.channel, Literal(channel),
                adsbib.eprintid, Literal(record.preprintid),
                adsbib.volume, Literal(record.volume),
                adsbib.pageStart, Literal(record.page),
                fabio.isRealizationOf, work_uri,
            ])
        else:#this is a non-arxiv'ed, non refereed paper, eg AAS/ADASS with no arxiv'
            #thus assume unrefereed but journal
            endnum=record.bibcode[4:9].find('.')
            if endnum==-1:
                endnum=5
            jsource=record.bibcode[4:4+endnum]#giovanni method
            gdadd(g, expression_uri, [
                a, fabio.JournalArticle,
                adsbib.publishedIn, uri_conf[jsource],
                adsbib.volume, Literal(record.volume),
                adsbib.pageStart, Literal(record.page),
                fabio.isRealizationOf, work_uri,
            ])
    if record['DOI']:
        print '-----DOI------'
        gadd(g,expression_uri, adsbib.doi, Literal(record.DOI))
        #gadd(g,expression_uri, '_'.join(adsbib.doi.split('/')), Literal(record.DOI))
    if record['lastpage']:
        gadd(g,expression_uri, adsbib.pageEnd, Literal(record.lastpage))
    gadd(g, expression_uri, adsbib.pubDate, Literal(record.pubdate, datatype="xsd:date"))
    #lots more metadata and pav stuff needed. ask edwin.BUG above use asDateTime for this
    return expression_uri

def expr_eprint_meta(g, record, theuuid, maine=None):
    bibcode_uri = uri_bib[record.bibcode]
    work_uri=uri_bib[theuuid]
    #expression_uri=URIRef('http://arxiv.org/%s' %record.preprintid)
    expression_uri=uri_bib[record.elementAttribute('preprintid', 'ecode')]
    #hardcoded AJ until we have the publication finder ready
    print "in eem", expression_uri
    gdadd(g, expression_uri, [
        a, adsbib.Eprint,
        adsbib.publishedIn, uri_conf['ARXIV'],
        adsbib.eprintid, Literal(record.preprintid),
        fabio.isRealizationOf, work_uri,
    ])
    # adsbib.channel, Literal("astro-ph"),
    if maine:
        gadd(g, expression_uri, adsbib.alsoPublishedIn, maine)
        gadd(g, maine, adsbib.alsoHasEprint, expression_uri)
    return expression_uri

def work_expr_meta(g, record, ex, theuuid):
    bibcode_uri = uri_bib[record.bibcode]
    work_uri=uri_bib[theuuid]
    gdbnadd(g, work_uri, adsbib.hasAggregation,[
        a, adsbib.Aggregation,
        adsbib.aggregatedAt, uri_conf['ADS'],
	    adsbib.bibcode, Literal(record.bibcode),
	    adsbib.hasExpression, ex[0],

	])
    #will aggregation always have first expression?
    #ADS pubdates lack the depth our example has..what should we do?
    gadd(g, work_uri, adsbib.defaultRealizedThrough, ex[0])

def do_keywords(g, record, theuuid):
    bibcode_uri = uri_bib[record.bibcode]
    work_uri=uri_bib[theuuid]
    kwtext='';
    for kw in record.getkeywords():
        if kw.text:
            label = kw.text
            kwtext=kwtext+label+", "
            qplabel='_'.join(quote_plus(label).split('+'))
            kw_uri=normalizedkeys[qplabel]
            gadd(g, work_uri, adsbib.keywordConcept, kw_uri)
    kwtext=kwtext[:-2]
    gadd(g, work_uri, adsbib.keywordText, Literal(kwtext))

def do_authors(g, record, theuuid):
    bibcode_uri = uri_bib[record.bibcode]
    work_uri=uri_bib[theuuid]
    acount=1
    for author in record.getauthors():
        authnamenode=author.findall('name')[0]
        auth_fname=authnamenode.findall('western')[0].text
        auth_name=authnamenode.findall('normalized')[0].text
        qplabel='_'.join(quote_plus(auth_name).split('+'))
        auth_uri = uri_agents["PersonName/"+qplabel+"/"+str(uuid.uuid4())]
        gadd(g, auth_uri, a, agent.PersonName)
        gadd(g, auth_uri, agent.fullName, Literal(auth_fname))
        gadd(g, auth_uri, agent.normName, Literal(auth_name))
        gadd(g, work_uri, pav.authoredBy, auth_uri)
        afils=record.getaffiliations(author)
        emails=record.getemails(author)
        #must match afilliations to URI's by an inverse lookup later'
        for ele in afils:
            gdbnadd(g, auth_uri, adsbase.hasAffiliation, [
                a, adsbase.Affiliation,
                adsbase.affiliationText, Literal(ele),
                adsbase.affiliationContext, work_uri,
            ])
            
        for ele in emails:
            gadd(g, auth_uri, foaf.mbox, URIRef('mailto:'+ele))        
        acount=acount+1

def do_references(g, record, theuuid):
    bibcode_uri = uri_bib[record.bibcode]
    work_uri=uri_bib[theuuid]
    #NEW: notice our hybrid model for citations where everything is stored in expressions but ADS computed cites are stored in work too. Also note text citation objects have work uri inside them as
    #object instead of subject. Finally note we cite into expressions and not works. This needs to be
    #probably changed at work level!!!!
    for ref in record.getreferences():
        ref_bibcode = ref.attrib['bibcode']
        ref_score=int(ref.attrib['score'])
        if ref_score==5:
            theref=ref.text
            gdbnadd(g, bibcode_uri, adsbib.hasCitation, [
                a, adsbib.Citation,
                adsbib.citationText, Literal(theref),
                adsbib.citationFrom, work_uri
            ])
        else:
            theref=ref.text
            #HERE WE CITE EXPRESSION URI's!!!!! Because we may not have a work uri in the system?'
            gadd(g, work_uri, cito.cites, uri_bib[ref_bibcode])
            gadd(g, bibcode_uri, cito.cites, uri_bib[ref_bibcode])
            gdbnadd(g, bibcode_uri, adsbib.hasCitation, [
                a, adsbib.Citation,
                adsbib.citationText, Literal(theref),
                adsbib.citationFrom, work_uri,
                adsbib.identifier, Literal(ref_bibcode)
            ])

    
    
def record_as_graph_from_xml(bibcode, incuuid, node, baseUrl=None, thegraph=None):
    record = node
    print ">>>>", bibcode, record.bibcode
    bibcode_uri = uri_bib[record.bibcode]
    #bibcode_uri = URIRef("%s/%s" % (uri_bib.namespace, record.bibcode))
    #added baseUrl but didnt seem to make a difference
    if thegraph==None:
        g = ConjunctiveGraph(identifier=URIRef(baseUrl))
    else:
        g=thegraph 
    bindgraph(g)
    theuuid=record_meta(g, incuuid, record)
    #gadd(g, URIRef('#hello'), a, adsbase.Bastard)
    work_meta(g, record, theuuid)
    eray=[]
    e=None
    # i believe this also covers the case where the expression is only the arxiv
    e=expr_meta(g, record, theuuid)
    eray.append(e)
    if record['preprintid'] and int(record.rec.attrib['refereed'])==1:
        #TODOrecursively get record and refs here!
        ep=expr_eprint_meta(g, record, theuuid, e)
        eray.append(ep)
    #how to handle versioning? multiple arxivs..not here?
    #yes we dont have them here and wont for the near future until we have the pipeline set up
    work_expr_meta(g, record, eray, theuuid)
    do_keywords(g, record, theuuid)
    do_authors(g, record, theuuid)
    #need to rationalize this and do affiliations
    do_references(g, record, theuuid)     
    return g    



def record_as_rdf(datapath, bibcodefile, format='xml', baseUrl=None):

    odir = datapath + "/data/rdf"
    if not os.path.isdir(odir):
            os.makedirs(odir)
   
    xmlfile=bibcodefile.replace('biblist.txt', 'bibcodes.xml')
    yhash=getuuid4bibcode.storeYears(SORTEDYEARLIST)
    dbhash=getuuid4bibcode.setsFromBibcodes(bibcodefile,  yhash)
    print "LOADING XML FILE", xmlfile
    recordstree=ElementTree.parse(xmlfile)
    print "LOOPING OVER RECORDS"
    for rec in recordstree.findall('record'):
        node=RecordObj(rec)
        bibcode=node.bibcode
        print "BIBCODE", bibcode
        h= HTMLParser.HTMLParser()
        bibcode=h.unescape(bibcode)

        # Doug has added this as a safety check (the publications
        # data for Chandra uses %26 rather than &amp; for the bibcode).
        if bibcode.find('%') != -1:
            raise ValueError("bibcode={0} contains a % character".format(bibcode))
        
        incuuid=dbhash[bibcode]
        node.bibcode=bibcode
        graph = record_as_graph_from_xml(bibcode, incuuid, node, baseUrl)
        dformat=format
        if format=="pretty-xml":
            dformat='xml'
        serializedstuff=graph.serialize(format=format)
        #print serializedstuff
        fd=open(odir+"/"+quote_plus(bibcode)+"."+dformat, "w")
        fd.write(serializedstuff)
        fd.close()
        print "-----------------------------------------------"
        
def main():
    adsbaseurl=ads_baseurl
    try:
        opts, args = getopt.getopt(sys.argv[1:], None)
    except getopt.error, msg:
        print msg 
        print __doc__
        print "Usage: python adsclassic2rdf.py [datapath] bibcodefile [format]"
        sys.exit(2)
    print "ARGS: ", args
    if len(args) == 3:
        datapath, bibcodefile, format = args
        print record_as_rdf(datapath, bibcodefile, format, baseUrl=adsbaseurl)
    elif len(args) == 2:
        datapath, bibcodefile = args
        print record_as_rdf(datapath, bibcodefile, baseUrl=adsbaseurl)
    else:
        datapath="../chandra-rdf"
        print record_as_rdf(datapath, args[0], baseUrl=adsbaseurl)

if __name__ == '__main__':
    main()


#pretty-xml formats things rather strangely and should be avoided
