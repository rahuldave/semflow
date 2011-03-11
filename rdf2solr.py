#rdf2solr: this is only for the bib stuff...not the connected observation and proposal stuff
import adsrdf
import pysolr
from urllib import unquote, quote_plus
import uuid, sys
import HTMLParser

SESAME='http://localhost:8081/openrdf-sesame/'
REPOSITORY='testads4'
SOLR='http://localhost:8983/solr'

def getInfoForBibcode(bibcode):
    c=adsrdf.ADSConnection(SESAME, REPOSITORY)
    bibcodeuri='uri_bib:'+bibcode
    result={}
    iduri=c.getDataBySP(bibcodeuri, 'fabio:isRealizationOf')
    print "returned", iduri
    iduri=iduri[0]

    result['id']=iduri.split('#')[1]
    iduri='uri_bib:'+result['id']
    print "IDURI", iduri, result['id']
        
    result['bibcode']=bibcode
    result['keywords']=[e.split('#')[1].replace('_',' ') for e in c.getDataBySP(iduri, 'adsbib:keywordConcept')]
    result['title']=c.getDataBySP(iduri, 'adsbase:title')
    result['author']=[unquote(e.split('#')[1]).replace('_',' ') for e in c.getDataBySP(iduri, 'pav:authoredBy')]
    result['keywords_s']=result['keywords']
    result['author_s']=result['author']
    #get the publication uri
    result['pubyear']=int(c.getDataBySP(bibcodeuri, 'adsbib:pubDate')[0].split()[1])
    theobjects=c.getDataBySP(bibcodeuri, 'adsbase:hasAstronomicalSource')
    objectlist=[]
    for theobj in theobjects:
        odata=c.getDataBySP('uri_base:'+theobj.split('#')[1], 'adsbase:hasMetadataString')
        odict=eval(odata[0])
        oid=odict['id']
        otype=odict['otype']
        ouri=theobj
        objectlist.append({'oid':oid, 'otype':otype, 'ouri':ouri})
    result['objectnames']=[e['oid'] for e in objectlist]
    result['objecttypes']=[e['otype'] for e in objectlist]
    result['objectnames_s']=result['objectnames']
    result['objecttypes_s']=result['objecttypes']
    return result
    
def putIntoSolr(solrinstance, bibcode):
    bibdir=getInfoForBibcode(bibcode)
    print bibdir
    solrinstance.add([bibdir], commit=False)
    
if __name__=="__main__":
    c=adsrdf.ADSConnection(SESAME, REPOSITORY)
    #researchpapers=[unquote(e.split('#')[1]) for e in c.getDataByType('cito:ResearchPaper')]
    #h= HTMLParser.HTMLParser()
    researchpapers=[ele.strip() for ele in open(sys.argv[1]).readlines()]
    print researchpapers
    #researchpapers=['2002ApJ...564..683M']
    solr=pysolr.Solr(SOLR)
    for ele in researchpapers:
        print "Indexing: ",ele
        putIntoSolr(solr, ele)
        print "-------------"
    solr.commit()
