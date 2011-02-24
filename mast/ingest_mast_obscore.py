#!/usr/bin/env python

"""
Read in the MAST obscore file.

We assume the data is in pipe-separated format and has no
header line. The format is discussed below.

At present we output to a single file, but I think it would make sense to
create smaller files - perhaps trying to select groups of related rows
from the table itself or just bundle a set number of rows - to reduce
memory consumption/execution time.

The format is taken to be (from initial obscore tables in CSV format):

% head -1 obscore.csv | tr , '\n' | cat -n
     1  s_ra
     2  s_dec
     3  datalen
     4  radecsys
     5  equinox
     6  timesys
     7  specsys
     8  vover
     9  vodate
    10  target_name
    11  ra_targ
    12  dec_targ
    13  title
    14  obs_creator_name
    15  obs_collection
    16  obs_publisher_did
    17  obs_id
    18  creation_date
    19  version
    20  instrument
    21  dssource
    22  em_domain
    23  der_snr
    24  spec_val
    25  spec_bw
    26  spec_fil
    27  em_res_power
    28  date_obs
    29  t_exptime
    30  t_min
    31  t_max
    32  aperture
    33  telescope_name
    34  tmid
    35  fluxavg
    36  fluxmax2
    37  em_min
    38  em_max
    39  min_flux
    40  max_flux
    41  min_error
    42  max_error
    43  access_format
    44  access_url
    45  representative
    46  preview
    47  project
    48  spectralaxisname
    49  fluxaxisname
    50  spectralsi
    51  fluxsi
    52  spectralunit
    53  fluxunit
    54  fluxucd
    55  fluxcal
    56  coord_obs
    57  coord_targ
    58  s_ra_min
    59  s_ra_max
    60  s_dec_min
    61  s_dec_max
    62  s_resolution
    63  t_resolution
    64  s_region
    65  o_fluxucd
    66  calib_level
    67  dataproduct_type
    68  t_span
    69  s_fov
    70  filesize
    71  access_estsize

"""

import sys 

import csv

from namespaces import *

from rdflib import URIRef, Namespace, Literal, BNode, \
     ConjunctiveGraph, Graph

# utility routines (should probably move to namespaces)

# A dialect for pipe-separated values
class PSV(csv.Dialect):
    """Pipe-separated values (separator is |).

    At present all we really care about is the delimiter
    and lineterminator fields; the others are guesses.
    """
    
    delimiter = '|'
    doublequote = False
    escapechar = '\\'
    lineterminator = "\r\n"
    quotechar = None
    quoting = csv.QUOTE_NONE
    skipinitialspace = True # not sure about this one
    
csv.register_dialect("psv", PSV)

"""
From

head -1 obscore.csv | tr , '\n' | awk '{ printf "  \"%s\",\n", $1 }' -

"""

_colnames = [
  "s_ra",
  "s_dec",
  "datalen",
  "radecsys",
  "equinox",
  "timesys",
  "specsys",
  "vover",
  "vodate",
  "target_name",
  "ra_targ",
  "dec_targ",
  "title",
  "obs_creator_name",
  "obs_collection",
  "obs_publisher_did",
  "obs_id",
  "creation_date",
  "version",
  "instrument",
  "dssource",
  "em_domain",
  "der_snr",
  "spec_val",
  "spec_bw",
  "spec_fil",
  "em_res_power",
  "date_obs",
  "t_exptime",
  "t_min",
  "t_max",
  "aperture",
  "telescope_name",
  "tmid",
  "fluxavg",
  "fluxmax2",
  "em_min",
  "em_max",
  "min_flux",
  "max_flux",
  "min_error",
  "max_error",
  "access_format",
  "access_url",
  "representative",
  "preview",
  "project",
  "spectralaxisname",
  "fluxaxisname",
  "spectralsi",
  "fluxsi",
  "spectralunit",
  "fluxunit",
  "fluxucd",
  "fluxcal",
  "coord_obs",
  "coord_targ",
  "s_ra_min",
  "s_ra_max",
  "s_dec_min",
  "s_dec_max",
  "s_resolution",
  "t_resolution",
  "s_region",
  "o_fluxucd",
  "calib_level",
  "dataproduct_type",
  "t_span",
  "s_fov",
  "filesize",
  "access_estsize",
]

_ncols = len(_colnames)
_colmap = dict(zip(_colnames, range(0,_ncols)))

def check_row(row):
    """Ensure the number of columns is correct.

    We could also check other items but for now do not
    bother.
    """
    
    if len(row) != _ncols:
        raise ValueError("Row contains {0} columns, expected {1}!\n\n{2}\n".format(len(row), _ncols, row))

def get_column(row, cname):
    """Return the cell for the given column name from the row,
    which is expected to be the return value of a csv reader
    object.

    We assume that check_row() has already been called on this
    row.
    """

    try:
        return row[_colmap[cname]]

    except KeyError:
        raise ValueError("Invalid column name: {0}!".format(cname))

def row2dict(row):
    "Return a dictionary of key=column-name, value=column-value."

    check_row(row)
    return dict(zip(_colnames, row))

def addVal(graph, subject, pred, obj, objconv):
    """Add the triple

    (subject, pred, objconv(obj))

    to graph if obj is not == ''.
    """

    if obj == '':
        return

    gadd(graph, subject, pred, objconv(obj))

def addVals(graph, subject, plist):
    """Adds the given predicate list to the graph for
    the subject, where plist is an array of items of
    the form

      [p1, o1, c1, p2, o2, c2, ...]

    and the triple (subject, pi, ci(oi)) is added of
    oi is not ''.
    """

    np = len(plist)
    if np % 3 != 0:
        raise ValueError("plist does not contain groups of pred,obj,conv values")

    for i in range(0, np, 3):
        addVal(graph, subject, plist[i], plist[i+1], plist[i+2])
    
def addObsCoreRow(row):
    """Returns a Graph representing the given row.

    Errors may be thrown if the input is invalid (e.g. unable to coerce
    a cell into the correct type).

    TODO: need to handle missing values
    """

    vals = row2dict(row)

    # Try using the obs_id field as the identifier for the URI
    # fragment.
    #
    obs_id = vals['obs_id']
    if obs_id == '':
        raise ValueError("No obs_id value in this row!")
    
    urifrag = 'MAST_' + obs_id
    daturi = uri_dat[urifrag]
    obsuri = uri_obs[urifrag]

    graph = Graph()

    # Can we assume this is a SimpleObservation or could it be a
    # ComplexObservation? Not convinced we can tell, so
    # use the parent Observation class for now.
    #
    #gadd(graph, obsuri, a, adsobsv.SimpleObservation)
    gadd(graph, obsuri, a, adsobsv.Observation)

    # For now assuming we have a Datum rather than a DataSet;
    # we could use the parent SingularDataProdict but try
    # this.
    #
    gadd(graph, daturi, a, adsobsv.Datum)
    #gadd(graph, daturi, a, adsobsv.SingularDataProduct)

    #gadd(graph, obsuri, adsobsv.hasDatum, daturi)
    gadd(graph, obsuri, adsobsv.hasDataProduct, daturi)

    #gadd(graph, daturi, adsobsv.forSimpleObservation, obsuri)
    gadd(graph, daturi, adsobsv.forObservation, obsuri)

    # Qus: should we use obs_id for both here?
    gadd(graph, obsuri, adsobsv.observationId, Literal(obs_id))
    gadd(graph, daturi, adsobsv.dataProductId, Literal(obs_id))

    ### Observational properties
    #
    addVals(graph, obsuri,
            [
                adsbase.atTime, vals['date_obs'], asDateTime,
                adsobsv.observedTime, vals['t_exptime'], asFloat, # QUS: units?
                adsobsv.tExptime, vals['t_exptime'], asFloat, # QUS: units?

            ])
    
    # add _MAST_ to the URI fragment so that can identify them if necessary,
    # although MAST isn't the observatory itself
    #
    # TODO: work out what prefix to use; for now guessing uri_conf is okay,
    # since that's what the Chandra pipeline uses, but would uri_obsv be better?
    #
    tname = vals['telescope_name']
    iname = vals['instrument']
    if tname != '':
        gadd(graph, obsuri, adsobsv.atTelescope, uri_conf['TELESCOPE_MAST_' + tname])

    if iname != '':
        gadd(graph, obsuri, adsbase.usingInstrument, uri_conf['INSTRUMENT_MAST_' + iname])
        
    ### Data set properties
    #
    addVals(graph, daturi,
            [
                adsobsv.createdOn, vals['creation_date'], asDateTime,
                adsobsv.dataURL, vals['access_url'], Literal, # TODO: surely this should allow a URI?
                adsobsv.calibLevel, vals['calib_level'], asInt,

                adsbase.dataType, vals['dataproduct_type'], Literal,

                # Units?
                adsobsv.wavelengthStart, vals['em_min'], asFloat,
                adsobsv.wavelengthEnd, vals['em_max'], asFloat,
            ])

    sra = vals['s_ra']
    sdec = vals['s_dec']
    if sra != '' and sdec != '':
        gdbnadd(graph, obsuri, adsobsv.associatedPosition,
                [
                    a, adsobsv.Pointing,
                    adsobsv.ra, asFloat(sra),
                    adsobsv.dec, asFloat(sdec),
                ])

    # We assume that s_resolution is only present if s_region is.
    #
    sregion = vals['s_region']
    if sregion != '':
        predList = [
                a, adsobsv.RegionOfSky,
                adsobsv.fov, Literal(sregion),
            ]
        sres = vals['s_resolution']
        if sres != '':
            predList.extend([adsobsv.resolution, asFloat(sres)])
            
        gdbnadd(graph, obsuri, adsobsv.associatedFootprint, predList)

    # TODO:  is adsbase.title the correct predicate?
    #
    tname = vals['target_name']
    if tname != '':
          gdbnadd(graph, obsuri, adsobsv.target, [
              a, adsobsv.AstronomicalSource,
              adsbase.title, Literal(tname),
              ]
            )

    cname = vals['obs_creator_name']
    if cname != '':
        gdbnadd(graph, obsuri, adsobsv.observationMadeBy, [
            a, agent.PersonName,
            agent.fullName, Literal(cname)
            ]
        )

    # TODO:
    #   - is this semantically sensible
    #   - should the data or observation be associated with the collection?
    #     for now assume collection
    #   - is adsbase.title the right predicate
    #   - should we be clever and amalgamate all the nodes that refer to the
    #     same collection?
    #
    ocoll = vals['obs_collection']
    if ocoll != '':
        gdbnadd(graph, daturi, adsobsv.fromDataCollection, [
              a, adsobsv.DataCollection,
              adsbase.title, Literal(ocoll),
            ]
        )

    return graph

def getObsCoreFile(fname):
    """Convert the given obscore file from MAST (in psv format) into
    RDF.

    Rows that can not be converted are ignored (an error message is
    displayed on STDERR in this case).
    """

    graph = ConjunctiveGraph(identifier=URIRef(ads_baseurl))
    bindgraph(graph)

    fh = open(fname, "r")
    rdr = csv.reader(fh, dialect="psv")
    rnum = 0
    rpass = 0
    for row in rdr:
        rnum += 1
        try:
            gr = addObsCoreRow(row)
            graph += gr
            rpass += 1
        
        except Exception, e:
            print >> sys.stderr, "ERROR: row# " + str(rnum) + "\n" + str(e)

        if rnum % 100 == 0:
            print "Processed row: " + str(rnum)

    fh.close()
    print("Finished processing file.")
    return (graph, rnum, rpass)

_fmts = { "n3": "n3", "rdf": "xml" }

if __name__=="__main__":
    nargs = len(sys.argv)
    if nargs in [2,3] :
        import os.path
        fname=sys.argv[1]
        if nargs == 2:
            fmt = "rdf"
        else:
            fmt = sys.argv[2]

        if not(fmt in _fmts):
            raise ValueError("Invalid format '" + fmt + "'")
        
        bname=os.path.basename(fname)
        ofname="tests/mast/"+bname+"." + fmt
        (g, rnum, rsucc) = getObsCoreFile(fname)

        if rsucc == 0:
            raise IOError("No rows were converted!")

        output = g.serialize(format=_fmts[fmt])

        fd=open(ofname, "w")
        fd.write(output)
        fd.close()
        print "Created: " + ofname + " containing " + str(rsucc) + " rows."
        if rnum != rsucc:
            print "NOTE: " + str(rnum-rsucc) + " rows were not included!"
            
    else:
        print "Wrong usage", sys.argv
        sys.exit(-1)


"""
OLD CODE BELOW

def getObsFile(fname):
    g = ConjunctiveGraph(identifier=URIRef(ads_baseurl))
    bindgraph(g)
    recordstree=ElementTree.parse(fname)
    rootnode=recordstree.getroot()
    xobj=XMLObj(recordstree)
    trec={}
    trec['obsname']=rootnode.attrib['name']
    trec['obsid']=rootnode.attrib['obsid']
    trec['instrument_name']=xobj.elementAttribute('instrument', 'name')
    trec['obsvtype']=xobj.type
    trec['time']=xobj.observed_time
    trec['date']=xobj.start_date
    trec['ra']=xobj.ra
    trec['dec']=xobj.dec
    trec['proposal_id']=xobj.elementAttribute('proposal', 'id')
    #print trec
    obsuri=uri_obs['CHANDRA_'+trec['obsid']]
    daturi=uri_dat['CHANDRA_'+trec['obsid']]
    gadd(g, daturi, a, adsobsv.Datum)
    gadd(g, obsuri, a, adsobsv.SimpleObservation)
    gdadd(g, obsuri, [
            adsobsv.observationId, Literal(trec['obsid']),
            adsobsv.observationType, Literal(trec['obsvtype']),
            adsbase.atTime, Literal(trec['date']),
            adsobsv.observedTime, Literal(trec['time']),
            adsbase.atObservatory, uri_conf['OBSERVATORY_CHANDRA'],
            adsobsv.atTelescope,   uri_conf['TELESCOPE_CHANDRA'],
            adsbase.usingInstrument, uri_conf['INSTRUMENT_CHANDRA_'+trec['instrument_name']],
            adsobsv.hasDatum, daturi,
            adsbase.asAResultOfProposal, uri_prop['CHANDRA_'+trec['proposal_id']]
        ]
    )
    gdadd(g, daturi, [
            adsobsv.dataProductId, Literal(trec['obsid']),
            adsobsv.forSimpleObservation, obsuri
        ]
    )
    gdbnadd(g, obsuri, adsobsv.associatedPosition, [
            a, adsobsv.Pointing,
            adsobsv.ra, Literal(trec['ra']),
            adsobsv.dec, Literal(trec['dec'])
        ]
    )
    serializedstuff=g.serialize(format='xml')
    return serializedstuff
    
def getPubFile(fname):
    g = ConjunctiveGraph(identifier=URIRef(ads_baseurl))
    bindgraph(g)
    recordstree=ElementTree.parse(fname)
    rootnode=recordstree.getroot()
    xobj=XMLObj(recordstree)
    trec={}
    trec['bibcode']=xobj.bibcode
    trec['classified_by']=xobj.classified_by
    #this above coild also be figured by bibgroup
    #shouldnt this be a curated statement. But what is the curation. Not a source curation
    #later.
    trec['paper_type']=xobj.paper_type
    #trec['obsids']=[e.text for e in xobj.rec.findall('data')[0].findall('obsid')]
    boolobsids=False
    if len(xobj.rec.findall('data'))> 0:
        if len(xobj.rec.findall('data')[0].findall('obsid'))> 0:
            print "1"
            trec['obsids']=[e.text for e in xobj.rec.findall('data')[0].findall('obsid')]
            boolobsids=True
    else:
        print "2"
        trec['obsids']=[]
    #print trec
    bibcode_uri = uri_bib[trec['bibcode']]
    print bibcode_uri
    for obsid in trec['obsids']:
        obsuri=uri_obs['CHANDRA_'+obsid]
        daturi=uri_dat['CHANDRA_'+obsid]
        gadd(g, bibcode_uri, adsbase.aboutScienceProcess, obsuri)
        gadd(g, bibcode_uri, adsbase.aboutScienceProduct, daturi)
        gadd(g, bibcode_uri, adsobsv.datum_p, Literal(str(boolobsids).lower()))
        #This is temporary. must map papertype to scienceprocesses and use those ones exactly
        gadd(g, bibcode_uri, adsbib.paperType, Literal(trec['paper_type']))
        
    serializedstuff=g.serialize(format='xml')
    return serializedstuff

def getObsIdsForPubs(fname):
    recordstree=ElementTree.parse(fname)
    rootnode=recordstree.getroot()
    xobj=XMLObj(recordstree)
    trec={}
    trec['bibcode']=xobj.bibcode
    #print trec['bibcode']
    
    if len(xobj.rec.findall('data'))> 0:
        if len(xobj.rec.findall('data')[0].findall('obsid'))> 0:
            trec['obsids']=[e.text for e in xobj.rec.findall('data')[0].findall('obsid')]
            for ele in trec['obsids']:
                print trec['bibcode'], ele
    else:
        print trec['bibcode'], "NOTHING"
    
def getPropFile(fname):
    g = ConjunctiveGraph(identifier=URIRef(ads_baseurl))
    bindgraph(g)
    recordstree=ElementTree.parse(fname)
    rootnode=recordstree.getroot()
    xobj=XMLObj(recordstree)
    trec={}
    trec['propname']=rootnode.attrib['name']
    trec['propid']=rootnode.attrib['id']
    trec['title']=xobj.title
    trec['category']=xobj.category
    #we used a proposalType here, as this is somewhat different from justscienceprocess. add to ontology
    trec['abstract']=xobj.abstract
    trec['pi']=[xobj.elementAttribute('pi', 'last'),xobj.elementAttribute('pi', 'first')]
    #print trec
    propuri=uri_prop['CHANDRA_'+trec['propid']]
    #This is FALSE. TODO..fix to ads normed name or lookitup How? Blanknode? WOW.
    qplabel=trec['pi'][0]+'_'+trec['pi'][1]
    auth_uri = uri_agents[qplabel]
    gadd(g, propuri, a, adsbase.ObservationProposal)
    gdadd(g, propuri, [
            adsobsv.observationProposalId, Literal(trec['propid']),
            adsobsv.observationProposalType, Literal("CHANDRA/"+trec['category']),
            adsbase.principalInvestigator, auth_uri,
            adsbase.title, Literal(trec['title'])
        ]
    )
    serializedstuff=g.serialize(format='xml')
    return serializedstuff

def getPropIdsForObs(fname):
    recordstree=ElementTree.parse(fname)
    rootnode=recordstree.getroot()
    xobj=XMLObj(recordstree)
    trec={}
    trec['obsid']=rootnode.attrib['obsid']
    trec['proposal_id']=xobj.elementAttribute('proposal', 'id')
    print trec['obsid'],trec['proposal_id']
    
dafunc={
'obsv':getObsFile,
'pub':getPubFile,
'prop':getPropFile,
'obsids':getObsIdsForPubs,
'propids':getPropIdsForObs
}    
if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[2] in dafunc.keys():
        #getObsFile(sys.argv[1])
        import os.path
        fname=sys.argv[1]
        bname=os.path.basename(fname)
        style=sys.argv[2]
        ofname="tests/chandrastart/"+style+"/"+bname+".rdf"
        output=dafunc[style](fname)
        #getPubFile(sys.argv[1])
        if style in ['obsv', 'pub', 'prop']:
            fd=open(ofname, "w")
            fd.write(output)
            fd.close()
    else:
        print "Worong usage", sys.argv
        sys.exit(-1)

"""
