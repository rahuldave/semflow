#!/usr/bin/env python

"""
Adapted from Doug's IUE ingest script for proposals'

Dougs old docs
Read in an IUE proposal list and spit out RDF.

It is based on the chandra/obsids.py script.

Parsing of a proposal line is left to mast_proprdf_<mission>.py

"""

import sys 
import os, os.path
import uuid

from rdflib import Literal

from namespaces import a, uri_prop, uri_agents, agent, adsbase, adsobsv, addVals, addVal
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
    return uri_prop['MAST/'+mission+'/propid/'+propid]

# hack to support breaks in the title
#
proposal_store = None

def read_proposal(fh):
    """Read in a proposal from the given file handle,
    returning a dictionary in the format needed by
    add_proposal.

    The proposal may span multiple lines.

    None is returned if there is no more data in the
    file handle.

    """

    global proposal_store

    flag = True
    while flag:
        text = fh.readline()
        if text == "":
            if proposal_store == None:
                return None
            else:
                raise IOError("Proposal expected to continue but EOF: {0}".format(proposal_store))

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
            fields = splitProposalLine(line)
            flag = False

        except ValueError:
            #print("Skipping line: " + text)
            #return False
            print("INFO: Creating proposal store for: " + line)
            proposal_store = line

    # try to match Chandra behavior but note difference in the
    # "first name" field since here it can be blank or contain spaces,
    # such as "Michael L."
    #
    # also, surnames can contain spaces too.
    #
    # note: we reject any fields with first-name only
    #
    out = { "propid": fields["propid"] }

    try:
        pi_last = fields["pi_last"]

        try:
            pi_first = fields["pi_first"]

            out["qplabel"] = pi_last + "_" + pi_first
            out["fullname"] = pi_last + ", " + pi_first

        except KeyError:

            out["qplabel"] = pi_last
            out["fullname"] = pi_last

    except KeyError:
        # pass
        if fields.has_key("pi_first"):
            print("DBG: proposal has pi_first but no pi_last: {0}".format(fields))

        #print("DBG: Proposal {0} has no PI name.".format(fields))

    try:
        out["title"] = fields["title"]

    except KeyError:
        pass

    return out
             
def add_proposal(graph, proposal, mission):
    """Add the proposal, returned by read_proposal, to
    the graph.

    At present we do not make use of

      author "place/affiliation"
      abstract

    """

    # We require propid but the rest is optional
    propid = proposal["propid"]
    prop_uri = getPropURI(propid, mission)
    addVals(graph, prop_uri,
            [a, adsbase.ObservationProposal, None,
             adsobsv.observationProposalId, propid, Literal,
             adsobsv.observationProposalType, mission+"/None", Literal
             ])

    try:
        title = proposal["title"]
        #BUG: munges characters, will have to do for now
        mungedtitle = title.decode('iso-8859-1').encode('utf-8')
        addVal(graph, prop_uri, adsbase.title, mungedtitle, Literal)

    except KeyError:
        pass

    try:
        qplabel = proposal["qplabel"]
        # TODO: may need more elaborate escaping
        qplabel = qplabel.replace(" ", "_")

        author_uri = uri_agents["PersonName/"+qplabel+"/"+str(uuid.uuid4())]
        fullname = proposal["fullname"]
        addVals(graph, author_uri,
                [a, agent.PersonName, None,
                 agent.fullName, fullname, Literal])
        addVal(graph, prop_uri, adsbase.principalInvestigator, author_uri, None)

    except KeyError:
        pass

if __name__=="__main__":

    nargs = len(sys.argv)
    if nargs in [3, 4, 5]:
        mission=sys.argv[1]

        # load in mission-specific proposal parsing code
        mfile = "newmast/mast_proprdf_{0}.py".format(mission)
        execfile(mfile)

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
        while True:
            prop = read_proposal(ifh)
            if prop == None: break
            add_proposal(graph, prop, mission)

        ifh.close()
        writeGraph(graph, ofname, format=fmt)

    else:
        sys.stderr.write("Usage: {0} <mission> <filename> [conffile] [rdf|n3]\n".format(sys.argv[0]))
        sys.exit(-1)
