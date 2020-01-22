
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

# reassemble blocks
# for bz in range(start_blocks[0], start_blocks[0]+n_blocks[0]):
#     for by in range(start_blocks[1], start_blocks[1]+n_blocks[1]):
#         for bx in range(start_blocks[2], start_blocks[2]+n_blocks[2]):
#
# for bz in range(start_blocks[0], 2):
#     for by in range(start_blocks[1], 2):
#         for bx in range(start_blocks[2], 2):
#
#             n_points_block = 0
#
#             print("Block: " + str((bz,by,bx)))
#
#             blocksize = dataIO.Blocksize(prefix)
#             sheet_size = blocksize[1]*blocksize[2]
#             row_size = blocksize[2]
#
#             print("Blocksize is: " + str(blocksize))
#
#             input_directory = "segments_out/"
#             output_directory = "blocks_out/"
#
#             filenames = sorted(glob.glob(input_directory+"*"))
#
#             labels_out = np.zeros((blocksize),dtype=np.uint64)
#
#             for fname in filenames:
#
#                 temp = fname.strip().split("-")
#
#                 if(len(temp)<4): continue
#
#                 bz_read = int(re.sub("[^0-9]", "", temp[-3]))
#                 by_read = int(re.sub("[^0-9]", "", temp[-2]))
#                 bx_read = int(re.sub("[^0-9]", "", temp[-1]))
#                 ID_in_fname = int(temp[-4])
#
#                 if bz_read != bz: continue
#                 if by_read != by: continue
#                 if bx_read != bx: continue
#
#                 # print("Block indices read: " + str((bz_read, by_read, bx_read)))
#                 # print("ID read: " + str(ID_in_fname))
#
#                 blocksize_read = [-1,-1,-1]
#                 volumesize_read = [-1,-1,-1]
#                 ID_read = -1
#                 checksum_read = -1
#                 n_points = -1
#
#                 with open(fname, 'rb') as fd:
#                     volumesize_read[0], volumesize_read[1], volumesize_read[2], blocksize_read[0] = struct.unpack('qqqq', fd.read(32))
#                     blocksize_read[1], blocksize_read[2], ID_read, n_points = struct.unpack('qqqq', fd.read(32))
#
#                     # print("Read n_points: " + str(n_points))
#
#                     assert (tuple(volumesize_read) == dataIO.Volumesize(prefix))
#                     assert (tuple(blocksize_read) == blocksize)
#                     assert (ID_read == ID_in_fname)
#
#                     point_cloud_global = struct.unpack('%sq' % n_points, fd.read(8*n_points))
#                     point_cloud_local = struct.unpack('%sq' % n_points, fd.read(8*n_points))
#
#                     checksum_read = struct.unpack('q', fd.read(32))
#
#                     points_global = set(point_cloud_global)
#                     points_local = set(point_cloud_local)
#
#                     assert(checksum_read[0]==(sum(points_local)+sum(points_global)))
#
#                     del points_global
#                     del point_cloud_global
#
#                 n_points_block+=n_points
#
#                 for index in points_local:
#
#                     iz = index // sheet_size
#                     iy = (index - iz * sheet_size) // row_size
#                     ix = index % row_size
#
#                     labels_out[iz,iy,ix] = ID_read
#
#             print("n_points for block: " + str(n_points_block))
#
#             filename_out = "Zebrafinch-labels_discarded-"+str(bz).zfill(4)+"z-"+str(by).zfill(4)+"y-"+str(bx).zfill(4)+"x"+".h5"
#             dataIO.WriteH5File(labels_out, output_directory+filename_out, "main")
