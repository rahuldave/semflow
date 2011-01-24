import pysolr

SOLR='http://localhost:8983/solr'


conn = pysolr.Solr('http://127.0.0.1:8983/solr/')
conn.delete(q='*:*')
