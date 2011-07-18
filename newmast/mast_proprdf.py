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

EUVE proposals are as IUE but without the last |N field:

99-036|A Deep EUVE Variability Study of the Seyfert Galaxy NGC 4051| Antonella|Fruscione|Harvard CfA/CXC|The Seyfert galaxy NGC~4051 is one of the brightest AGN in the EUV and X-ray sky. It is also one of the most rapidly variable. It is therefore an excellent candidate on which to study the origin of the EUV and X-ray emission in AGN. Its central black hole mass is quite small (approx 10e6 solar masses), making comparison with the behaviour of galactic black hole X-ray binary systems (BHXRBs) much easier than with other AGN with more massive black holes where characteristic variability timescales will be longer. Comptonisation of soft photons is a widely favoured possibility for the production of the X-ray/EUV emission in AGN. Here we propose to build on previous very successful coordinated EUVE and RXTE observations to further test the Comptonisation model and to investigate the similarities between AGN and BHXRBs. We propose to carry out a continuous 1 month EUVE observation to be coordinated with a 2 month RXTE programme of 4-times daily observations.

FUSE proposals have a different ordering:

A061|1| |JOHN|HUTCHINGS|Dominion Astrophysical Observatory, HIA, NRC of Canada, Cana|We propose FUSE observations of the brightest OB stars in the local group galaxies M31 and M33.  The stars are faint but their UV fluxes are known from HST and UIT data.  This will extend the stellar wind and interstellar studies currently under way with HST and ground-based telescopes, with similar resolution (1000) and S/N.  The program will expand our comparison of stellar winds, evolution, and the ISM among the major galaxies of the local group.

Z908|0| | |Andersson|FUSE Observatory Program|This program will obtain emission line spectra from 4 positions in the Vela SNR.
Z008|0| |Dr. Peter|Lundqvist|Stockholm Observatory|O VI emission from SN 1987A in the Large Magellanic Cloud will be observed to characterize the time dependence of the hot gas. The observation will be done on the LWRS aperture to obtain the total O VI flux from the SN environment.

so there's also different formats (case and inclusion of an honorific) in author names.

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
            (propid, title, pi_first, pi_last, place, remainder) = \
                line.split("|", 5)
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
    pi_first = pi_first.strip()
    if pi_first == "":
        qplabel = pi_last
        fullname = pi_last
        
    else:
        qplabel = pi_last + "_" + pi_first
        fullname = pi_last + ", " + pi_first

    return { "propid": propid,
             "title": title,
             "qplabel": qplabel,
             "fullname": fullname
             }
             
def add_proposal(graph, proposal, mission):
    """Add the proposal, returned by read_proposal, to
    the graph.

    At present we do not make use of

      author "place/affiliation"
      abstract

    """

    propid = proposal["propid"]
    title = proposal["title"]
    qplabel = proposal["qplabel"]
    fullname = proposal["fullname"]

    prop_uri = getPropURI(propid, mission)

    # TODO: may need more elaborate escaping
    qplabel = qplabel.replace(" ", "_")

    author_uri = uri_agents["PersonName/"+qplabel+"/"+str(uuid.uuid4())]

    addVals(graph, author_uri,
            [a, agent.PersonName, None,
             agent.fullName, fullname, Literal])
    #print type(title), propid, author_uri, title
    #adsbase.title, str(title.encode('utf-8')), Literal
    #BUG: munges characters, will have to do for now
    mungedtitle=title.decode('iso-8859-1').encode('utf-8')
    addVals(graph, prop_uri,
            [a, adsbase.ObservationProposal, None,
             adsobsv.observationProposalId, propid, Literal,
             adsobsv.observationProposalType, mission+"/None", Literal,
             adsbase.principalInvestigator, author_uri, None,
             adsbase.title, mungedtitle, Literal
             ]
            )
    
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
        ofname = datapath+"/proposals."+mission+"."+fmt + ".copy"
        
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
