#!/usr/bin/env python

"""
Read in the MAST bibliographic data; we also require the obscore table
to support mapping between the records.

"""
#DATA="../mast_hut-rdf"
import sys, os, os.path

#import hashlib
import urllib
import base64

from psv import open_obscore, get_column
from namespaces import *

from rdflib import URIRef, Graph
import rdflib

from mast_utils import *

def getBibliography(fname):
    """Extract the <bibcode obsid> values from fname.

    Any obsid remapping stored in fname+'.rename' will be applied.
    """

    fh = open(fname, "r")
    out = {}
    for l in fh.readlines():
        args = l.strip().split()
        if len(args) not in [2,3]:
            print("SKIPPING: [{0}]".format(l))

        else:
            bibcode = args[0]
            # convert obsid to lower case for use in writeBibliographyFile2
            obsid = args[1]
            obsid = obsid.lower()
            if len(args)==3:
                program=args[2]
            else:
                program=None
            try:
                out[obsid].append((bibcode, program))

            except KeyError:
                out[obsid] = [(bibcode, program)]

    fh.close()

    adjustBibliographyMap(out, fname)
    return out

def adjustBibliographyMap(bmap, fname):
    """Given the output of getBibliography, apply any obsid changes
    in the mapping file fname + '.rename'. If the file does not exist
    then do nothing.
    """

    try:
        fh = open(fname + '.rename', 'r')

    except IOError:
        return

    for l in fh.readlines():
        l = l.strip()
        if l == '' or l[0] == '#':
            continue

        args = l.split()
        if len(args) != 2:
            print("WARNING: skipping obsid rename line '{0}'".format(l))
            continue

        # NOTE: have to lower-case all obsid values
        old = args[0].lower()
        new = args[1].lower()

        try:
            m = bmap[old]

        except KeyError:
            print("WARNING: obsid from rename file not in bibliographic map: {0}".format(old))
            continue

        del bmap[old]
            
        try:
            bmap[new].extend(m)

        except KeyError:
            bmap[new] = m

    fh.close()
    
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


def writeBibliographyFile2(mission, hashmapfname, ohead, bibcodes, missionmapfunc, format="n3"):
    """Write out bibliographic records using the hash in fname.

    bibcodes is a dictionary with key: obsid, value: list of bibcodes.

    The output is written to
    
        ohead.<format>

    """

    hms=open(hashmapfname).read()
    hmd=eval(hms)
    graph = makeGraph()

    nbib = 0
    for row in hmd.keys():

        obsuri=row
        obs_id=missionmapfunc(str(obsuri).split("/")[-1]).lower()
        for daturi in hmd[obsuri]:
            for (k,bs) in bibcodes.iteritems():
                # Many MAST bibcodes appear to use obsid values which are
                # prefixes of the obscore ones; there may also be case differences
                # which we paper over by making both lower case (a bit excessive,
                # since it is likely that the obscore-derived values are in lower
                # case, but just in case). The lower casing of the keys in bibcodes
                # is done on data entry (by getBibliography).
                #
                if not obs_id.startswith(k):
                    #print "NSW", obs_id, k
                    continue
                print "Got here", obs_id, k
                for b in bs:
                    biburi = URIRef(ads_baseurl + "/bib#" + b[0])
                    gadd(graph, biburi, adsbase.aboutScienceProduct, daturi)
                    gadd(graph, biburi, adsbase.aboutScienceProcess, obsuri)
                    if b[1]!=None:
                        propuri=uri_prop['MAST/'+mission+'/propid/'+b[1]]
                        gadd(graph, obsuri, adsbase.asAResultOfProposal, propuri)

                nbib += len(bs)
                print("# bibcodes = {0}".format(nbib))



    writeGraph(graph, "{0}.{1}".format(ohead, format), format=format)
        
if __name__=="__main__":
    mastmission = sys.argv[1]
    execfile("./newmast/default.conf")
    execfile("./mast/ingest_"+mastmission+".py")
    nargs = len(sys.argv)
    if nargs in [3,4,5] :
        oname = DATA+"/"+mastmission+"/obsdatahash.map"
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

        ofname="map."+mastmission
        writeBibliographyFile2(mastmission, DATA+"/"+oname,
                              DATA+"/" + mastmission+"/"+ofname,
                              bibcodes, getObsidForPubMap, format=fmt)

    else:
        sys.stderr.write("Usage: {0} <MAST MISSION> <MISSION PUB MAPFILE> [conffile] [rdf|n3]\n".format(sys.argv[0]))
        sys.exit(-1)


