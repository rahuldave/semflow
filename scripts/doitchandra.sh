#adsrdf:
    python adsclassic2rdf.py ../chandra-rdf ../AstroExplorer/Missions/Chandra/chandra/sherry.p.a.biblist.txt
    python adsclassic2rdf.py ../chandra-rdf ../AstroExplorer/Missions/Chandra/chandra/hutoverlap.biblist.txt
    
#simbadrdf:
    python simbad2rdf.py ../AstroExplorer/Missions/Chandra/chandra/sherry.p.a.simbad.dict ../chandra-rdf
    python simbad2rdf.py ../AstroExplorer/Missions/Chandra/chandra/hutoverlap.simbad.dict ../chandra-rdf
    
#pubrdf:
    python chandra/genrdf.py pub ../AstroExplorer/Missions/Chandra/chandra/sherry.p.a.linkedpubs.txt ../chandra-rdf/
    python chandra/genrdf.py pub ../AstroExplorer/Missions/Chandra/chandra/hutoverlap.linkedpubs.txt ../chandra-rdf/
    
#obsvrdf:
    python chandra/genrdf.py obsv ../AstroExplorer/Missions/Chandra/chandra/global.obsids.txt ../chandra-rdf/
    
#proprdf:
    python chandra/genrdf.py prop ../AstroExplorer/Missions/Chandra/chandra/global.proposals.txt ../chandra-rdf/
    
    
#adsload:    
    python loadfiles.py ../AstroExplorer/Missions/Chandra/chandra/sherry.p.a.biblist.txt
    python loadfiles.py ../AstroExplorer/Missions/Chandra/chandra/hutoverlap.biblist.txt
    
#simbadload:
    python loadfiles-simbad.py ../AstroExplorer/Missions/Chandra/chandra/sherry.p.a.biblist.txt
    python loadfiles-simbad.py ../AstroExplorer/Missions/Chandra/chandra/hutoverlap.biblist.txt
    
#pubload:
    python chandra/loadfiles.py ../AstroExplorer/Missions/Chandra/chandra/sherry.p.a.linkedpubs.txt pub
    python chandra/loadfiles.py ../AstroExplorer/Missions/Chandra/chandra/hutoverlap.linkedpubs.txt pub

#obsvload:
    python chandra/loadfiles.py ../AstroExplorer/Missions/Chandra/chandra/global.obsids.txt obsv
    
#propload:
    python chandra/loadfiles.py ../AstroExplorer/Missions/Chandra/chandra/global.proposals.txt prop
    
    
#We had to produce a cut file below due to some linkage probs in Chandra
#pubsolr:
    #python solrclear.py #is doing this first
    #python rdf2solr4.py CHANDRA chandra ../AstroExplorer/Missions/Chandra/chandra/sherry.p.a.biblist.txt.cut 
    #python rdf2solr4.py CHANDRA chandra ../AstroExplorer/Missions/Chandra/chandra/hutoverlap.biblist.txt
