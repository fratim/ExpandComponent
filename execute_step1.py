
import growSomae
import sys
import dataIO
import os
import time
import glob
import numpy as np
import re
import struct

prefix = 'Zebrafinch'

# pass arguments
if(len(sys.argv))!=2:
    raise ValueError(" ERROR")
else:
    query_comp = int(sys.argv[1])

start_blocks = dataIO.StartBlocks(prefix)
n_blocks = dataIO.NBlocks(prefix)

start_time = time.time()
growSomae.growFromPoint(  prefix, query_comp, start_blocks[0],start_blocks[1],start_blocks[2],
                    start_blocks[0]+n_blocks[0]-1,start_blocks[1]+n_blocks[1]-1,start_blocks[2]+n_blocks[2]-1)
print("time component " + str(query_comp) + ": " + str(time.time()-start_time))
