#ifndef __CPP_WIRING__
#define __CPP_WIRING__
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <unordered_map>
#include <unordered_set>
#include <iostream>
#include <stdio.h>


// universal variables and functions
#define OR_Z 0
#define OR_Y 1
#define OR_X 2


// function calls across cpp files
void CppGetcomponentFromPointlist(const char *prefix, long *inp_indices, long *inp_indices_somae, long n_indices, long n_indices_somae, long query_ID, long inp_blocksize[3], long volume_size[3]);



//////////////////////////////////////
//// COORDINATE UTILITY FUNCTIONS ////
//////////////////////////////////////

inline void IndexToIndices(long iv, long &ix, long &iy, long &iz, long sheet_size, long row_size)
{

    iz = iv / sheet_size;
    iy = (iv - iz * sheet_size) / row_size;
    ix = iv % row_size;
}

inline long IndicesToIndex(long ix, long iy, long iz, long sheet_size, long row_size)
{
    return iz * sheet_size + iy * row_size + ix;
}

inline long IndexLocalToGlobal(long iv, long block_ind[3], long block_size[3], long volume_size[3])
{

  long row_size = block_size[OR_X];
  long sheet_size = block_size[OR_X]*block_size[OR_Y];

  long iz_global = iv / sheet_size                                    + block_ind[OR_Z]*block_size[OR_Z];
  long iy_global = (iv - (iv / sheet_size) * sheet_size) / row_size   + block_ind[OR_Y]*block_size[OR_Y];
  long ix_global = iv % row_size                                      + block_ind[OR_X]*block_size[OR_X];

  return iz_global * volume_size[OR_X]*volume_size[OR_Y] + iy_global *volume_size[OR_X]  + ix_global;
}

inline long PadIndex(long index_unpadded, long unpadded_sheet_size, long unpadded_row_size, long padded_sheet_size, long padded_row_size)
{

    long iz = index_unpadded / unpadded_sheet_size;
    long iy = (index_unpadded - iz * unpadded_sheet_size) / unpadded_row_size;
    long ix = index_unpadded % unpadded_row_size;

    //  pad the location by one
    long iz_padded = iz + 1;
    long iy_padded = iy + 1;
    long ix_padded = ix + 1;

    // find the new voxel index
    long index_padded = iz_padded * padded_sheet_size + iy_padded * padded_row_size + ix_padded;

    return index_padded;
}

inline long UnpadIndex(long index_padded, long unpadded_sheet_size, long unpadded_row_size, long padded_sheet_size, long padded_row_size)
{

    long iz_unpadded = index_padded / padded_sheet_size                                                               - 1;
    long iy_unpadded = (index_padded - (index_padded / padded_sheet_size) * padded_sheet_size) / padded_row_size      - 1;
    long ix_unpadded = index_padded % padded_row_size                                                                 - 1;

    return iz_unpadded * unpadded_sheet_size + iy_unpadded * unpadded_row_size + ix_unpadded;
}



#endif
