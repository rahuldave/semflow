#!/usr/bin/env python

"""
Adapted from Doug's IUE ingest script for proposals'

Dougs old docs
Read in an IUE proposal list and spit out RDF.

It is based on the chandra/obsids.py script.

The IUE proposal list looks like

OD89K|Observing the Earth|Ralph C.|Bohlin|STScI|Abstract unavailable|N

where the 'Abstract unavailable' can be filled in with the abstract
text and this text can contain | characters. Note that the proposal
title can contain \n (at least it does for proposal id OD88Z).


"""

import sys 
import os, os.path
import uuid

from rdflib import Literal

from namespaces import a, uri_prop, uri_agents, agent, adsbase, adsobsv, addVals
from mast_utils import makeGraph, validateFormat, writeGraph

#DATA = "../mast_hut-rdf"

#def getObsURI(obsid, fragment=None):
#    if fragment:
#        return uri_obs['CHANDRA/obsid/'+obsid+"/"+fragment]
#    return uri_obs['CHANDRA/obsid/'+obsid]
    
#def getDatURI(obsid, fragment=None):
#    if fragment:
#        return uri_dat['CHANDRA/obsid/'+obsid+"/"+fragment]
#    return uri_dat['CHANDRA/obsid/'+obsid]

# For now assuming that the proposal id is unique within MAST;
# this could be changed.
def getPropURI(propid, mission):
    return uri_prop['MAST/propid/'+mission+'/'+propid]

# hack to support breaks in the title
#
proposal_store = None
    
def add_proposal(graph, text, mission):
    """Add the proposal, stored in the line of text, to
    the graph.

    The routine returns True if the line as added to the
    graph, False if it was not fully processed.

    At present we do not make use of

      author "place/affiliation"
      abstract

    """

    global proposal_store

    line = text.strip()

    if proposal_store != None:
        if proposal_store[-1] == ' ':
            line = proposal_store + line
        else:
            line = proposal_store + " " + line

        print("INFO: -> " + line)
        proposal_store = None

    # I wonder if | characters in the abstract have been cleaned/protected?
    # Of course, some abstracts do contain | which means we need a slightly
    # more-complex algotithm than text.strip().split("|").
    #
    # Fortunately we do nothing with the abstract and flag for now so can
    # ignore. Given that we now support multi-line entries using a very-simple
    # hack there is the possibility that this will produce garbage output.
    # will worry about that if we find it.
    #
    try:
        (propid, title, pi_first, pi_last, place, abstract_and_flag) = \
                 line.split("|", 5)
 
    except ValueError:
        #print("Skipping line: " + text)
        #return False
        print("INFO: Creating proposal store for: " + line)
        proposal_store = line
        return False

    pi_first = pi_first.strip()

    # It is unclear what the flag field is, since it is not just a
    # way of indicating a missing abstract.
    
    #nflag = flag == "N"
    #nabs  = abstract == "Abstract unavailable"

    #if (nflag and not nabs) or (not nflag and nabs):
    #    print("NOTE: flag=" + flag + " abstract=" + abstract)

    # try to match Chandra behavior but note difference in the
    # "first name" field since here it can be blank or contain spaces,
    # such as "Michael L."
    #
    # also, surnames can contain spaces too.
    #
    prop_uri = getPropURI(propid, mission)

    if pi_first == "":
        qplabel = pi_last
        fullname = pi_last
        
    else:
        qplabel = pi_last + "_" + pi_first
        fullname = pi_last + ", " + pi_first

    # TODO: may need more elaborate escaping
    qplabel = qplabel.replace(" ", "_")

    author_uri = uri_agents["PersonName/"+qplabel+"/"+str(uuid.uuid4())]

    addVals(graph, author_uri,
            [a, agent.PersonName, None,
             agent.fullName, fullname, Literal])

    addVals(graph, prop_uri,
            [a, adsbase.ObservationProposal, None,
             adsobsv.observationProposalId, propid, Literal,
             adsbase.principalInvestigator, author_uri, None,
             adsbase.title, title, Literal
             ]
            )
    
    return True

if __name__=="__main__":

    nargs = len(sys.argv)
    if nargs in [3, 4, 5]:
        mission=sys.argv[1]
        fname = sys.argv[2]
        bname = os.path.basename(fname)
        
        if nargs == 4:
            fmt = sys.argv[3]
        else:
            fmt = "rdf"

        validateFormat(fmt)

        if nargs >= 4:
            execfile(sys.argv[3])
        else:
            execfile("./newmast/default.conf")

        #DATA = "../mast_" + mission + "-rdf"

        # ohead = DATA + "/" + bname
        # odhfname = DATA + "/obsdatahash.map"
        datapath=DATA+'/'+mission
        if not os.path.isdir(datapath):
            os.makedirs(datapath)
        ofname = datapath+"/proposals."+mission+"."+fmt
        
        ifh = open(fname, "r")
        graph = makeGraph()
        for txt in ifh:
            add_proposal(graph, txt, mission)

        ifh.close()
        writeGraph(graph, ofname, format=fmt)

    else:
        sys.stderr.write("Usage: {0} <mission> <filename> [conffile] [rdf|n3]\n".format(sys.argv[0]))
        sys.exit(-1)
