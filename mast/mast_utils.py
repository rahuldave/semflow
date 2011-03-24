"""
Utilities for processing MAST data.

"""

from namespaces import ads_baseurl, bindgraph

from rdflib import URIRef, ConjunctiveGraph

_fmts = { "n3": "n3", "rdf": "xml" }

def validateFormat(format):
    "Throws a ValueError if format is unsupported."
    
    if format in _fmts:
        return

    raise ValueError("Invalid format '{0}' - must be one of {1}".format(format, " ".join(_fmts.keys())))

def writeGraph(graph, fname, format="n3"):
    "Write the graph to the given file."

    output = graph.serialize(format=_fmts[format])

    fd = open(fname, "w")
    fd.write(output)
    fd.close()
    print("Created: {0}".format(fname))

def makeGraph():
    "Returns a new graph."

    graph = ConjunctiveGraph(identifier=URIRef(ads_baseurl))
    bindgraph(graph)
    return graph

