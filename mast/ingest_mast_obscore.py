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

def addVal(graph, subject, pred, obj, objconv=Literal):
    """If obj is not '' then add the following triple to the
    supplied graph:

    if objconv == None or obj is a URIRef
      (subject, pred, obj)

    else
      (subject, pred, objconv(obj))

    If you are adding a URIRef then may as well just use gadd()
    directly.
    
    """

    if isinstance(obj, URIRef):
        gadd(graph, subject, pred, obj)
        return
    
    if obj == '':
        return

    if objconv == None:
        gadd(graph, subject, pred, obj)
    else:
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

def cleanFragment(frag):
    """Given a piece of text we wish to use as an identifier,
    remove/replace un-wanted characters.

    White space is removed (fails if all whitespace).
    Converted to upper case.
    
    """

    ans = frag.replace(" ", "")
    if ans == "":
        raise ValueError("Input fragment is empty!")
    else:
        return ans.upper()
    

def addFragment(base, fragment):
    """Create a URI by combining base with fragment, after
    cleaning the fragment. base should be a namespace object."""

    return base[cleanFragment(fragment)]
    
def addObsCoreRow(row):
    """Returns a Graph representing the given row. We do not add it to the
    main graph here in case there is invalid data for this row. Perhaps
    it would be better to have all validity checks first and then add
    direcctly to the graph, since it may be faster once the main graph
    starts getting large (unlikely).

    Errors may be thrown if the input is invalid (e.g. unable to coerce
    a cell into the correct type).
    """

    vals = row2dict(row)

    # Try using the obs_id field as the identifier for the URI
    # fragment.
    #
    obs_id = vals['obs_id']
    if obs_id == '':
        raise ValueError("No obs_id value in this row!")
    
    urifrag = cleanFragment('MAST_' + obs_id)
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

                adsobsv.resolution, vals['s_resolution'], asFloat,
                adsobsv.tResolution, vals['t_resolution'], asFloat,

                # Units?
                adsobsv.wavelengthStart, vals['em_min'], asFloat,
                adsobsv.wavelengthEnd, vals['em_max'], asFloat,

                # We just use a string literal to store the target name; downstream
                # processing can try and improve this mapping.
                #
                # TODO: it seems that the predicate should be more descriptive
                # than adsbase.name.
                #
                adsbase.name, vals['target_name'], Literal,
                adsbase.title, vals['title'], Literal,
                
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

    sregion = vals['s_region']
    if sregion != '':
        predList = [
                a, adsobsv.FootPrint,
                adsobsv.s_region, Literal(sregion),
            ]
            
        gdbnadd(graph, obsuri, adsobsv.associatedFootprint, predList)

    # add _MAST_ to the URI fragment so that can identify them if necessary,
    # although MAST isn't the observatory itself
    #
    # TODO: work out what prefix to use; for now guessing uri_conf is okay,
    # since that's what the Chandra pipeline uses, but would uri_obsv be better?
    #
    tname = vals['telescope_name']
    iname = vals['instrument']
    if tname != '':
        gadd(graph, obsuri, adsobsv.atTelescope,
             addFragment(uri_conf, 'TELESCOPE_MAST_' + tname))

    if iname != '':
        gadd(graph, obsuri, adsbase.usingInstrument,
             addFragment(uri_conf, 'INSTRUMENT_MAST_' + iname))
        
    ### Data set properties
    #
    addVals(graph, daturi,
            [
                pav.createdOn, vals['creation_date'], asDateTime,
                adsobsv.dataURL, vals['access_url'], Literal, # TODO: surely this should allow a URI?
                adsobsv.calibLevel, vals['calib_level'], asInt,

                adsbase.dataType, vals['dataproduct_type'], Literal,

            ])

    # TODO:
    #   - need to come up with a scheme for collection and creator URIs
    #     (we assume that the name is an IFP for the object;
    #     ie it uniquely identifies the object). What about
    #     spelling errors/differences.
    #
    #   - should I replace / by some other character since it could
    #     confuse some parsers? Replace space with ?
    #
    #   - upper case all characters under the assumption that case
    #     is not important and that there may be differences in case
    #
    cname = vals['obs_creator_name']
    if cname != '':
        # Is this correct; ie is the obs_creator_name really
        # the same as observationMadeBy?
        #
        cnameuri = addFragment(uri_dat, 'MAST_CREATOR_' + cname)
        gadd(graph, obsuri, adsobsv.observationMadeBy, cnameuri)
        gdadd(graph, cnameuri, [
            a, agent.PersonName,
            agent.fullName, Literal(cname)
            ])

    ocoll = vals['obs_collection']
    if ocoll != '':
        colluri = addFragment(uri_dat, 'MAST_COLLECTION_' + ocoll)
        addVal(graph, daturi, adsobsv.fromDataCollection, colluri)
        gdadd(graph, colluri, [
            a, adsobsv.DataCollection,
            adsbase.name, Literal(ocoll)
            ])
        
    return graph

def writeObsCoreGraph(graph, fname, format="n3"):
    "Write the graph to the given file."

    output = graph.serialize(format=_fmts[format])

    fd = open(fname, "w")
    fd.write(output)
    fd.close()
    print "Created: " + fname

def makeGraph():
    "Returns a new graph."

    graph = ConjunctiveGraph(identifier=URIRef(ads_baseurl))
    bindgraph(graph)
    return graph

def getObsCoreFile(fname, ohead, nsplit=10000, format="n3"):
    """Convert the given obscore file from MAST (in psv format) into
    RDF.

    Rows that can not be converted are ignored (an error message is
    displayed on STDERR in this case).

    Since the input file is large we now split apart the output every
    nsplit rows. The output is written to
    
        ohead.<i>.<format>

    where i is a counter, starting at 1
    """

    fh = open(fname, "r")
    rdr = csv.reader(fh, dialect="psv")

    rnum = 0
    rpass = 0

    idx = 1
    graph = makeGraph()

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

        if rnum % nsplit == 0:
            # TODO: do we want to catch IO errors here?
            writeObsCoreGraph(graph, ohead + "." + str(idx) + "." + format,
                              format=format)
            idx += 1
            graph = makeGraph()
            
    fh.close()

    # write out the last elements, if necessary
    #
    if rnum % nsplit != 0:
        # TODO: do we want to catch IO errors here?
        writeObsCoreGraph(graph, ohead + "." + str(idx) + "." + format,
                          format=format)

    if rpass == 0:
        raise IOError("No rows were converted!")
    
    if rnum != rpass:
        print "NOTE: " + str(rnum-rpass) + " rows were not included!"

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
        ohead = "tests/mast/" + bname
        getObsCoreFile(fname, ohead, format=fmt)

    else:
        print "Usage: " + sys.argv[0] + " <filename> [rdf|n3]"
        sys.exit(-1)


