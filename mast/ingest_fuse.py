#from namespaces import *
from psv import open_obscore, row2dict
from mast_utils import *
import string

#Kayleigh says no changes are needed to stock ingest file

def getObsidForPubMap(obsid):
    return string.upper(obsid)
    
def getObsCoreFile(fname):
    """
    Takes psv format file, returns a dict with keys the filenames to use, the values
    an array of tuples for that filename, each tuple, the vals, anbool, where anbool says is
    info is taken from corresponding vals. vals is the conversion of the psv row into a dict.
    """
    
    (rdr, fh) = open_obscore(fname)

    rnum = 0
    rpass = 0

    idx = 1
    
    globalrowdict={}
    h_at={}
    for row in rdr:
        vals=row2dict(row)
        obs_id = vals['obs_id']
        h_at[obs_id]=[(vals, 1)]
            
                    
            
    fh.close()    
    return h_at    
