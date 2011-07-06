import gzip
import sys
SORTEDYEARLIST='sortedyearlist.txt'
DEFAULTPATH='../AstroExplorer/filebibs/'
from sets import Set


def setupAlts(defaultpath,altfile):
    dbhash={}
    fd=open(defaultpath+altfile)
    pairs=[line.strip().split() for line in fd.readlines()]
    for ele in pairs:
        dbhash[ele[0].strip()]=ele[1].strip()
    fd.close()
    return dbhash
    

   
def storeYears(sortedyearlistfile):
    dbhash={}
    for line in open(sortedyearlistfile):
        year, value = line.strip().split()
        if not dbhash.has_key(year):
            dbhash[year]=[]
        dbhash[year].append(value)
    return dbhash

def openset(thefile, dbhash):
    for line in gzip.open(DEFAULTPATH+thefile+".gz"):
        bibcode,theuuid = line.strip().split()
        dbhash[bibcode]=theuuid

def setsFromBibcodes(bibcodefile, yearhash):
    #dh=setupAlts(DEFAULTPATH,'bmap.txt')
    dbhash={}
    bibcodehash={}
    fileset=Set()
    bibcodesiwant=[]
    for line in open(bibcodefile):
        bibcode = line.strip()
        bibcodesiwant.append(bibcode)
        bibyear=bibcode[0:4]
        filelist=yearhash[bibyear]
        print "filelist",filelist
        for ele in filelist:
            fileset.add(ele)
    print "FILESET", fileset
    print "BIBCODESIWANT",bibcodesiwant
    for everyfile in fileset:
        print everyfile
        openset(everyfile, bibcodehash)		
    for bcode in bibcodesiwant:
        dbhash[bcode]=bibcodehash[bcode]
        #if not dh.has_key(bcode):
        #    dbhash[bcode]=bibcodehash[bcode]
        #else:
        #    dbhash[bcode]=bibcodehash[dh[bcode]]
    return dbhash

if __name__=='__main__':
    filename=sys.argv[1]	
    yhash=storeYears(DEFAULTPATH+SORTEDYEARLIST)
    dbhash=setsFromBibcodes(filename,  yhash)
    for ele in dbhash.keys():
        print ele, dbhash[ele]
