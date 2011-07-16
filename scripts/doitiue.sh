#adsrdf:
	python adsclassic2rdf.py ../mast-rdf ../AstroExplorer/Missions/MAST/iue/iue.biblist.txt
	
#simbadrdf:
	python simbad2rdf.py ../AstroExplorer/Missions/MAST/iue/iue.simbad.dict ../mast-rdf
	
# Order is important here	
#obsvrdf:
	python newmast/mast_obsvrdf.py iue ../AstroExplorer/Missions/MAST/iue/obscore.iue.psv 
		
#pubrdf:
	python newmast/mast_pubrdf.py iue ../AstroExplorer/Missions/MAST/iue/map.iue.txt
	
#proprdf:
	python newmast/mast_proprdf.py iue ../AstroExplorer/Missions/MAST/iue/iue_program.list

#adsload:
	python loadfiles.py ../AstroExplorer/Missions/MAST/iue/iue.biblist.txt default2.conf
	
#simbadload:
	python loadfiles-simbad.py ../AstroExplorer/Missions/MAST/iue/iue.biblist.txt default2.conf
	
#obsvload:
	python newmast/mast_obsvload.py iue
	
#pubload:
	python newmast/mast_pubload.py iue

#propload:
	python newmast/mast_propload.py iue
	
#pubsolr:
	python rdf2solr5.py MAST iue ../AstroExplorer/Missions/MAST/iue/iue.biblist.txt
