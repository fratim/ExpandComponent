import growSomae
import sys
import dataIO
import os
import time

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
<<<<<<< HEAD
=======

>>>>>>> f61e2ec99da4389dccef869818646c383f3851bf
for bz in (start_blocks[0], start_blocks[0]+n_blocks[0]):
    for by in (start_blocks[1], start_blocks[1]+n_blocks[1]):
        for bx in (start_blocks[2], start_blocks[2]+n_blocks[2]):

            print("Block: " + str((bz,by,bx)))

<<<<<<< HEAD
            blocksize = dataIO.Blocksize(prefix)
            sheet_size = blocksize[1]*blocksize[2]
            row_size = blocksize[2]

            print("Blocksize is: " + str(blocksize))

            input_directory = "output_v1/segments_out/"
            output_directory = "output_v1/blocks_out/"
            filenames = sorted(glob.glob("input_directory"+"*"))

            labels_out = np.zeros((blocksize),dtype=np.uint64)

            for fname in filenames:

                print(fname)
                temp = fname.strip().split(",")

                if temp[1] != bz: continue
                if temp[2] != by: continue
                if temp[3] != bx: continue

                print("reading this file")

                blocksize_read = (-1,-1,-1)
                volumesize_read = (-1,-1,-1)
                ID_read = -1
                checksum_read = -1
                n_points = -1

                with open(fname, 'rb') as fd:
                    volumesize_read[0], volumesize_read[1], volumesize_read[2], blocksize_read[0], blocksize_read[2], blocksize_read[3], ID_read, n_points_read = struct.unpack('qqqq', fd.read(8*8))

                    assert (volumesize_read == dataIO.Volumesize(prefix))
                    assert (blocksize_read == blocksize)

                    point_cloud_global = struct.unpack('%sq' % npoints, fd.read(8 * npoints))
                    point_cloud_local = struct.unpack('%sq' % npoints, fd.read(8 * npoints))

                    checksum_read = struct.unpack('qqqq', fd.read(8))

                    del point_cloud_global
                    points_local = set(point_cloud_local)

                    assert(checksum_read==sum(points_local))

                for index in points_local:

                    iz = index / sheet_size
                    iy = (index - iz * sheet_size) / row_size
                    ix = index % row_size

                    labels_out[iz,iy,ix] = ID_read

            filename_out = "Zebrafinch-labels_discarded-"+str(bz).zfill(4)+"z-"+str(by).zfill(4)+"y-"+str(bx).zfill(4)+"x"+".h5"
            dataIO.WriteH5File(labels_out, output_directory+filename_out, "main")
=======
            input_directory = "segments_out/"

            # get the grid size for this prefix
            zres, yres, xres = dataIO.GridSize(prefix)

            point_cloud = set(dataIO.ReadPoints(prefix, label, 'segmentations'))

            surface_points = FindSurface(point_cloud, zres, yres, xres)

            surface_filename = 'surfaces/{}/{:06d}.pts'.format(prefix, label)
>>>>>>> f61e2ec99da4389dccef869818646c383f3851bf
