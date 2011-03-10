"""
Namespaces and related routines for ADS project.
"""

from rdflib import URIRef, Namespace, Literal, BNode
from rdflib.namespace import XSD

import datetime

class MyNamespace(object):

    def __init__(self, uristring):
        self.namespace=Namespace(uristring)

    def __getattr__(self, item):
        return self.namespace[item]

    def __getitem__(self, item):
        return self.namespace[item]

class ADSNamespace(MyNamespace):

    def __init__(self, fname):
        MyNamespace.__init__(self,
                             "https://github.com/rahuldave/ontoads/raw/master/owl/" + fname + "#"
                             )

IVOA_URI_HEAD = "ivoa://"

def is_ivoa_uri(txt):
    return txt.startswith(IVOA_URI_HEAD)

rdf=MyNamespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs=MyNamespace("http://www.w3.org/2000/01/rdf-schema#")

xsd=MyNamespace("http://www.w3.org/2001/XMLSchema#")

skos=MyNamespace("http://www.w3.org/2004/02/skos/core#")

dc=MyNamespace("http://purl.org/dc/elements/1.1/")
dcterms=MyNamespace("http://purl.org/dc/terms/")

foaf=MyNamespace("http://xmlns.com/foaf/0.1/")

cito=MyNamespace("http://purl.org/spar/cito/")
fabio=MyNamespace("http://purl.org/spar/fabio/")

agent=MyNamespace("http://swan.mindinformatics.org/ontologies/1.2/agents/")
pav=MyNamespace("http://swan.mindinformatics.org/ontologies/1.2/pav/")

adsbase=ADSNamespace("ADS-Base.owl")
adsbib=ADSNamespace("ADS-bibo.owl")
adsobsv=ADSNamespace("ADS-obsv.owl")

aakeys=ADSNamespace("AAKeys.rdf")

ajkeys=ADSNamespace("AJKeys.rdf")
normalizedkeys=ADSNamespace("NormalizedKeys.rdf")
arxivkeys=ADSNamespace("ArxivKeys.rdf")
pacs=ADSNamespace("pacs.rdf")

#get basic configuration instances from below

ads_baseurl="http://ads.harvard.edu/sem"

uri_context=MyNamespace(ads_baseurl+"/context#")
uri_base=MyNamespace(ads_baseurl+"/base#")
uri_bib=MyNamespace(ads_baseurl+"/bib#")
uri_prop=MyNamespace(ads_baseurl+"/bib/prop#")
uri_obsv=MyNamespace(ads_baseurl+"/obsv#")
uri_obs=MyNamespace(ads_baseurl+"/obsv/obs#")
uri_dat=MyNamespace(ads_baseurl+"/obsv/dat#")
uri_meta=MyNamespace(ads_baseurl+"/meta#")
uri_agents=MyNamespace(ads_baseurl+"/agents#")
uri_conf=MyNamespace(ads_baseurl+"/conf#")

BASE=adsbase.namespace
a=rdf.type



namespace_dict = dict(
cito=cito.namespace,
fabio=fabio.namespace,
dc=dc.namespace,
dcterms=dcterms.namespace,
foaf=foaf.namespace,
rdf=rdf.namespace,
rdfs=rdfs.namespace,
xsd=xsd.namespace,
adsbase=adsbase.namespace,
agent=agent.namespace,
pav=pav.namespace,
adsbib=adsbib.namespace,
adsobsv=adsobsv.namespace,
skos=skos.namespace,
aakeys=aakeys.namespace,

pacs=pacs.namespace,
normalizedkeys=normalizedkeys.namespace,
arxivkeys=arxivkeys.namespace,
ajkeys=ajkeys.namespace,

uri_context=uri_context.namespace,
uri_base=uri_base.namespace,
uri_meta=uri_meta.namespace,
uri_bib=uri_bib.namespace,
uri_obsv=uri_obsv.namespace,
uri_conf=uri_conf.namespace,
uri_agents=uri_agents.namespace,
uri_obs=uri_obs.namespace,
uri_dat=uri_dat.namespace,
uri_prop=uri_prop.namespace,
)

def bindgraph(g):
    for ele in namespace_dict.keys():
        g.bind(ele,namespace_dict[ele])

def bindgraphold(g):
    g.bind('foaf', FOAF)
    g.bind('bibo', BIBO)
    g.bind('dc', DC) 
    g.bind('dct', DCT) 
    g.bind('ads', ADS)
    g.bind('rdf', RDF)
    g.bind('skos', SKOS)


def gadd(g, s, p, o):
    g.add((s,p,o))

def gbuild(g, tlist):
    if len(tlist) %  3 ==0:
        for i in range(len(tlist)):
            if i %3 ==0:
                gadd(g, tlist[i], tlist[i+1], tlist[i+2])

def gdadd(g, s, tlist):
    if len(tlist) %  2 ==0:
        for i in range(len(tlist)):
            if i %2 ==0:
                gadd(g, s, tlist[i], tlist[i+1])


def gdbnadd(g, s, p, tlist):
    bnode=BNode()
    gdadd(g, bnode, tlist)
    gadd(g, s, p, bnode)
    
def n3encode(theitem):
    namespace, endurl=theitem.split(':')
    return "<"+str(namespace_dict[namespace])+endurl+">"

# Since the values are stored as strings; we do a type conversion
# to check that the value is valid, but store the input string
# to avoid unnescessary numeric conversion.
#
def asInt(lit):
    "Create a literal node assuming integer input (i.e. store int(lit))"
    int(lit)
    return Literal(lit, datatype=XSD.integer)

def asFloat(lit):
    """Create a literal node assuming floating-point input (i.e. store float(lit)),
    as an xsd:float."""
    float(lit)
    return Literal(lit, datatype=XSD.float)

def asDouble(lit):
    """Create a literal node assuming floating-point input (i.e. store float(lit)),
    as an xsd:double."""
    float(lit)
    return Literal(lit, datatype=XSD.double)

"""
def asDate(lit):
    "Create a literal node using the XSD.date datatype"
parse as date
    return Literal(lit, datatype=XSD.date)
"""

def asDateTime(lit):
    """Create a literal node using the XSD.dateTime datatype.

    At present assumes a format of '1999-02-17 22:01:09' which
    may need to be extended.
    """

    dt = datetime.datetime.strptime(lit, '%Y-%m-%d %H:%M:%S')
    return Literal(dt)

def asDuration(lit):
    """Create a literal node using the XSD.duration datatype,
    described at http://www.w3.org/TR/xmlschema-2/#duration 

    lit is assumed to be in seconds.

    To simplify the conversion, the duration is split up to a
    maximum of days; ie we do not try to calculate the number
    of months or years (this should not be a common duration
    for our data).
    
    """

    dt = float(lit)
    if dt < 0:
        dt = abs(dt)
        outstr = "-P"
    elif dt > 0:
        outstr = "P"
    else:
        return Literal("PT0S", datatype=XSD.duration)

    (nd, r1) = divmod(dt, 24*3600)
    nd = int(nd)
    if nd > 0:
        outstr += "{0}D".format(nd)

    if r1 > 0:
        outstr += "T"

        (nh, r2) = divmod(r1, 3600)
        nh = int(nh)
        if nh > 0:
            outstr += "{0}H".format(nh)

        if r2 > 0:
            (nm, ns) = divmod(r2, 60)
            nm = int(nm)
            if nm > 0:
                outstr += "{0}M".format(nm)

            if ns > 0:
                outstr += "{0}S".format(ns)
                      
    return Literal(outstr, datatype=XSD.duration)
