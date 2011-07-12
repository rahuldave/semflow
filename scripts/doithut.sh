#adsrdf:
	python adsclassic2rdf.py ../mast-rdf ../AstroExplorer/Missions/MAST/hut/hut.biblist.txt
#simbadrdf:
	python simbad2rdf.py ../AstroExplorer/Missions/MAST/hut/hut.simbad.dict ../mast-rdf
	
# Order is important here	
#obsvrdf:
	python newmast/mast_obsvrdf.py hut ../AstroExplorer/Missions/MAST/hut/obscore.hut.psv 	
#pubrdf:

	python newmast/mast_pubrdf.py hut ../AstroExplorer/Missions/MAST/hut/map.hut.txt
#proprdf:
	echo None

#adsload:
	python loadfiles.py ../AstroExplorer/Missions/MAST/hut/hut.biblist.txt default2.conf
	
#simbadload:
	python loadfiles-simbad.py ../AstroExplorer/Missions/MAST/hut/hut.biblist.txt default2.conf
	
#obsvload:
	python newmast/mast_obsvload.py hut
	
#pubload:
	python newmast/mast_pubload.py hut

#propload:
	echo None
	
#pubsolr:
	python rdf2solr4.py MAST hut ../AstroExplorer/Missions/MAST/hut/hut.biblist.txt
