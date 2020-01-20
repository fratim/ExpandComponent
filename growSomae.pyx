import os
import time


cimport cython
cimport numpy as np
import ctypes
import numpy as np

import dataIO

# cdef extern from 'cpp-wiring.h':
#     void CPPcreateDataBlock(const char *prefix, const char *lookup_table_directory, long *inp_labels, long *inp_somae, float input_resolution[3],
#             long inp_blocksize[3], long volume_size[3], long block_ind_inp[3], long block_ind_start_inp[3], long block_ind_end_inp[3],
#             const char* synapses_dir, const char* somae_dir, const char* output_dir);
#     void CppSkeletonRefinement(const char *prefix, float input_resolution[3], long inp_blocksize[3], long volume_size[3], long block_ind_begin[3],
#             long block_ind_end[3], const char* output_dir);
#     void ComputeAnchorPoints(const char *prefix, const char* output_dir, long inp_blocksize_inp[3], long blockind_inp[3], long block_ind_start_inp[3], long block_ind_end_inp[3],
#             long volumesize_in_inp[3], long *z_min_wall, long *z_max_wall, long *y_min_wall, long *y_max_wall, long *x_min_wall, long *x_max_wall);
# save walls

def growSomae(prefix, output_folder, query_ID, block_z_start, block_y_start, block_x_start, block_z_end, block_y_end, block_x_end):

    index_list = []

    for bz in (block_z_start, block_z_end+1):
        for by in (block_y_start, block_y_end+1):
            for bx in (block_x_start, block_x_end+1):

                labels_in = fileName = dataIO.InputlabelsDirectory(prefix)+"/"+prefix+"/Zebrafinch-labels_discarded_filled_padded-"+str(block_z).zfill(4)+"z-"+str(block_y).zfill(4)+"y-"+str(block_x).zfill(4)+"x"+".h5"
                data = dataIO.ReadH5File(fileName)
                point_list = getPointList(labels_in, blocksize, bz, by, bx, query_ID)
                index_list = [index_list, point_list]

                print(len(index_list))
                del point_list


    # get blocksize
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_blocksize = np.ascontiguousarray(dataIO.Blocksize(prefix), dtype=ctypes.c_int64)
    # get volumesize
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_volumesize = np.ascontiguousarray(dataIO.Volumesize(prefix), dtype=ctypes.c_int64)
    # get Resolution from meta file
    cdef np.ndarray[float, ndim=1, mode='c'] cpp_resolution = np.ascontiguousarray(dataIO.Resolution(prefix)).astype(np.float32)
    # get block indices (start)
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_block_ind_begin = np.ascontiguousarray(np.array([block_z_start, block_y_start, block_x_start]), dtype=ctypes.c_int64)
    # get block indices (end)
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_block_ind_end = np.ascontiguousarray(np.array([block_z_end, block_y_end, block_x_end]), dtype=ctypes.c_int64)

    CppSkeletonRefinement(prefix.encode('utf-8'), &(cpp_resolution[0]), &(cpp_blocksize[0]), &(cpp_volumesize[0]), &(cpp_block_ind_begin[0]), &(cpp_block_ind_end[0]), output_folder.encode('utf-8'))
