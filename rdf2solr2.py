#v2
#rdf2solr
import adsrdf
import pysolr
from urllib import unquote, quote_plus
import uuid, sys
import HTMLParser, datetime, calendar

SESAME='http://localhost:8081/openrdf-sesame/'
REPOSITORY='testads3'
SOLR='http://localhost:8983/solr'

def splitns(theuri):
    ns, item=theuri.split('#')
    return item
    
def rinitem(item):
    return "/".join(item.split('_'))
    
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
    result['title']=c.getDataBySP(iduri, 'adsbase:title')[0]
    pquery0="""
        SELECT ?atext WHERE {
            uri_bib:%s adsbib:hasAbstract ?anode.
            ?anode adsbib:abstractText ?atext.            
        }
     """ % (result['id'])
        
    print pquery0
    res1=c.makeQuery(pquery0)
    result['abstract']=res1[0]['atext']['value']
    #print "TITLE", result['title']
    citationcount=len(c.getDataBySP(iduri, 'cito:cites'))
    result['citationcount_i']=citationcount
    ptray=c.getDataBySP(bibcodeuri, 'adsbib:paperType')
    if len(ptray)>0:
        result['papertype_s']=ptray[0]
        #print "PAPERTYPE", result['papertype_s']
    result['author']=[unquote(e.split('#')[1]).replace('_',' ') for e in c.getDataBySP(iduri, 'pav:authoredBy')]
    result['keywords_s']=result['keywords']
    result['author_s']=result['author']
    #get the publication uri
    result['pubyear_i']=int(c.getDataBySP(bibcodeuri, 'adsbib:pubDate')[0].split()[1])
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
    
    #theobsids=[rinitem(splitns(e)) for e in c.getDataBySP(bibcodeuri, 'adsbase:aboutScienceProduct')]
    theobsiduris=c.getDataBySP(bibcodeuri, 'adsbase:aboutScienceProcess')
    obsray=[]
    daprops=['obsids_s','obsvtypes_s','exptime_f','obsvtime_d','instruments_s','ra_f','dec_f', 'propids_s', 'proposaltitle', 'proposalpi', 'proposalpi_s', 'proposaltype_s']
    for theuri in theobsiduris:
        thedict={}
        theobsid=splitns(theuri)
        thedict['obsids_s']=rinitem(theobsid)
        print theobsid, c.getDataBySP('uri_obs:'+theobsid, 'adsobsv:observationType')
        thedict['obsvtypes_s']=c.getDataBySP('uri_obs:'+theobsid, 'adsobsv:observationType')[0]
        thedict['exptime_f']=float(c.getDataBySP('uri_obs:'+theobsid, 'adsobsv:observedTime')[0])
        tdt=c.getDataBySP('uri_obs:'+theobsid, 'adsbase:atTime')[0]
        month, day, year, thehour=tdt.split()

        th, tmin=thehour[:-2].split(':')
        th=int(th)
        tmin=int(tmin)
        if thehour[-2:]=='PM' and th < 12:
            th=int(th)+12
            print "TDT", tdt
        obsvtime=datetime.datetime(int(year), list(calendar.month_abbr).index(month), int(day), th, tmin)
        thedict['obsvtime_d']=obsvtime.isoformat()+"Z"
        
        theinstrument=splitns(c.getDataBySP('uri_obs:'+theobsid, 'adsbase:usingInstrument')[0])
        thedict['instruments_s']="/".join(theinstrument.split('_')[1:])
        
        #pointing=c.getDataBySP('uri_obs:'+theobsid, 'adsobsv:associatedPosition')[0]
        #FAIL dune to bnode crapola ra=c.getDataBySP(pointing, 'adsobsv:ra')
        
        pquery="""
        SELECT ?ra ?dec WHERE {
            uri_obs:%s adsobsv:associatedPosition ?position.
            ?position adsobsv:ra ?ra.
            ?position adsobsv:dec ?dec.
            
        }
        """ % (theobsid)
        
        #print pquery
        res=c.makeQuery(pquery)
        #print "POINTING", res
        ra=res[0]['ra']['value']
        dec=res[0]['dec']['value']
        print "RADEC", ra, dec
        if ra!='None' and dec!='None':
            thedict['ra_f']=float(ra)
            thedict['dec_f']=float(dec)
            
        #proposal stuff
        propuri=c.getDataBySP('uri_obs:'+theobsid, 'adsbase:asAResultOfProposal')[0]
        print "PROPURI", propuri
        thepropid=splitns(propuri)
        thedict['propids_s']=rinitem(thepropid)
        thedict['proposaltitle']=c.getDataBySP('uri_prop:'+thepropid, 'adsbase:title')[0]
        thedict['proposaltype_s']=c.getDataBySP('uri_prop:'+thepropid, 'adsobsv:observationProposalType')[0]
        e=c.getDataBySP('uri_prop:'+thepropid, 'adsbase:principalInvestigator')[0]
        thedict['proposalpi']=unquote(e.split('#')[1]).replace('_',' ') 
        thedict['proposalpi_s']=thedict['proposalpi']
        print thedict
        obsray.append(thedict)
    
    #print "OBSRAY", obsray
    if len(obsray)>0:
        for tkey in daprops:
            result[tkey]=[e[tkey] for e in obsray if e.has_key(tkey)]
    return result
    
def putIntoSolr(solrinstance, bibcode):
    bibdir=getInfoForBibcode(bibcode)
    print '===================================='
    print bibdir
    print '===================================='
    solrinstance.add([bibdir], commit=False)
    
if __name__=="__main__":
    c=adsrdf.ADSConnection(SESAME, REPOSITORY)
    #researchpapers=[unquote(e.split('#')[1]) for e in c.getDataByType('cito:ResearchPaper')]
    #h= HTMLParser.HTMLParser()
    researchpapers=[ele.strip() for ele in open(sys.argv[1]).readlines()]
    #print researchpapers
    #researchpapers=['2000A&A...359..489C', '2000ApJ...534L..47G', '2000ApJ...536L..27W', '2000ApJ...540L..69S', '2000ApJ...541...49H']
    solr=pysolr.Solr(SOLR)
    #solr=None
    for ele in researchpapers:
        print "Indexing: ",ele
        putIntoSolr(solr, ele)
        print "-------------"
    solr.commit()
