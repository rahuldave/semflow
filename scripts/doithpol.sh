#adsrdf:
	python adsclassic2rdf.py ../mast-rdf ../AstroExplorer/Missions/MAST/hpol/hpol.biblist.txt
#simbadrdf:
	python simbad2rdf.py ../AstroExplorer/Missions/MAST/hpol/hpol.simbad.dict ../mast-rdf
	
# Order is important here	
#obsvrdf:
	python newmast/mast_obsvrdf.py hpol ../AstroExplorer/Missions/MAST/hpol/obscore.hpol.psv 	
#pubrdf:

	python newmast/mast_pubrdf.py hpol ../AstroExplorer/Missions/MAST/hpol/map.hpol.txt
#proprdf:
	echo None

#adsload:
	python loadfiles.py ../AstroExplorer/Missions/MAST/hpol/hpol.biblist.txt default2.conf
	
#simbadload:
	python loadfiles-simbad.py ../AstroExplorer/Missions/MAST/hpol/hpol.biblist.txt default2.conf
	
#obsvload:
	python newmast/mast_obsvload.py hpol
	
#pubload:
	python newmast/mast_pubload.py hpol

#propload:
	echo None
	
#pubsolr:
	python rdf2solr4.py MAST hpol ../AstroExplorer/Missions/MAST/hpol/hpol.biblist.txt	`
