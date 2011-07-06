#!/usr/bin/env python2.4
import sys
from ads.SIMBAD import Client

def getForBibcode(bibcode):
    SimbadClient = Client()
    SimbadClient.bibcode = bibcode
    SimbadClient.getObjects()
    if SimbadClient.error:
        print "ERROR", bibcode, SimbadClient.error
        return -1
    return SimbadClient.objects

if __name__=="__main__":
    thefilename=sys.argv[1]
    bibcodes=[ele.rstrip() for ele in open(thefilename).readlines()]
    bdict={}
    for bcode in bibcodes:
        result=getForBibcode(bcode)
        if result != -1:
            bdict[bcode]=result
    print bdict
