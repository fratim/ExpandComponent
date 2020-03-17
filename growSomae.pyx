
import os
import time


cimport cython
cimport numpy as np
import ctypes
import numpy as np

import dataIO

cdef extern from 'cpp-growSomae.h':
    void CppGetcomponentFromPointlist(const char *prefix, long *inp_indices, long *inp_indices_somae, long n_indices, long n_indices_somae, long query_ID, long inp_blocksize[3], long volume_size[3]);


def growFromPoint(prefix, query_ID, block_z_start, block_y_start, block_x_start, block_z_end, block_y_end, block_x_end):

    print("----------------------------------------")
    print("Query ID is: " + str(query_ID))
    print("Prefix is: " + prefix)

    index_list = []
    index_list_somae = []

    if prefix =="Zebrafinch":
        for bz in range(block_z_start, block_z_end+1):
            print("bz is: " + str(bz))
            for by in range(block_y_start, block_y_end+1):
                for bx in range(block_x_start, block_x_end+1):

                    # read in segmentation
                    fileName = dataIO.InputlabelsDirectory(prefix)+"/Zebrafinch-input_labels-"+str(bz).zfill(4)+"z-"+str(by).zfill(4)+"y-"+str(bx).zfill(4)+"x"+".h5"
                    labels_in = dataIO.ReadH5File(fileName)
                    dsp_factor = 1
                    point_list = dataIO.getPointList(labels_in, dataIO.Blocksize(prefix), dataIO.Volumesize(prefix), bz, by, bx, query_ID, dsp_factor)
                    index_list = index_list + point_list
                    del point_list

                    # read in somae
                    fileNamesomae = dataIO.SomaeDirectory(prefix)+"/" + prefix + "/Zebrafinch-somae_refined_dsp8-"+str(bz).zfill(4)+"z-"+str(by).zfill(4)+"y-"+str(bx).zfill(4)+"x.h5"
                    labels_in_somae = dataIO.ReadH5File(fileNamesomae)
                    dsp_factor = 8
                    point_list_somae = dataIO.getPointList(labels_in_somae, dataIO.Blocksize(prefix), dataIO.Volumesize(prefix), bz, by, bx, query_ID, dsp_factor)
                    index_list_somae = index_list_somae + point_list_somae
                    del point_list_somae

                    print("len index list: " + str(len(index_list)))
                    print("len index list somae: " + str(len(index_list_somae)))


    if prefix == "JWR":
        for bz in range(block_z_start, block_z_end+1):
            print("bz is: " + str(bz))
            for by in range(block_y_start, block_y_end+1):
                for bx in range(block_x_start, block_x_end+1):

                    # read in segmentation

                    print("reading labels from: " )
                    fileName = dataIO.InputlabelsDirectory(prefix)+"/JWR-"+str(bz).zfill(4)+"z-"+str(by).zfill(4)+"y-"+str(bx).zfill(4)+"x"+".h5"
                    labels_in = dataIO.ReadH5File(fileName)
                    dsp_factor = 1
                    point_list = dataIO.getPointList(labels_in, dataIO.Blocksize(prefix), dataIO.Volumesize(prefix), bz, by, bx, query_ID, dsp_factor)
                    index_list = index_list + point_list
                    del point_list

                    # read in somae
                    fileNamesomae = dataIO.SomaeDirectory(prefix)+"/" + prefix + "/JWR-somae_filled_refined_dsp4-"+str(bz).zfill(4)+"z-"+str(by).zfill(4)+"y-"+str(bx).zfill(4)+"x.h5"
                    labels_in_somae = dataIO.ReadH5File(fileNamesomae)
                    dsp_factor = 4
                    point_list_somae = dataIO.getPointList(labels_in_somae, dataIO.Blocksize(prefix), dataIO.Volumesize(prefix), bz, by, bx, query_ID, dsp_factor)
                    index_list_somae = index_list_somae + point_list_somae
                    del point_list_somae

                    print("len index list: " + str(len(index_list)))
                    print("len index list somae: " + str(len(index_list_somae)))

    # g = open("pointlists_out/pointlist_"+str(query_ID)+".txt", "w+")
    # for entry in index_list:
    #     g.write(str(int(entry)).zfill(25)+"\n")
    # g.close()
    #
    # g = open("pointlists_out/pointlist_somae_"+str(query_ID)+".txt", "w+")
    # for entry in index_list_somae:
    #     g.write(str(int(entry)).zfill(25)+"\n")
    # g.close()

    if len(index_list)==0 or len(index_list_somae)==0:
        print("ERROR")
        print("len index list segment: " + str(len(index_list)))
        print("len index list somae: " + str(len(index_list_somae)))
        raise ValueError("Either list is empty - aborting")

    cdef long cpp_query_ID = query_ID

    # index_table = np.genfromtxt("pointlist_" + str(query_ID) + ".txt", delimiter=',',invalid_raise=True)
    index_table = np.asarray(index_list)
    print(index_table.shape)

    cdef np.ndarray[long, ndim=1, mode='c'] cpp_index_table = np.ascontiguousarray(index_table, dtype=ctypes.c_int64)
    cdef long cpp_n_indices = len(index_table)

    # index_table_somae = np.genfromtxt("pointlist_somae_" + str(query_ID) + ".txt", delimiter=',',invalid_raise=True)
    index_table_somae = np.asarray(index_list_somae)
    print(index_table_somae.shape)

    cdef np.ndarray[long, ndim=1, mode='c'] cpp_index_table_somae = np.ascontiguousarray(index_table_somae, dtype=ctypes.c_int64)
    cdef long cpp_n_indices_somae = len(index_table_somae)

    # get blocksize
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_blocksize = np.ascontiguousarray(dataIO.Blocksize(prefix), dtype=ctypes.c_int64)
    # get volumesize
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_volumesize = np.ascontiguousarray(dataIO.Volumesize(prefix), dtype=ctypes.c_int64)

    CppGetcomponentFromPointlist(prefix.encode('utf-8'), &(cpp_index_table[0]), &(cpp_index_table_somae[0]), cpp_n_indices, cpp_n_indices_somae, cpp_query_ID, &(cpp_blocksize[0]), &(cpp_volumesize[0]))
