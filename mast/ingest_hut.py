from namespaces import *
from psv import open_obscore, row2dict
from mast_utils import *

def getObsidForPubMap(obsid):
    return obsid.split('=')[0]
    
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
        at_time="_".join(vals['date_obs'].split())
        if obs_id == '':
            raise ValueError("No obs_id value in this row!")
        access_url = vals['access_url']
        access_name=access_url.split('/')[-1].split('_ph_')[0]
        if access_name.find('_sum') !=-1:
            access_name=access_name.split('_sum')[0]
        anbool=1
        if access_name.find('_imcscor')!=-1:
            access_name=access_name.split('_imcscor')[0]
            anbool=0
        #print "access url", access_url
        if access_url.strip() == '':
            raise ValueError("Empty access_url for row")
        dayfind=access_url.find(obs_id+"_d")
        nightfind=access_url.find(obs_id+"_n")
        afind=access_url.find(obs_id+"_a")
        if dayfind!=-1:
            d2key=obs_id+"_d"
            #dkey=obs_id#lets not to day separately
        elif afind!=-1:
            d2key=obs_id+"_a"
        elif nightfind!=-1:
            d2key=obs_id+"_a"
        else:
            d2key=obs_id
            
        #dkey=obs_id+"--"+access_name
        dkey=obs_id
        if not globalrowdict.has_key(dkey):
            globalrowdict[dkey]=[]
        globalrowdict[dkey].append((vals, at_time, access_name, d2key, anbool))
    
    #print "LLLLL"    
    for dkey in globalrowdict.keys():
        print "grd", dkey, len(globalrowdict[dkey])
        dalen=len(globalrowdict[dkey])
        h_an={}
        for ele in globalrowdict[dkey]:
            vals, at_time, access_name, d2key, anbool=ele
            print "time",at_time, dkey, access_name, anbool
            if not h_an.has_key(access_name):
                h_an[access_name]=[]
            if anbool==1 or dalen==1:
                h_an[access_name].append((ele, at_time))
            else:
                h_an[access_name].append((ele, None))
        #print "han", h_an
        h_an2={}        
        for item in h_an.keys():
            #Sprint "hanitem", h_an[item]
            thetimelist=[e[1] for e in h_an[item] if e[1]!=None]
            if len(thetimelist)>=1:
                thetime=thetimelist[0]
            else:
                #This happens like in pupaeast when there is only imscor
                print "OOOOOOOOOOOOOOOPS", len(thetimelist)
            h_an2[item]=[(e[0],thetime) for e in h_an[item]]
        print "deekee",dkey
        for k in h_an2.keys():
            for item in h_an2[k]:
                #print "<<<",item[0][0],">>>"
                if not h_at.has_key(dkey+"="+item[1]):
                    h_at[dkey+"="+item[1]]=[]
                h_at[dkey+"="+item[1]].append((item[0][0], item[0][4]))
                #add the anbool and vals in here
                #unbool tells you which row contains the information we ought to use
                #in this case not imscor. in default case anbool=1 for everything.
            
                    
            
    fh.close()    
    return h_at    
