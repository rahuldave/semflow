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

def initialize_logging(logname, file=logging.INFO, screen=logging.INFO):
    """Sets up console and file logging. The levels
    are set by the screen and file arguments which default
    to logging.INFO for both.

    The file output is <logname>.log.

    """

    global logger
    
    logging.basicConfig(level=file,
                        format="%(asctime)s %(levelname)-8s %(message)s",
                        filename="{0}.log".format(logname),
                        filemode="w"
                        )

    logger = logging.getLogger("")
                        
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(message)s'))
    ch.setLevel(screen)
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

# TODO:
#   Could amalgamate some of the queries since many access the
#   same URI (although may not be worth it since spo-style queries
#   should be optimised wrt general SPAQRL queries).
#
def getInfoForBibcode(c, solr, bibcode, mission, project):
    bibcodeuri='uri_bib:'+bibcode
    result={}
    iduri=c.getDataBySP(bibcodeuri, 'fabio:isRealizationOf')
    debug("returned", "{0} {1}".format(iduri, bibcodeuri))
    iduri=iduri[0]

    # we use the original URI when accessing the author names
    idurifull = iduri
    
    result['id']=iduri.split('#')[1]
    theid=result['id']
    iduri='uri_bib:'+result['id']
    debug("IDURI", "{0} {1}".format(iduri, result['id']))
        
    result['bibcode']=bibcode

    # Should get the rdf:label for the concept (caching it)
    # rather than decoding the URI, but needs the label added to the
    # store. Note that we unquote the fragment to ensure %3B and
    # other keywords are displayed sensibly.
    # 
    result['keywords']=[unquote(e.split('#')[1]).replace('_',' ') for e in c.getDataBySP(iduri, 'adsbib:keywordConcept')]
    
    result['title']=c.getDataBySP(iduri, 'adsbase:title')[0].decode("utf-8") # DJB added decode statement as I think we want to send across a unicode string
    pquery0="""
        SELECT ?atext WHERE {
            uri_bib:%s adsbib:hasAbstract [ adsbib:abstractText ?atext ] .            
        }
     """ % (result['id'])

    #print pquery0
    res1=c.makeQuery(pquery0)
    #print res1[0]
    result['abstract']=res1[0]['atext']['value']

    debug("TITLE", result['title'].encode("ascii", "replace")) ## can contain UTF-8
    citationcount=len(c.getDataBySP(iduri, 'cito:cites'))
    result['citationcount_i']=citationcount

    # Paper type handling:
    # 
    # The adsbib:paperType is currently only added for Chandra data, but
    # this means that papers with data from Chandra + MAST missions will
    # have this setting. Since the predicate does not indicate which mission
    # catagorised the paper as "science", we have to either guess, leave
    # as "science" (i.e. with no mission attribution), or ignore.
    # Doug has elected to go for the ignore route since it doesn't seem
    # to be useful at the present time.
    """
    ptray=c.getDataBySP(bibcodeuri, 'adsbib:paperType')

    The following is broken since a Chandra paper with MAST/euve data
    will lose the "chandra/science" setting if the Chandra data is added
    to Solr before EUVE.

    if len(ptray)>0:
        # DJB:
        #   for papers with Chandra and MAST data will have
        #   a paper type of "science", which results in an
        #   entry of mission+"/science" -> "MAST/science"
        #   as well as (added later on) project+"/Regular"
        #
        #   We switch to using project rather than mission here,
        #   so get "chandra/science", "iue/science", ...
        #   although the MAST ones will get re-added later on
        #   (but duplication left in since not all MAST missions
        #   will have an entry added here).
        #
        #paptypes=[mission+"/"+ele for ele in ptray]
        paptypes=[project+"/"+ele for ele in ptray]
        debug("PTYPE", "{0} {1}".format(bibcode, ptray))
    else:
        paptypes=[]
        debug("PTYPE", "{0} {1}".format(bibcode, "NONE"))

    """    
    
    # TODO:
    #
    # We want to store an "author list" as well as the individual
    # authors, so that we can get the ordering correct, but we do not
    # have that information in the RDF store at present. Storing the
    # author list should remove the issue we have when a paper has the
    # same author name appear more than once. Storing an author list
    # is neat, but then how can we have a "only display the first n
    # authors"?  One option would be to create two versions: the full
    # list and a short form, but this is a bit messy.

    # NOTE:
    #
    # Since each author name is stored with a UUID at the end, and
    # will be added multiple times to a paper, if the paper uses data
    # from multiple missions, then we get multiple copies of an
    # author. So we go to the effort of decoding the authors to get a
    # unique set, which means that if an authorname is repeated twice
    # - e.g. Terlevich and Terlevich - then we will lose information
    # if the names match completely. Also, we now query the RDF store
    # for the agents:normName field for each author rather than decode
    # from the URI, although this may slow things down.
    """
    authoren=c.getDataBySP(iduri, 'pav:authoredBy')
    #print authoren
    #BUG: one slash too many in authors you think?
    result['author']=[unquote(e.split('/')[-2]).replace('_',' ') for e in authoren]
    """

    aqstr = "SELECT ?name {{ <{0}> <http://swan.mindinformatics.org/ontologies/1.2/pav/authoredBy> [ <http://swan.mindinformatics.org/ontologies/1.2/agents/normName> ?name ].}}".format(idurifull)
    authoren = c.makeQuery(aqstr)
    authorlist = set()
    for au in authoren:
        authorlist.add(au["name"]["value"])
        
    result['author'] = list(authorlist)
    
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
            odict=eval(odata[0]) # why does this need to be an eval? aha, because we are storing a Python dictionary in the string!
            oid=odict['id']
            # Strip out the leading 'NAME ' from object identifiers
            if oid.startswith("NAME "):
                oid = oid[5:]
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

            """ For now Doug is excluding the paper type facet

            # See the discussion for the creation of paptypes above
            # since there is some awkwardness here (some MAST papers
            # end up having an adsbib:paperType value since they also
            # contain Chandra data).
            #
            # papertypes.add(theproject+"/Regular")
            papertypes.add(theproject+"/science")
            """

            missions.add(themission+"/"+theproject)

        elif is_chandra:
            themission, thevariable, theobsid=splitns(theuri)
            theproject=themission#like Chandra/Chandra
            uritail=themission+"/"+thevariable+"/"+theobsid
            #thedict['missions_s']=themission # this should be in RDF!!

            """ Paper type handling is currently removed

            # this is needed to handle papers with multiple missions
            papertypes.add(theproject+"/science")
            """

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

        # print "The target", thetarget
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
                
        #Hut dosent have obsvtypes. Call it MAST_HUT/None

        # Chandra data was being created using adsobsv:tExpTime when it should have been
        # adsobsv:tExptime. This should now be fixed but this check is left in to catch
        # any oddities.
        #
        tvals = c.getDataBySP('uri_obs:'+uritail, 'adsobsv:tExptime')
        if len(tvals) == 0:
            raise IOError("Unable to find adsobsv:tExptime for uri_obs:{0}".format(uritail))

        else:
            if len(tvals) > 1:
                debug("MULTI-EXP", "uri_obs:{0} has adsobsv:tExptime={1}".format(uritail, tvals))

            thedict['exptime_f'] = float(tvals[0])
            
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

        # TODO: should be able to query the RDF store for the label to use for the instrument
        # but for now just extract the information from the URI, and remove any %-encoding
        # done
        theinstrumentname = unquote(theinstrumentname)
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
                # The map between bibcode, obsid and proposal can contain proposals
                # for which we have no other data. Instead of saying 'No Info' we can
                # at least add in the mission name.
                #
                # TODO: should we just remove proposaltype_s for these records? If not,
                # do we want to add in fake proposals for other missions that do not have
                # them (probably not)?
                #
                #thedict['proposaltype_s']='No Info'
                if themission == "MAST":
                    thedict['proposaltype_s'] = theproject + '/None'
                elif themission == "CHANDRA":
                    thedict['proposaltype_s'] = 'CHANDRA/None'
                else:
                    raise ValueError("Unexpected mission '{0}' for {1}".format(mission, propuri))

            qstr = "SELECT ?name WHERE { <" + propuri + "> adsbase:principalInvestigator [ agent:fullName ?name ] . }"
            pinameres = c.makeQuery(qstr)
            nres = len(pinameres)
            if nres == 0:
                piname = 'No Info'
            else:
                if nres != 1:
                    print("DBG: found {0} proposal pis for {1}, using first from {2}".format(nres, propuri, pinameres))
                piname = pinameres[0]["name"]["value"]
                # the following should not occur but just in case
                if piname.strip() == "":
                    logger.debug("PINAME: found ' ' so converting to 'No Info'; should not happen")
                    piname = "No Info"

            thedict['proposalpi'] = piname
            thedict['proposalpi_s']=thedict['proposalpi']
            
        #BUG: SHOULD we have something like this associating None's where there is no proposal?????'    
        #else:
        #    thedict['propids_s']=themission+"/None"
            
            #print thedict
        obsray.append(thedict)
        
    result['missions_s']=list(missions)

    """ paper types are currently removed

    paptypes.extend(list(papertypes))
    if len(paptypes) == 0:
        debug("PTYPE", "bibcode={0} has no paper type!".format(bibcode))

    result['papertype_s']=paptypes
    """

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


def putIntoSolr(sesame, solrinstance, bibcode, mission, project):
    bibdir=getInfoForBibcode(sesame, solrinstance, bibcode, mission, project)
    #print '===================================='
    #print bibdir
    #print '===================================='

    solrinstance.add([bibdir], commit=False)
    
    
# Issue with loading into sh obsids.sh and all wont we duplicate them
# if we do stuff separately for overlaps and stuff. Should we do it
# just once or check whats been loaded to protect against this BUG
#
if __name__=="__main__":

    # to cut down on the screen output you can try"
    #initialize_logging("rdf2solr5", file=logging.WARNING, screen=logging.WARNING)
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

    info("Mission:", mission)
    
    sesame = adsrdf.ADSConnection(SESAME, REPOSITORY)
    info("Sesame connection:", sesame)

    researchpapers=[ele.strip() for ele in open(biblist).readlines()]
    debug("Research papers:", researchpapers)
    
    solr=pysolr.Solr(SOLR)
    info("Solr connection:", solr)

    for ele in researchpapers:
        info("Indexing:", ele)
        putIntoSolr(sesame, solr, ele, mission, project)
        #logger.info("-------------")

    solr.commit()
    info("Finished:", time.asctime())
