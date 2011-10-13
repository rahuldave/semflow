#v2: This contains the connected stuff
#rdf2solr
import nose
import adsrdf
import pysolr
from urllib import unquote, quote_plus
import uuid, sys
import HTMLParser, datetime, calendar
from namespaces import n3encode
import rdflib

# as we are assuming python 2.6 we can use set() rather than Set()
# from sets import Set

import time
import logging
import re

from rdf2solarfuncs import getTailFromSplit
logger = None
bibcode='2000ApJ...534L..47G'
#bibcode='1993ApJ...410L.119V'
bibcode='2001ApJ...549..554A'
bibcodeuri='uri_bib:'+bibcode
execfile('./default.conf')
sesame = adsrdf.ADSConnection(SESAME, REPOSITORY)
theobsiduris=sesame.getDataBySP(bibcodeuri, 'adsbase:aboutScienceProcess')
obsray=[]

#daprops=['obsids_s','obsvtypes_s','exptime_f','obsvtime_d','instruments_s', 'telescopes_s', 'emdomains_s',  'targets_s', 'ra_f','dec_f', 'datatypes_s']
print "THEOBSIDURIS", theobsiduris
mission='CHANDRA'
project='chandra'
for theuri in theobsiduris:
    print theuri
    themission, theproject, theobsid, junkdataid, uritail=getTailFromSplit(mission, project, theuri)
    print themission, theproject, theobsid, junkdataid, uritail
    obstypes=sesame.getDataBySP('uri_obs:'+uritail, 'adsobsv:observationType')
    print obstypes, ":::"
    tvals = sesame.getDataBySP('uri_obs:'+uritail, 'adsobsv:tExptime')
    print "UTITAIL", uritail, tvals
#solr=pysolr.Solr(SOLR)
