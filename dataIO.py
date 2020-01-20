import os
import h5py
import struct


import numpy as np
from numba import njit
#from PIL import Image



import meta_data


def Resolution(prefix):
    # return the resolution for this prefix
    return meta_data.MetaData(prefix).Resolution()

def Blocksize(prefix):
    # return the blocksize for this prefix
    return meta_data.MetaData(prefix).Blocksize()

def StartBlocks(prefix):
    # return the blocksize for this prefix
    return meta_data.MetaData(prefix).StartBlocks()

def NBlocks(prefix):
    # return the blocksize for this prefix
    return meta_data.MetaData(prefix).NBlocks()

def Volumesize(prefix):
    # return the volumesize for this prefix
    return meta_data.MetaData(prefix).Volumesize()

def InputlabelsDirectory(prefix):
    # return the filepath to the segmented blocks
    return meta_data.MetaData(prefix).InputlabelsDirectory()

def SynapsesDirectory(prefix):
    # return the filepath to the synapses (of each Neuron)
    return meta_data.MetaData(prefix).SynapsesDirectory()

def SomaeDirectory(prefix):
    # return the filepath to the synapses (of each Neuron)
    return meta_data.MetaData(prefix).SomaeDirectory()

def OutputDirectory(prefix):
    # return the filepath to the synapses (of each Neuron)
    return meta_data.MetaData(prefix).OutputDirectory()

def ReadImage(filename):
    # return the image corresponding to this file
    im = np.array(Image.open(filename))
    return im

def ReadH5File(filename):
    # return the first h5 dataset from this file
    with h5py.File(filename, 'r') as hf:
        keys = [key for key in hf.keys()]
        data = np.array(hf[keys[0]])
    return data

def WriteH5File(data, filename, dataset):
    with h5py.File(filename, 'w') as hf:
        # should cover all cases of affinities/images
        hf.create_dataset(dataset, data=data, compression='gzip')

def ReadPoints(prefix, label, dataset):
    # get the filename for the segmentation
    point_cloud_filename = '{}/{}/{:06d}.pts'.format(dataset, prefix, label)
    prefix_zres, prefix_yres, prefix_xres = GridSize(prefix)

    with open(point_cloud_filename, 'rb') as fd:
        zres, yres, xres, npoints, = struct.unpack('qqqq', fd.read(32))
        assert (zres == prefix_zres)
        assert (yres == prefix_yres)
        assert (xres == prefix_xres)
        point_cloud = struct.unpack('%sq' % npoints, fd.read(8 * npoints))

    return point_cloud

def ReadAllPoints(prefix, dataset):
    labels = [int(label[:-4]) for label in sorted(os.listdir('{}/{}'.format(dataset, prefix)))]

    point_clouds = {}

    # read all individual point clouds
    for label in labels:
        point_clouds[label] = ReadPoints(prefix, label, dataset)

    return point_clouds

def ReadWidths(prefix, label):
    # get the filename with all of the widths
    width_filename = 'widths/{}/{:06d}.pts'.format(prefix, label)

    prefix_zres, prefix_yres, prefix_xres = GridSize(prefix)

    widths = {}

    with open(width_filename, 'rb') as fd:
        zres, yres, xres, nelements, = struct.unpack('qqqq', fd.read(32))
        assert (zres == prefix_zres)
        assert (yres == prefix_yres)
        assert (xres == prefix_xres)

        for _ in range(nelements):
            index, width, = struct.unpack('qf', fd.read(12))
            widths[index] = width

    # return the dictionary of widths for each skeleton point
    return widths

@njit
def getPointList(labels_in, blocksize, volumesize,  bz, by, bx, query_ID, dsp_factor):

    iv_list = []

    for iz in range(labels_in.shape[0]):
        for iy in range(labels_in.shape[1]):
            for ix in range(labels_in.shape[2]):

                if labels_in[iz,iy,ix]!=query_ID: continue

                iz_global = iz*dsp_factor + bz*blocksize[0]
                iy_global = iy*dsp_factor + by*blocksize[1]
                ix_global = ix*dsp_factor + bx*blocksize[2]

                iv_global = iz_global * volumesize[2]*volumesize[1] + iy_global *volumesize[2]  + ix_global

                iv_list.append(iv_global)


    return iv_list
