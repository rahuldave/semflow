#adsrdf:
	python adsclassic2rdf.py ../mast-rdf ../AstroExplorer/Missions/MAST/fuse/fuse.biblist.txt
	
#simbadrdf:
	python simbad2rdf.py ../AstroExplorer/Missions/MAST/fuse/fuse.simbad.dict ../mast-rdf
	
# Order is important here	
#obsvrdf:
	python newmast/mast_obsvrdf.py fuse ../AstroExplorer/Missions/MAST/fuse/obscore.fuse.psv 
		
#pubrdf:
	python newmast/mast_pubrdf.py fuse ../AstroExplorer/Missions/MAST/fuse/map.fuse.txt
	
#proprdf:
	python newmast/mast_proprdf.py fuse ../AstroExplorer/Missions/MAST/fuse/fuse_program.list

#adsload:
	python loadfiles.py ../AstroExplorer/Missions/MAST/fuse/fuse.biblist.txt default2.conf
	
#simbadload:
	python loadfiles-simbad.py ../AstroExplorer/Missions/MAST/fuse/fuse.biblist.txt default2.conf
	
#obsvload:
	python newmast/mast_obsvload.py fuse
	
#pubload:
	python newmast/mast_pubload.py fuse

#propload:
	python newmast/mast_propload.py fuse
	
#pubsolr:
	python rdf2solr4.py MAST fuse ../AstroExplorer/Missions/MAST/fuse/fuse.biblist.txt
