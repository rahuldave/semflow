#loadfiles
__version__="0.1"
import os.path, sys
import random

import os.path, sys, os, glob

bibcodes=[ele.strip() for ele in open(sys.argv[1]).readlines()]
#print bibcodes
newbibcodes=random.sample(bibcodes, 60)
for ele in newbibcodes:
	print ele
