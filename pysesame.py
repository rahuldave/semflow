from urllib import quote_plus, urlencode, quote
import urllib2, types
from simplejson import loads

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

class connection:
    def __init__(self,url):
        self.baseurl=url
        self.sparql_prefix=""
    
    def addnamespace(self,id,ns):
        self.sparql_prefix+='PREFIX %s:<%s>\n' % (id,ns) 
    
    def __getsparql__(self, atype, method, uri=None):
        """Updated to support both POST and get styles. If POST, the posting 
        uri must be supplied. If GET method is entire URI, if POST its the 
        query string
        """
        if uri!=None:
            req=urllib2.Request(self.baseurl+uri)
        else:
            req=urllib2.Request(self.baseurl+method)
        req.add_header('Accept', atype)
        #req.add_header('Accept', 'application/sparql-results+json')
        #NEEDED to SET above to get sensible results.
        #req.add_header('Accept', 'application/rdf+xml')
        #req.add_header('Accept', 'application/sparql-results+xml')
        if uri !=None:
            req.add_data(method)
            req.add_header('Content-Type','application/x-www-form-urlencoded')
            #print "INPUTDATA", req.get_data()
        try:
            sock=urllib2.urlopen(req)
            #print "INFO", sock.info()
            data=sock.read()
            #print "DATA", data
            sock.close()
        except:
            import sys, traceback
            data=""
            print "ERROR", traceback.print_tb(sys.exc_info()[2])
            #return [{'error':data}]
        if atype != SPJSON:
            print "ATYPE", atype
            return data
        try:
            result=loads(data)['results']['bindings']
            return result
        except:
            import sys, traceback
            print "ERROR", traceback.print_tb(sys.exc_info()[2])
            return [{'error':data}]
        
    def use_repository(self,r):
        self.repository=r
    
    def query(self,q, atype=SPJSON):
        print "LENGTH", len(self.sparql_prefix+q)
        q='repositories/'+self.repository+'?query='+quote_plus(self.sparql_prefix+q)
        #print "Q",q
        return self.__getsparql__(atype, q)
        
    def querypost(self, q, atype=SPJSON):
        uri='repositories/'+self.repository
        q='query='+quote(self.sparql_prefix+q)
        #q='query='+quote_plus(q)
        
        #print "Q",q
        return self.__getsparql__(atype, q, uri)
        
    def construct_query(self,q):
        q='repositories/'+self.repository+'?query='+quote_plus(self.sparql_prefix+q)
        data=urllib2.urlopen(self.baseurl+q).read()
        return data
    
    def query_statements(self, qdict, atype=SPCXML):
        "query statements in rep for subject, object, predicate, or context..spoc"
        host=self.baseurl+'repositories/'+self.repository+'/statements'
        #print 'HOST', host 
        #BUG we do not handle if qitem is a list yet
        qlist=[]
        for qtype, qitem in qdict.items():
            if type(qitem)==types.ListType:#NOT SUPPORTED BY SESAME
                for themem in qitem:
                    qlist.append(SPOC[qtype]+"="+quote_plus(themem))
            else:
                qlist.append(SPOC[qtype]+"="+quote_plus(qitem))
        endpoint=host+"?"+'&'.join(qlist) 
        #print "ENDPOINT",endpoint
        req=urllib2.Request(endpoint)
        #accepting rdf/xml not ntriples
        req.add_header('Accept', atype)
        res=urllib2.urlopen(req)
        #print "INFO", res.info()
        return res.read()
        
    def get_in_context(self, context=None, atype=SPCXML):
        host=self.baseurl+'repositories/'+self.repository+'/statements'
        if context==None:
            endpoint=host
        else:
            endpoint=host+"?"+'context='+quote_plus(context) 
        #print "ENDPOINT",endpoint
        req=urllib2.Request(endpoint)
        #accepting rdf/xml not ntriples
        req.add_header('Accept', atype)
        res=urllib2.urlopen(req)
        #print "INFO", res.info()
        return res.read()
    
    def deletedata(self, context=None):
        #delete everything in a repository or in a specific context
        host=self.baseurl+'repositories/'+self.repository+'/statements'
        if context==None:
            endpoint=host
        else:
            endpoint=host+"?"+'context='+quote_plus(context)
        #print 'HOST', host , endpoint
        req=urllib2.Request(endpoint)
        req.get_method = lambda: 'DELETE'
        res=urllib2.urlopen(req)
        #print "INFO", res.info()
        return res
           
    def postdata(self,data, context=None, method='POST'):
        "POST/PUT a bunch of RDF statements into the repository"
        #PUT replaces, rather than adds, either for whole rep, or for context
        #/openrdf-sesame/repositories/mem-rdf/statements
        host=self.baseurl+'repositories/'+self.repository+'/statements'
        if context==None:
            endpoint=host
        elif type(context)==types.ListType:
            qlist=["context="+ele for ele in context]
            endpoint=host+"?"+'&'.join(qlist)
        else:
            endpoint=host+"?"+'context='+context
        #print 'ENDPOINT', endpoint 
        req=urllib2.Request(endpoint)
        if method=='PUT':#otherwise assume POST
            req.get_method = lambda: 'PUT'
        req.add_header('Content-Type', SPCXML)
        req.add_data(data)
        res=urllib2.urlopen(req)
        #print "INFO", res.info()
        return res.read()
       
    def postfile(self, thefile, context=None, method='POST'):
        #print "FILE", thefile
        data=open(thefile).read()
        #print "DATA"
        #print data
        #print "========================"
        res=self.postdata(data, context, method)
        return res	
       
q1="""
SELECT ?costar ?movie WHERE {
  ?movie  fb:film.film.starring fb:en.john_travolta .
  ?movie fb:film.film.starring ?costar .
  filter (?costar != fb:en.john_travolta)
}
"""
q2="""
SELECT ?costar ?fn WHERE {?film fb:film.film.performances ?p1 .
                   ?film dc:title ?fn .
                   ?p1 fb:film.performance.actor ?a1 .
                   ?a1 dc:title "John Malkovich".
                   ?film fb:film.film.performances ?p2 .
                   ?p2 fb:film.performance.actor ?a2 .
                   ?a2 dc:title ?costar .}
"""

if __name__=='__main__':

    c=connection('http://localhost:8081/openrdf-sesame/')
    c.use_repository('testmovie')
    c.addnamespace('fb','http://rdf.freebase.com/ns/')
    c.addnamespace('dc','http://purl.org/dc/elements/1.1/')
    
    res=c.query(q1)

    for r in res:
        print ">>",r
