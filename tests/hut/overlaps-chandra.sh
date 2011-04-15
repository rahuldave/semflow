python loadfiles.py tests/hut/hut-chandra-overlap.txt
python loadfiles-simbad.py tests/hut/hut-chandra-overlap.txt
python chandra/loadfiles-pub.py tests/hut/hut-chandra-overlap.txt /pub
python chandra/loadfiles-obsv.py tests/hut/obsids.overlap.txt /obsv
python chandra/loadfiles-prop.py tests/hut/prop.overlap.txt /prop
python rdf2solr3.py tests/hut/hut-chandra-overlap.txt 
#not sure we need above these would come from hut

