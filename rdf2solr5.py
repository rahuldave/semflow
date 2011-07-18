#v2: This contains the connected stuff
#rdf2solr
import adsrdf
import pysolr
from urllib import unquote, quote_plus
import uuid, sys
import HTMLParser, datetime, calendar
from namespaces import n3encode

# as we are assuming python 2.6 we can use set() rather than Set()
# from sets import Set

import time
import logging

logger = None

def initialize_logging(logname):
    """Sets up console level logging at INFO
    and file logging at DEBUG level (file output is
    <logname>.log.

    """

    global logger
    
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(levelname)-8s %(message)s",
                        filename="{0}.log".format(logname),
                        filemode="w"
                        )

    logger = logging.getLogger("")
                        
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(message)s'))
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

def debug(lbl, msg):
    """Write out the string 'lbl msg' at the DEBUG log level."""
    logger.debug("{0} {1}".format(lbl, msg))
    
def info(lbl, msg):
    """Write out the string 'lbl msg' at the INFO log level."""
    logger.info("{0} {1}".format(lbl, msg))
    
#SESAME='http://localhost:8081/openrdf-sesame/'
#REPOSITORY='testads4'
#SOLR='http://localhost:8983/solr'

#IMPORTANT:
#The critical problem when we have multiple results from different surveys
#are twofold (a) Ordering (b) stuff added later. Currently we punt on (b)
#by assuming everything is just added at one time. ie we redo all SOLR.

def splitns(theuri, splitter='/', atposition=-2):
    splittuple=theuri.split(splitter)[atposition-1:]
    return splittuple

def splitnsmast(theuri, atposition=-3, splitter='/'):
    mission, variable, theid, thehash=theuri.split(splitter)[atposition-1:]
    logger.debug("{0}+++".format(mission))
    return mission, variable, theid+"/"+thehash
        
def rinitem(item):
    return "/".join(item.split('_'))
    
def getInfoForBibcode(solr, bibcode, mission, project):
    c=adsrdf.ADSConnection(SESAME, REPOSITORY)
    bibcodeuri='uri_bib:'+bibcode
    result={}
    iduri=c.getDataBySP(bibcodeuri, 'fabio:isRealizationOf')
    debug("returned", "{0} {1}".format(iduri, bibcodeuri))
    iduri=iduri[0]

    result['id']=iduri.split('#')[1]
    theid=result['id']
    iduri='uri_bib:'+result['id']
    debug("IDURI", "{0} {1}".format(iduri, result['id']))
        
    result['bibcode']=bibcode
    result['keywords']=[e.split('#')[1].replace('_',' ') for e in c.getDataBySP(iduri, 'adsbib:keywordConcept')]
    result['title']=c.getDataBySP(iduri, 'adsbase:title')[0].decode("utf-8") # DJB added decode statement as I think we want to send across a unicode string
    pquery0="""
        SELECT ?atext WHERE {
            uri_bib:%s adsbib:hasAbstract ?anode.
            ?anode adsbib:abstractText ?atext.            
        }
     """ % (result['id'])
        
    #print pquery0
    res1=c.makeQuery(pquery0)
    #print res1[0]
    result['abstract']=res1[0]['atext']['value']

    debug("TITLE", result['title'].encode("ascii", "replace")) ## can contain UTF-8
    citationcount=len(c.getDataBySP(iduri, 'cito:cites'))
    result['citationcount_i']=citationcount
    #this is the first thing that can have multiple stuff from chandra, hut and other
    #we still dont handle this
    ptray=c.getDataBySP(bibcodeuri, 'adsbib:paperType')
    ######FLAG
    if len(ptray)>0:
        paptypes=[mission+"/"+ele for ele in ptray]
        debug("PTYPE", "{0} {1}".format(bibcode, ptray))
    else:
        paptypes=[]
        debug("PTYPE", "{0} {1}".format(bibcode, "NONE"))
    
    #Above is only accurate when we dont do overlaps. For HUT/Chandra overlap, we should
    #be doing None/Something overlap but i do this as just Something should be fine
    #Itake the position that "None", if you want to institutionalize it, should be put in the rdf    
    #print "PAPERTYPE", result['papertype_s']
    authoren=c.getDataBySP(iduri, 'pav:authoredBy')
    #print authoren
    #BUG: one slash too many in authors you think?
    result['author']=[unquote(e.split('/')[-2]).replace('_',' ') for e in authoren]
    #print result['author']
    result['keywords_s']=result['keywords']
    result['author_s']=result['author']
    #get the publication uri
    result['pubyear_i']=int(c.getDataBySP(bibcodeuri, 'adsbib:pubDate')[0].split()[1])
    theobjects=c.getDataBySP(bibcodeuri, 'adsbase:hasAstronomicalSource')
    debug("THEOBJECTS", "{0} {1}".format(bibcode, len(theobjects)))
    objectlist=[]
    for theobj in theobjects:
        #print "theobj", theobj
        odata=c.getDataBySP('uri_source:'+theobj.split('/')[-1], 'adsbase:hasMetadataString')
        #print "theobj", theobj, odata
        if len(odata)>0:
            odict=eval(odata[0])
            oid=odict['id']
            otype=odict['otype']
            ouri=theobj
            objectlist.append({'oid':oid, 'otype':otype, 'ouri':ouri})
        else:
            print "PROBLEM", bibcode, theobj, odata
    result['objectnames']=[e['oid'] for e in objectlist]
    result['objecttypes']=[e['otype'] for e in objectlist]
    result['objectnames_s']=result['objectnames']
    result['objecttypes_s']=result['objecttypes']
    ######FLAG
    #if mission=='CHANDRA':
    #    result['missions_s']=mission
    #else:
    #    result['missions_s']=mission+"/"+project
    #print result['objectnames']
    #theobsids=[rinitem(splitns(e)) for e in c.getDataBySP(bibcodeuri, 'adsbase:aboutScienceProduct')]
    theobsiduris=c.getDataBySP(bibcodeuri, 'adsbase:aboutScienceProcess')
    #print "OBSIDS", bibcodeuri, theobsiduris
    obsray=[]
    #TESTnotice by this we dont uniq telescopes or data types...what does this mean for the numbers, if anything?
    #daprops=['obsids_s','obsvtypes_s','exptime_f','obsvtime_d','instruments_s', 'telescopes_s', 'emdomains_s', 'missions_s', 'targets_s', 'ra_f','dec_f', 'datatypes_s','propids_s', 'proposaltitle', 'proposalpi', 'proposalpi_s', 'proposaltype_s']
    #daprops=['obsids_s','obsvtypes_s','exptime_f','obsvtime_d','instruments_s', 'telescopes_s', 'emdomains_s',  'targets_s', 'ra_f','dec_f', 'datatypes_s','propids_s', 'proposaltitle', 'proposalpi', 'proposalpi_s', 'proposaltype_s']
    daprops=['obsids_s','obsvtypes_s','exptime_f','obsvtime_d','instruments_s', 'telescopes_s', 'emdomains_s',  'targets_s', 'ra_f','dec_f', 'datatypes_s','propids_s', 'proposaltitle', 'proposalpi', 'proposalpi_s', 'proposaltype_s']
    
    debug("THEOBSIDURIS", theobsiduris)
    datatypes=[]
    #olddict=solr.search('id:'+theid)
    missions=set()
    papertypes=set()
    for theuri in theobsiduris:
        thedict={}

        # There must be better ways to do this
        is_mast = theuri.find('MAST') != -1
        is_chandra = theuri.find('CHANDRA') != -1
        
        #BUG: make this polymorphic
        if is_mast:
            themission, theproject,thevariable, theobsid=splitns(theuri, atposition=-3)
            uritail=themission+"/"+theproject+"/"+thevariable+"/"+theobsid
            #thedict['missions_s']=themission+"/"+theproject
            papertypes.add(theproject+"/Regular")
            missions.add(themission+"/"+theproject)
        elif is_chandra:
            themission, thevariable, theobsid=splitns(theuri)
            theproject=themission#like Chandra/Chandra
            uritail=themission+"/"+thevariable+"/"+theobsid
            #thedict['missions_s']=themission # this should be in RDF!!
            #chandra already has papertypes thanks to sherry so dont do anything
            #perhaps papertypes should be handled at the pubrdf level
            missions.add(theproject)
        else:
            raise ValueError("Unable to decode URI for mission: " + theuri)
        
        debug("URITAIL", uritail)
        if is_mast:
            pquery0="""
            SELECT ?tname WHERE {
            %s adsbase:target ?tnode.
            ?tnode adsbase:name ?tname.            
            }
            """ % (n3encode('uri_obs:'+uritail))
            #Sprint pquery0
            res1=c.makeQuery(pquery0)
            debug("RES1", res1)
            if len(res1) > 0:
                target=res1[0]['tname']['value']
            else:
                target='Unspecified'
            #target=res1[0]['tname']['value']
            thetarget=themission+"/"+target
        elif is_chandra:
            titleray=c.getDataBySP('uri_obs:'+uritail, 'adsbase:title')
            if len(titleray)==0:
                title="Unspecified"
            else:
                title=titleray[0]
            thetarget=themission+"/"+title
        else:
            thetarget="None"
        print "The target", thetarget
        thedict['targets_s']=thetarget
        #print "::::::::::::::::", theobsid, theuri, themission, thevariable
        #thedict['obsids_s']=rinitem(theobsid)
        thedict['obsids_s']=theproject+"/"+theobsid

        #print theobsid, c.getDataBySP('uri_obs:'+uritail, 'adsobsv:observationType')
        obstypes=c.getDataBySP('uri_obs:'+uritail, 'adsobsv:observationType')
        if len(obstypes)>0:
            if theproject==themission:
                thedict['obsvtypes_s']=theproject+"/"+obstypes[0]
            else:
                thedict['obsvtypes_s']=themission+"/"+theproject+"/"+obsvtypes[0]
        else:
            if theproject==themission:
                thedict['obsvtypes_s']=theproject+"/Unspecified"
            else:
                thedict['obsvtypes_s']=themission+"/"+theproject+"/Unspecified"
        #Hut dosent have obsvtypes. Caal it MAST_HUT/None
        debug("???", "{0} {1}".format(c.getDataBySP('uri_obs:'+uritail, 'adsobsv:tExptime'),
                                      c.getDataBySP('uri_obs:'+uritail, 'adsobsv:tExpTime')))

        # this indicates a bug in the ingest code that should be cleaned up 
        try:
            thedict['exptime_f']=float(c.getDataBySP('uri_obs:'+uritail, 'adsobsv:tExpTime')[0])
        except:
            thedict['exptime_f']=float(c.getDataBySP('uri_obs:'+uritail, 'adsobsv:tExptime')[0])
            
        tdt=c.getDataBySP('uri_obs:'+uritail, 'adsbase:atTime')[0]
        #print "TDT", tdt
        obsvtime=datetime.datetime.strptime(tdt,"%Y-%m-%dT%H:%M:%S")
        #month, day, year, thehour=tdt.split()

        #th, tmin=thehour[:-2].split(':')
        #th=int(th)
        #tmin=int(tmin)
        #if thehour[-2:]=='PM' and th < 12:
        #    th=int(th)+12
        #    print "TDT", tdt
        #obsvtime=datetime.datetime(int(year), list(calendar.month_abbr).index(month), int(day), th, tmin)
        thedict['obsvtime_d']=obsvtime.isoformat()+"Z"
        
        #hasDatum is a subset of hasDataProduct. How do we get sparql to fo up inhertitance hierarchy
        #Currently we have no way of knowing as the owl file hasnt been loaded in
        pquery="""
            SELECT ?dtype WHERE {
            {%s adsobsv:hasDataProduct ?daturi.} UNION {%s adsobsv:hasDatum ?daturi.}
            ?daturi adsbase:dataType ?dtype.
            }
        """ % (n3encode('uri_obs:'+uritail),n3encode('uri_obs:'+uritail) )
        res=c.makeQuery(pquery)
        #print "RES", res, pquery
        tempdt={}
        if len(res)>0:
            for ele in res:
                tkey=ele['dtype']['value']
                if tempdt.has_key('tkey'):
                    tempdt[tkey]+=1
                else:
                    tempdt[tkey]=1
            thedict['datatypes_s']=tempdt.keys()
        else:
            thedict['datatypes_s']=[]
        #BUG: Still assume one istrument. This will change, point is how? There will be both
        #multiple stuff for non-simple obs and hierarchical stuff for simple obs like gratings
        #how will we model this?
        debug("DATATYPES", thedict['datatypes_s'])
        theinstrument=c.getDataBySP('uri_obs:'+uritail, 'adsbase:usingInstrument')[0]
        theinstrumentname=theinstrument.split('/')[-1]
        thedict['instruments_s']="/".join(theinstrumentname.split('_'))
        #BUG: Still assume one telescope, this will change
        thetelescope=c.getDataBySP('uri_obs:'+uritail, 'adsobsv:atTelescope')[0]
        thetelescopename=thetelescope.split('/')[-1]
        thedict['telescopes_s']="/".join(thetelescopename.split('_'))
        #print thedict['instruments_s']
        #pointing=c.getDataBySP('uri_obs:'+theobsid, 'adsobsv:associatedPosition')[0]
        #FAIL dune to bnode crapola ra=c.getDataBySP(pointing, 'adsobsv:ra')
        #BUG we should first even see if Pointing exists before going for ra or dec
        
        #This will need special handling as it is multivalued array even within obsv.
        #So it will need flattening within publications
        theemdomains=c.getDataBySP('uri_obs:'+uritail, 'adsobsv:wavelengthDomain')
        #BUG:Note that by doing this emdomains is optional...Not sure we want that
        if len(theemdomains) > 0:
            thedict['emdomains_s']=[]
            for domain in theemdomains:
                thedict['emdomains_s'].append(domain.split('_')[-1])
            
        thepointings=c.getDataBySP('uri_obs:'+uritail, 'adsobsv:associatedPosition')
        
        if len(thepointings) > 0:
            pquery="""
            SELECT ?ra ?dec WHERE {
            %s adsobsv:associatedPosition ?position.
            ?position adsobsv:ra ?ra.
            ?position adsobsv:dec ?dec.
                
            }
            """ % (n3encode('uri_obs:'+uritail))
        
            #print pquery
            res=c.makeQuery(pquery)
            #print "POINTING", res
            ra=None
            dec=None
            if len(res)!=0:
                ra=res[0]['ra']['value']
                dec=res[0]['dec']['value']
                #print "RADEC", ra, dec
            if ra!='None' and dec!='None':
                thedict['ra_f']=float(ra)
                thedict['dec_f']=float(dec)
        else:
            print "******************************************No pointings for ", uritail
            
        #proposal stuff...not searching abstracts yet
        props=c.getDataBySP('uri_obs:'+uritail, 'adsbase:asAResultOfProposal')
        debug("PROPS", props)
        #BUG: again assuming only one proposal here. When we get paper proposals this will
        #Not be true any more. We should also disambiguate observational from paper proposals.
        #though paper proposals will be assoced with papers, not here, so this should be obsvprop
        #only
        #what happens when like in 2002ApJ...573..157N, this shows up for multiple missions
        if len(props)>0:
            propuri=props[0]
            debug("PROPURI", propuri)
            if propuri.find('MAST')!=-1:
                themission, theproject,thevariable, thepropid=splitns(propuri, atposition=-3)
                proptail=themission+"/"+theproject+"/"+thevariable+"/"+thepropid
            else:
                themission, thevariable, thepropid=splitns(propuri)
                theproject=themission#like Chandra/Chandra
                proptail=themission+"/"+thevariable+"/"+thepropid
            debug("PROPTAIL", proptail)
            #themission, thevariable, thepropid=splitns(propuri)
            #proptail=themission+"/"+thevariable+"/"+thepropid
            thedict['propids_s']=theproject+"/"+thepropid
            #print proptail, n3encode('uri_prop:'+proptail), c.getDataBySP('uri_prop:'+proptail, 'adsbase:title')
            proposaltitles=c.getDataBySP('uri_prop:'+proptail, 'adsbase:title')
            if len(proposaltitles)>0:
                thedict['proposaltitle']=proposaltitles[0]
            else:
                thedict['proposaltitle']='No Info'
            #proposal type already has project or mission included
            proposaltypes=c.getDataBySP('uri_prop:'+proptail, 'adsobsv:observationProposalType')
            if len(proposaltypes)>0:
                thedict['proposaltype_s']=proposaltypes[0]
            else:
                thedict['proposaltype_s']='No Info'

            elist=c.getDataBySP('uri_prop:'+proptail, 'adsbase:principalInvestigator')
            #print "PI", e
            if len(elist)>0:
                e=elist[0]
                thedict['proposalpi']=unquote(e.split('/')[-2]).replace('_',' ')
            else:
                thedict['proposalpi']='No Info'

            thedict['proposalpi_s']=thedict['proposalpi']

        #BUG: SHOULD we have something like this associating None's where there is no proposal?????'    
        #else:
        #    thedict['propids_s']=themission+"/None"
            
            #print thedict
        obsray.append(thedict)
    result['missions_s']=list(missions)
    paptypes.extend(list(papertypes))
    result['papertype_s']=paptypes
    #print "OBSRAY", obsray
    if len(obsray)>0:
        for tkey in daprops:
            #print "tkey is ", tkey
            temptkey=[e[tkey] for e in obsray if e.has_key(tkey)]
            #print "temptkey", temptkey
            temp2=[item if hasattr(item,'__iter__') else [item] for item in temptkey]
            #print "temp2", temp2
            if len(temp2) >0:
                result[tkey]=reduce(lambda x,y: x+y, temp2)
            else:
                result[tkey]=[]
    return result


def putIntoSolr(solrinstance, bibcode, mission, project):
    bibdir=getInfoForBibcode(solrinstance, bibcode, mission, project)
    #print '===================================='
    #print bibdir
    #print '===================================='

    solrinstance.add([bibdir], commit=False)
    
    
    #Issue with loading into sh obsids.sh and all wont we duplicate them if we do stuff separateky for overlaps and stuff. Should we do it just once or check whats been loaded to protect against this BUG
if __name__=="__main__":

    initialize_logging("rdf2solr5")
    debug("Starting:", time.asctime())
    
    if len(sys.argv)==4:
        confname = "./default.conf"
    elif len(sys.argv)==5:
        confname = sys.argv[4]
    else:
        print "Usage: python rdf2solr4.py MISSION(CAPS) project(small) biblistfile [conffile]"
        sys.exit(-1)

    debug("Execing:", confname)
    execfile(confname)

    biblist=sys.argv[3]
    mission=sys.argv[1]
    project=sys.argv[2]
    
    c=adsrdf.ADSConnection(SESAME, REPOSITORY)
    info("Sesame connection:", c)

    researchpapers=[ele.strip() for ele in open(biblist).readlines()]
    debug("Research papers:", researchpapers)
    
    solr=pysolr.Solr(SOLR)
    info("Solr connection:", solr)

    for ele in researchpapers:
        info("Indexing:", ele)
        putIntoSolr(solr, ele, mission, project)
        logger.info("-------------")
        
    solr.commit()
    debug("Finished:", time.asctime())
