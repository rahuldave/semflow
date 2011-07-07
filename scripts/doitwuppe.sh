#adsrdf:
	python adsclassic2rdf.py ../mast-rdf ../AstroExplorer/Missions/MAST/wuppe/wuppe.biblist.txt
#simbadrdf:
	python simbad2rdf.py ../AstroExplorer/Missions/MAST/wuppe/wuppe.simbad.dict ../mast-rdf
	
# Order is important here	
#obsvrdf:
	python newmast/mast_obsvrdf.py wuppe ../AstroExplorer/Missions/MAST/wuppe/obscore.wuppe.psv 	
#pubrdf:

	python newmast/mast_pubrdf.py wuppe ../AstroExplorer/Missions/MAST/wuppe/map.wuppe.txt
#proprdf:
	echo None

#adsload:
	python loadfiles.py ../AstroExplorer/Missions/MAST/wuppe/wuppe.biblist.txt default2.conf
	
#simbadload:
	python loadfiles-simbad.py ../AstroExplorer/Missions/MAST/wuppe/wuppe.biblist.txt
	 default2.conf
	
#obsvload:
	python newmast/mast_obsvload.py wuppe
	
#pubload:
	python newmast/mast_pubload.py wuppe

#propload:
	echo None
	
#pubsolr:
#	python rdf2solr4.py MAST wuppe ../AstroExplorer/Missions/MAST/wuppe/wuppe.biblist.txt
