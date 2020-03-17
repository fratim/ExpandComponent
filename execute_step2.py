
import growSomae
import sys
import dataIO
import os
import time
import glob
import numpy as np
import re
import struct

prefix = 'JWR'

if(len(sys.argv))!=4:
    raise ValueError(" Scripts needs exactley 3 input arguments (bz, by, bx)")
else:
    bz = int(sys.argv[1])
    by = int(sys.argv[2])
    bx = int(sys.argv[3])

print("bz by bx: " + str((bz,by,bx))

n_points_block = 0

print("Block: " + str((bz,by,bx)))

blocksize = dataIO.Blocksize(prefix)
sheet_size = blocksize[1]*blocksize[2]
row_size = blocksize[2]

print("Blocksize is: " + str(blocksize))

input_directory = "segments_out/"
output_directory = "blocks_out/"

filenames = sorted(glob.glob(input_directory+"*"))

labels_out = np.zeros((blocksize),dtype=np.uint64)

for fname in filenames:

    temp = fname.strip().split("-")

    if(len(temp)<4): continue

    bz_read = int(re.sub("[^0-9]", "", temp[-3]))
    by_read = int(re.sub("[^0-9]", "", temp[-2]))
    bx_read = int(re.sub("[^0-9]", "", temp[-1]))
    ID_in_fname = int(temp[-4])

    if bz_read != bz: continue
    if by_read != by: continue
    if bx_read != bx: continue

    print("reading: " + str(fname))

    blocksize_read = [-1,-1,-1]
    volumesize_read = [-1,-1,-1]
    ID_read = -1
    checksum_read = -1
    n_points = -1

    with open(fname, 'rb') as fd:
        volumesize_read[0], volumesize_read[1], volumesize_read[2], blocksize_read[0] = struct.unpack('qqqq', fd.read(32))
        blocksize_read[1], blocksize_read[2], ID_read, n_points = struct.unpack('qqqq', fd.read(32))

        # print("Read n_points: " + str(n_points))

        assert (tuple(volumesize_read) == dataIO.Volumesize(prefix))
        assert (tuple(blocksize_read) == blocksize)
        assert (ID_read == ID_in_fname)

        point_cloud_global = struct.unpack('%sq' % n_points, fd.read(8*n_points))
        point_cloud_local = struct.unpack('%sq' % n_points, fd.read(8*n_points))

        checksum_read = struct.unpack('q', fd.read(32))

        points_global = set(point_cloud_global)
        points_local = set(point_cloud_local)

        # if checksum_read[0]!=(sum(points_local)+sum(points_global)):
        #     print("ID is: " + str(ID_in_fname))
        #     print("checksum read is: " + str(checksum_read[0]))
        #     print("sum local is: " + str(sum(points_local)))
        #     print("sum global is: " + str(sum(points_global)))
        #     print("sum both is: "+ str((sum(points_local)+sum(points_global))))
        #
        #     raise ValueError("Checksum wrong")

        del points_global
        del point_cloud_global

    n_points_block+=n_points

    if len(points_local)>0:
        print("Block indices read: " + str((bz_read, by_read, bx_read)))
        print("ID read: " + str(ID_in_fname))

    for index in points_local:
        iz = index // sheet_size
        iy = (index - iz * sheet_size) // row_size
        ix = index % row_size

        labels_out[iz,iy,ix] = ID_read

print("n_points for block: " + str(n_points_block))

filename_out = "Zebrafinch-labels_discarded-"+str(bz).zfill(4)+"z-"+str(by).zfill(4)+"y-"+str(bx).zfill(4)+"x"+".h5"
dataIO.WriteH5File(labels_out, output_directory+filename_out, "main")
