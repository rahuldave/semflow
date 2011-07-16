#adsrdf:
	python adsclassic2rdf.py ../mast-rdf ../AstroExplorer/Missions/MAST/euve/euve.biblist.txt
	
#simbadrdf:
	python simbad2rdf.py ../AstroExplorer/Missions/MAST/euve/euve.simbad.dict ../mast-rdf
	
# Order is important here	
#obsvrdf:
	python newmast/mast_obsvrdf.py euve ../AstroExplorer/Missions/MAST/euve/obscore.euve.psv 
		
#pubrdf:
	python newmast/mast_pubrdf.py euve ../AstroExplorer/Missions/MAST/euve/map.euve.txt
	
#proprdf:
	python newmast/mast_proprdf.py euve ../AstroExplorer/Missions/MAST/euve/euve_program.list

#adsload:
	python loadfiles.py ../AstroExplorer/Missions/MAST/euve/euve.biblist.txt default2.conf
	
#simbadload:
	python loadfiles-simbad.py ../AstroExplorer/Missions/MAST/euve/euve.biblist.txt default2.conf
	
#obsvload:
	python newmast/mast_obsvload.py euve
	
#pubload:
	python newmast/mast_pubload.py euve

#propload:
	python newmast/mast_propload.py euve
	
#pubsolr:
	python rdf2solr5.py MAST euve ../AstroExplorer/Missions/MAST/euve/euve.biblist.txt
