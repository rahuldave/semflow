import sys
DEFAULTPATH='../AstroExplorer/filebibs/'

def setupAlts(defaultpath,altfile):
    dbhash={}
    fd=open(DEFAULTPATH+altfile)
    pairs=[line.strip().split() for line in fd.readlines()]
    for ele in pairs:
        dbhash[ele[0].strip()]=ele[1].strip()
    fd.close()
    return dbhash
    
if __name__=='__main__':
    dh=setupAlts(DEFAULTPATH, 'bmap.txt')
    #print len(dh.keys())
    bfile=sys.argv[1]
    if len(sys.argv)==2:
        mode='report'
    else:
        mode=sys.argv[2]
    fd=open(bfile)
    bcodes=[line.strip() for line in fd.readlines()]
    #print bcodes
    fd.close()
    for ele in bcodes:
        if mode=="report":
            if dh.has_key(ele):
                print ele, dh[ele]
        elif mode=="print":
            if dh.has_key(ele):
                print dh[ele]
            else:
                print ele