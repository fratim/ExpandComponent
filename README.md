This (experimental) repository includes code to grow a connected-component from a single or multiple source voxels. The input volume can be
saved in an abritrary number of blocks.
For each label (ID) present in the input segmentation volume, only the connected components which include a source voxel are contained.
All other components are discarded. The final segmentation volume is then again written in blocks.
This code was used to find all connected components which are connected to the soma of a neuron. Soma voxels are used as source voxels
and are then grown, only considering 6-conected neighbors. The final segmentation hence does not include any cut off branches.
