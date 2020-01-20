import growSomae
import sys
import dataIO
import os
import time

prefix = 'Zebrafinch'

start_blocks = dataIO.StartBlocks(prefix)
n_blocks = dataIO.NBlocks(prefix)

start_time = time.time()

for query_comp in [48]:
    growSomae.growFromPoint(  prefix, dataIO.OutputDirectory(prefix), query_comp, start_blocks[0],start_blocks[1],start_blocks[2],
                        start_blocks[0]+n_blocks[0]-1,start_blocks[1]+n_blocks[1]-1,start_blocks[2]+n_blocks[2]-1)

print("total time: " + str(time.time()-start_time))
