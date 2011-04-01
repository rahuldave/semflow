#!/usr/bin/env python

"""
Create RDF/XML or N3 versions of the input file, which
is assumed to be in pipe-separated format and have no header line.

"""
DATA="../mast_hut-rdf"
import sys 

#import hashlib
import base64

from rdflib import URIRef, Literal, Graph

from namespaces import *
from psv import open_obscore, row2dict
from mast_utils import *

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

    # We use this as a hash and assume it is a unique value
    # (could check this assumption as we process the files, but
    # it was true in the original dataset).
    #
    # Originally I had used the obs_id cell as a unique identifier for
    # both observation and dataset, but it turned out not to be unique
    # enough. It may be that this is down to the modelling, where we try
    # to associate as much information as possible with the observation,
    # rather than the data product. If the observation were very light-weight
    # then we could keep this as an identifier for the observation, but
    # would still need unique identifiers for the data values.
    #
    # We reverse the access URL before hashing to try and reduce collisions.
    # This is a bit silly and needs replacing; for instance
    # we do not need this many characters and the current "hash" scheme isn't
    # very unique.
    #
    access_url = vals['access_url']
    if access_url.strip() == '':
        raise ValueError("Empty access_url for row")
    
    obs_id = vals['obs_id']
    if obs_id == '':
        raise ValueError("No obs_id value in this row!")
    
    # We use a scheme based on the path
    #    
    #    xxx/data/MAST/obsid/<obs_id>/<hash>
    #    xxx/observation/MAST/obsid/<obs_id>/<hash>
    #
    # where <hash> is a "hash" of the access_url value.
    # This is intentended to
    #   - reduce file sizes (e.g. use of slash rather than hash URI)
    #   - be more REST-ful in that we can define properties for parents
    #     of these URIs to manage and merge data
    #   - allow somewhat easier updates in case of changes - e.g to
    #     the data location because a server changes so access_url
    #     changes but nothing else does
    #
    uri_hash = base64.urlsafe_b64encode(access_url[::-1])
    daturi = mkURI("/obsv/data/MAST/obsid/{0}/".format(obs_id), uri_hash)
    obsuri = mkURI("/obsv/observation/MAST/obsid/{0}/".format(obs_id), uri_hash)
    
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
    emmin = vals['em_min']
    emmax = vals['em_max']

    addVals(graph, obsuri,
            [
                adsbase.atTime, vals['date_obs'], asDateTime(),
                # not convinced that observerTime is worth it, as a xsd:duration
                adsobsv.observedTime, vals['t_exptime'], asDuration,
                adsobsv.tExptime, vals['t_exptime'], asDouble,

                adsobsv.resolution, vals['s_resolution'], asDouble,
                adsobsv.tResolution, vals['t_resolution'], asDouble,

                adsobsv.wavelengthStart, emmin, asDouble,
                adsobsv.wavelengthEnd, emmax, asDouble,

                adsbase.title, vals['title'], Literal,
                
                adsobsv.fov, vals['s_fov'], asDouble,

            ])

    # For now we create a URI for each target_name and make
    # it an AstronomicalSourceName. We know that this is not
    # always "sensible", in that some names are not sources as
    # such but calibration values (e.g. '20% UV FLOOD' or
    # 'NULL SAFETY RD') or some scheme of the observer
    # which may be positional or something else (e.g. '+014381').
    #
    tname = vals['target_name'].strip()
    if tname != '':
        tnameuri = mkURI("/obsv/target/MAST/", tname)

        gadd(graph, obsuri, adsbase.target, tnameuri)
        addVals(graph, tnameuri,
                [
                    a, adsobsv.AstronomicalSourceName, None,
                    adsbase.name, tname, Literal,
                    ])

    # We do not use the em_domain field since the values found in
    # the MAST table do not appear to match the ObsCore/VODataService
    # enumerations. Instead we create values based on the em_min/max
    # fields. These could be inferred but worth being explicit here.
    #
    for domain in getEMDomains(float(emmin), float(emmax)):
        addVal(graph, obsuri, adsobsv.wavelengthDomain, domain)

    sra = vals['s_ra']
    sdec = vals['s_dec']
    if sra != '' and sdec != '':
        gdbnadd(graph, obsuri, adsobsv.associatedPosition,
                [
                    a, adsobsv.Pointing,
                    adsobsv.ra, asDouble(sra),
                    adsobsv.dec, asDouble(sdec),
                ])

    sregion = vals['s_region']
    if sregion != '':
        predList = [
                a, adsobsv.FootPrint,
                adsobsv.s_region, Literal(sregion),
            ]
            
        gdbnadd(graph, obsuri, adsobsv.associatedFootprint, predList)

    # TODO:
    #   - work out what prefix to use; for now guessing uri_conf is okay,
    #     since that's what the Chandra pipeline uses, but would uri_obsv be
    #     better? Alternatively, move to a scheme more like the other URIs
    #     we create here
    #
    tname = vals['telescope_name']
    iname = vals['instrument']
    oname="MAST"
    gadd(graph, obsuri, adsobsv.atObservatory,
             addFragment(uri_infra, 'observatory/' + oname))
    if tname != '':
        gadd(graph, obsuri, adsobsv.atTelescope,
             addFragment(uri_infra, 'telescope/MAST_' + tname))

    if iname != '':
        gadd(graph, obsuri, adsbase.usingInstrument,
             addFragment(uri_infra, 'instrument/MAST_' + iname))

    ### Data set properties
    #
    gadd(graph, daturi, adsobsv.dataURL, URIRef(access_url))
    #BUG: fix this to use a mapper
    dprodtype="image"#DEFAULT
    if vals['dataproduct_type'].find("Spectrum.") != -1:
        dprodtype="spectra"
    elif vals['dataproduct_type'].find("Image.") != -1:
        dprodtype="image"
    addVals(graph, daturi,
            [
                pav.createdOn, vals['creation_date'], asDateTime(),
                adsobsv.calibLevel, vals['calib_level'], asInt,

                adsbase.dataType, dprodtype, Literal, # could be a URI; how standardised are the values?
                adsobsv.dataFormat, vals['access_format'], Literal, # could be a URI; how standardised are the values?
            ])

    # Adding a link to the IVOA identifier for completeness.
    # Since this is the dataset identifier, we link it to the
    # dataset rather than the observation.
    #
    gadd(graph, daturi, adsbase.hasIVOAIdentifier,
         URIRef(vals['obs_publisher_did']))
        
    # The scheme for creator and collection URI is
    #
    #    xxx/creator/MAST/<obs_creator_name>
    #    xxx/collection/MAST/<obs_collection>
    #
    # although <obs_collection> can be an IVOA identifier, which means
    # we use that instead; this breaks linked-data approach, so perhaps
    # need a predicate to say "this represents this IVOA id" (could
    # use owl:sameAs but not convinced we want this).
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
        #cnameuri = mkURI("/obsv/creator/MAST/", cname)
        cnameuri=addFragment(uri_conf, 'project/MAST_' + cname)
        gadd(graph, obsuri, adsobsv.observationMadeBy, cnameuri)
        #gdadd(graph, cnameuri, [
        #    a, agent.PersonName,
        #    agent.fullName, Literal(cname)
        #    ])

    ocoll = vals['obs_collection']
    if ocoll != '':
        if is_ivoa_uri(ocoll):
            colluri = URIRef(ocoll)
        else:
            colluri = mkURI("/obsv/collection/MAST/", ocoll)

        addVal(graph, daturi, adsobsv.fromDataCollection, colluri)
        gdadd(graph, colluri, [
            a, adsobsv.DataCollection,
            adsbase.name, Literal(ocoll)
            ])

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

    (rdr, fh) = open_obscore(fname)

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
            sys.stderr.write("ERROR: row# {0}\n{1}\n".format(rnum, str(e)))

        if rnum % 500 == 0:
            print ("Processed row: {0}".format(rnum))

        if rnum % nsplit == 0:
            # TODO: do we want to catch IO errors here?
            writeGraph(graph,
                       "{0}.{1}.{2}".format(ohead, idx, format),
                       format=format)
            idx += 1
            graph = makeGraph()
            
    fh.close()

    # write out the last elements, if necessary
    #
    if rnum % nsplit != 0:
        # TODO: do we want to catch IO errors here?
        writeGraph(graph,
                   "{0}.{1}.{2}".format(ohead, idx, format),
                   format=format)

    if rpass == 0:
        raise IOError("No rows were converted!")
    
    if rnum != rpass:
        print ("NOTE: {0} rows were not included!".format(rnum-rpass))

if __name__=="__main__":
    nargs = len(sys.argv)
    if nargs in [2,3] :
        import os.path
        fname=sys.argv[1]
        if nargs == 2:
            fmt = "rdf"
        else:
            fmt = sys.argv[2]

        validateFormat(fmt)
        
        bname=os.path.basename(fname)
        ohead = DATA+"/" + bname
        getObsCoreFile(fname, ohead, format=fmt, nsplit=1000)

    else:
        sys.stderr.write("Usage: {0} <filename> [rdf|n3]\n".format(sys.argv[0]))
        sys.exit(-1)


