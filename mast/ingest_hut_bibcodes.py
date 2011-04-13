#!/usr/bin/env python

"""
Read in the HUT bibliographic data; we also require the obscore table
to support mapping between the records.

"""
#DATA="../mast_hut-rdf"
import sys 

#import hashlib
import urllib
import base64

from psv import open_obscore, get_column
from namespaces import *

from rdflib import URIRef, Graph
import rdflib

from mast_utils import *

def getBibliography(fname):
    """Extract the <bibcode obsid> values from fname."""

    fh = open(fname, "r")
    out = {}
    for l in fh.readlines():
        args = l.strip().split()
        if len(args) != 2:
            print("SKIPPING: [{0}]".format(l))

        else:
            bibcode = args[0]
            obsid = args[1]
            try:
                out[obsid].append(bibcode)

            except KeyError:
                out[obsid] = [bibcode]

    fh.close()
    return out

def writeBibliographyFile(fname, ohead, bibcodes, format="n3"):
    """Write out bibliographic records using the obscore table in fname.

    bibcodes is a dictionary with key: obsid, value: list of bibcodes.

    The output is written to
    
        ohead.<format>

    """

    (rdr, fh) = open_obscore(fname)

    graph = makeGraph()

    nbib = 0
    for row in rdr:

        obs_id = get_column(row, "obs_id")
        access_url = get_column(row, "access_url")
        thedate="_".join(get_column(row, "date_obs").split())
        for (k,bs) in bibcodes.iteritems():
            # The HUT bibcodes appear to use obsid values which are
            # prefixes of the obscore ones.
            #
            if not obs_id.startswith(k):
                continue

            # Create the URIs that represent the data and observation objects from
            # the obscore table.
            #
            uri_hash = base64.urlsafe_b64encode(access_url[::-1])
            #daturi = mkURI("/obsv/MAST/obsid/{0}/data/".format(obs_id), uri_hash)
            #obsuri = mkURI("/obsv/MAST/obsid/{0}/observation/".format(obs_id), uri_hash)
            daturi = mkURI("/obsv/data/MAST/obsid/{0}/".format(obs_id+"-"+thedate), uri_hash)
            #obsuri = mkURI("/obsv/observation/MAST/obsid/{0}/".format(obs_id), uri_hash)
            obsuri = mkURI("/obsv/observation/MAST/obsid/{0}/".format(obs_id+"-"+thedate))
            # Loop through each bibcode, linking them to the data/observation URIs
            #
            for b in bs:
                biburi = URIRef(ads_baseurl + "/bib#" + cleanFragment(b))
                gadd(graph, biburi, adsbase.aboutScienceProduct, daturi)
                gadd(graph, biburi, adsbase.aboutScienceProcess, obsuri)


            nbib += len(bs)
            print("# bibcodes = {0}".format(nbib))

    fh.close()

    writeGraph(graph, "{0}.{1}".format(ohead, format), format=format)


def writeBibliographyFile2(fname, ohead, bibcodes, format="n3"):
    """Write out bibliographic records using the hash in fname.

    bibcodes is a dictionary with key: obsid, value: list of bibcodes.

    The output is written to
    
        ohead.<format>

    """

    hms=open(fname).read()
    hmd=eval(hms)
    graph = makeGraph()

    nbib = 0
    for row in hmd.keys():

        obsuri=row
        obs_id=str(obsuri).split("/")[-1].split('=')[0]
        for daturi in hmd[obsuri]:
            for (k,bs) in bibcodes.iteritems():
                # The HUT bibcodes appear to use obsid values which are
                # prefixes of the obscore ones.
                #
                if not obs_id.startswith(k):
                    continue

                for b in bs:
                    biburi = URIRef(ads_baseurl + "/bib#" + cleanFragment(b))
                    gadd(graph, biburi, adsbase.aboutScienceProduct, daturi)
                    gadd(graph, biburi, adsbase.aboutScienceProcess, obsuri)


                nbib += len(bs)
                print("# bibcodes = {0}".format(nbib))



    writeGraph(graph, "{0}.{1}".format(ohead, format), format=format)
        
if __name__=="__main__":
    execfile("./mast/default.conf")
    nargs = len(sys.argv)
    if nargs in [3,4,5] :
        import os.path
        oname = sys.argv[1]
        bname = sys.argv[2]
        if nargs < 5:
            fmt = "rdf"
        else:
            fmt = sys.argv[4]

        validateFormat(fmt)
        if nargs >3:
            execfile(sys.argv[3])
        else:
            execfile("./mast/default.conf")
        bibcodes = getBibliography(bname)
        writeBibliographyFile2(DATA+"/"+oname,
                              DATA+"/" + os.path.basename(bname),
                              bibcodes, format=fmt)

    else:
        sys.stderr.write("Usage: {0} <MAST obscore map> <HUT bibcode> [conffile] [rdf|n3]\n".format(sys.argv[0]))
        sys.exit(-1)


