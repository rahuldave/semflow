#layer for ads like things on top of pysesame and rdflib  or other. currently only pysesame.
from pysesame import connection, SPJSON, SPXML, SPCXML
#from bib2rdf2 import record_as_rdf, InvalidBibcode
import namespaces, types, StringIO
from rdflib import plugin, URIRef, BNode
from rdflib.Graph import ConjunctiveGraph



SPJSON='application/sparql-results+json'
SPXML='application/sparql-results+xml'
SPCXML='application/rdf+xml'
SPCN3='text/rdf+n3'
SPATXT='text/boolean'

SPOC={
    's':'subj',
    'o':'obj',
    'p':'pred',
    'c':'context'
}


#This document must:
"""
We must using this module be able to
(a) set up a connection with proper namespaces
(b) add a file under a given context to the repository
(c) ntriple encode namespave given thingies for context and other queries
This will require wrapping and normalizing some things in the connection class
Also cleany separate encoding from one file to the other, the pysesame connector
needs to be  general too and know nothing about namespaces.
(d) provide an interface easily usable by a script, a load script (ie manage transaction)
and by a long running web server
(e) provide python dictionary interfaces to both rdf and json outs using rdflib
"""
#you dont want to directly use PUT on a context for just one thing as that would replace
#the elements on that context each time. rather to delete data in that context, figure which files
#were in that context, and repost. This is under the assumption that multiple files or 
#transactions go into the population of a context

#create as a delegate class with added translation functionality

#TODO: We should create a cache for stuff like getSataBySP which does getDataByS and 
#then caches results so we dont hit triplestore again and again

class ADSConnection:

    def __init__(self, sesameURL, repository):
        c=connection(sesameURL)
        c.use_repository(repository)
        for ele in namespaces.namespace_dict.keys():
            #print ele, str(namespaces.namespace_dict[ele])
            c.addnamespace(ele, str(namespaces.namespace_dict[ele]))
        #tsc is triple store connection. we need to first write this, then translate to a driver architecture
        self.tsc=c
        
    
    #Build    
    
    def makeQuery(self, query, type=SPJSON):
        data=self.tsc.querypost(query, type)
        return data
        
    def deleteData(self, context=None):
        if context:
            self.tsc.deletedata(namespaces.n3encode(context))
        else:
            self.tsc.deletedata()
    
    def getDataInContext(self, context=None):
        if context:
            data=self.tsc.get_in_context(namespaces.n3encode(context))
        else:
            data=self.tsc.get_in_context()
        return data
        
    def getDataBySPO(self, thingy, thingytype="s", context=None):
        qdict={}
        if context:
            qdict['c']=namespaces.n3encode(context)
        qdict[thingytype]=namespaces.n3encode(thingy)
        #print "QDICT", qdict
        data=self.tsc.query_statements(qdict)
        return data
        
    #BUG do not handle if value corresponding to a key is a list, ie we dont handle two subjects for eg.
    def getDataByDict(self, thedict, context=None):
        qdict={}
        if context:
            qdict['c']=namespaces.n3encode(context)
        for ele in thedict.keys():
            if type(thedict[ele])==types.ListType:#NOT SUPPORTED BY SESAME
                qdict[ele]=[]
                for themem in thedict[ele]:
                    qdict[ele].append(namespaces.n3encode(themem))
            else:
                qdict[ele]=namespaces.n3encode(thedict[ele])
        #print "QDICT", qdict
        data=self.tsc.query_statements(qdict)
        return data
    
    def getDataByType(self, thetype, context=None):
        thedict={'p':'rdf:type', 'o':thetype}
        data=self.getDataByDict(thedict, context)
        bg=ConjunctiveGraph()
        namespaces.bindgraph(bg)
        res=bg.parse(StringIO.StringIO(data))
        listofo=[]
        for trip in res:
            listofo.append(str(trip[0]))
        return listofo
            
    def getDataBySP(self, thingy, propthingy, context=None):
        qdict={}
        if context:
            qdict['c']=namespaces.n3encode(context)
        #print "THINGY", thingy
        if len(thingy.split(':'))>1:
            qdict['s']=namespaces.n3encode(thingy)
        else:
            qdict['s']=thingy
        qdict['p']=namespaces.n3encode(propthingy)
        #print "qdict", qdict
        data=self.tsc.query_statements(qdict)
        #print data
        bg=ConjunctiveGraph()
        namespaces.bindgraph(bg)
        #abnode=BNode()
        res=bg.parse(StringIO.StringIO(data))
        listofo=[]
        #this bnode crap is very fragile TODO:replace
        for trip in res:
            listofo.append(str(trip[2]))
        return listofo
                
    def addFile(self, thefile,context=None):
        if context:
            self.tsc.postfile(thefile, namespaces.n3encode(context))
        else:
            self.tsc.postfile(thefile)
            
if __name__=="__main__":
    import sys
    c=ADSConnection('http://localhost:8081/openrdf-sesame/', 'testads3')
    #result=c.getDataBySPO('uri_bib:1998MNRAS.293..306Q')
#    bibcode='1998MNRAS.293..306Q'
#    bibcodeuri='uri_bib:'+bibcode
#    result1=c.getDataBySP(bibcodeuri, 'adsbib:keywordConcept')
#    result2=c.getDataBySP(bibcodeuri, 'adsbase:title')
#    result3=c.getDataBySP(bibcodeuri, 'pav:authoredBy')
#    print "<<\n",bibcodeuri, result1, result2, result3, "\n>>"
#    thedict={
#     's':  'uri_bib:1998MNRAS.293..306Q',
#     'p': ['adsbib:keywordConcept', 'adsbase:title'] #dosent work
#        
#    }
    researchpapers=c.getDataByType('adsobsv:Datum')
    print len(researchpapers)
    #<http://ads.harvard.edu/sem/context#a40e27dc-8abb-4698-bd9b-415b60d3cfb4-chandra/loadfiles-obsv.py-0.1>
    #c.deleteData('uri_context:a40e27dc-8abb-4698-bd9b-415b60d3cfb4-chandra/loadfiles-obsv.py-0.1')
    #c.getDataInContext('uri_context:a40e27dc-8abb-4698-bd9b-415b60d3cfb4-chandra/loadfiles-obsv.py-0.1')
    researchpapers=c.getDataByType('adsobsv:Datum')
    print len(researchpapers)
    #result=c.getDataByDict(thedict)
    #print result
