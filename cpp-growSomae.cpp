/* c++ file to extract wiring diagram */
#include <limits>
#include "cpp-growSomae.h"
#include <iostream>
#include <stdexcept>
#include <fstream>
#include <vector>
#include <time.h>
#include <stdio.h>
#include <string>
#include <unistd.h>
#include <algorithm>
#include <fstream>
#include <stack>

void WriteHeaderSegID(FILE *fp, long &num, long &segID, long input_blocksize[3], long volumesize[3])
{
  int check = 0;
  int size_l = sizeof(long);

  check += fwrite(&(volumesize[OR_Z]), size_l, 1, fp);
  check += fwrite(&(volumesize[OR_Y]), size_l, 1, fp);
  check += fwrite(&(volumesize[OR_X]), size_l, 1, fp);
  check += fwrite(&(input_blocksize[OR_Z]), size_l, 1, fp);
  check += fwrite(&(input_blocksize[OR_Y]), size_l, 1, fp);
  check += fwrite(&(input_blocksize[OR_X]), size_l, 1, fp);
  check += fwrite(&segID, size_l, 1, fp);
  check += fwrite(&num, size_l, 1, fp);

  if (check != 8) { fprintf(stderr, "Failed to write file in writeheader\n"); exit(-1); }
}

void WritePointsOfSegment(const char *prefix, std::unordered_set<long> &points, long &query_ID, long input_blocksize[3], long volumesize[3])
{

  std::unordered_map<long,std::unordered_map<long,std::unordered_map<long, std::unordered_set<long>>>> global_points_block = std::unordered_map<long,std::unordered_map<long,std::unordered_map<long, std::unordered_set<long>>>>();
  std::unordered_map<long,std::unordered_map<long,std::unordered_map<long, std::unordered_set<long>>>> local_points_block = std::unordered_map<long,std::unordered_map<long,std::unordered_map<long, std::unordered_set<long>>>>();

  long global_sheet_size = volumesize[OR_Y]*volumesize[OR_X];
  long global_row_size = volumesize[OR_X];

  {
    // create an output file for the points
    char output_filename[4096];
    // sprintf(output_filename, "%s/segment_pontlist/%s/%s-segment_pointlist.pts", output_directory, prefix, prefix);
    sprintf(output_filename, "segments_out/%s-segment-%06ld.pts", prefix, query_ID);

    FILE *wfp = fopen(output_filename, "wb");
    if (!wfp) { fprintf(stderr, "Failed to open %s\n", output_filename); exit(-1); }

    long n_points = points.size();

    // write the characteristics header
    WriteHeaderSegID(wfp, n_points, query_ID, input_blocksize, volumesize);
    long checksum = 0;

    for (std::unordered_set<long>::iterator itr = points.begin(); itr!=points.end(); ++itr){

      long up_iv_global = *itr;
      if (fwrite(&up_iv_global, sizeof(long), 1, wfp) != 1) { fprintf(stderr, "Failed to write to %s\n", output_filename); exit(-1); }
      checksum += up_iv_global;

      // write points to maps
      long global_iz = 0;
      long global_iy = 0;
      long global_ix = 0;

      IndexToIndices(up_iv_global, global_ix, global_iy, global_iz, global_sheet_size, global_row_size);

      long zblock = floor((double)global_iz / (double)input_blocksize[OR_Z]);
      long yblock = floor((double)global_iy / (double)input_blocksize[OR_Y]);
      long xblock = floor((double)global_ix / (double)input_blocksize[OR_X]);

      long local_iz = global_iz - (input_blocksize[OR_Z]*zblock);
      long local_iy = global_iy - (input_blocksize[OR_Y]*yblock);
      long local_ix = global_ix - (input_blocksize[OR_X]*xblock);

      long local_iv = local_iz * input_blocksize[OR_Y] * input_blocksize[OR_X] + local_iy * input_blocksize[OR_X] + local_ix;

      global_points_block[zblock][yblock][xblock].insert(up_iv_global);
      local_points_block[zblock][yblock][xblock].insert(local_iv);

    }

    if (fwrite(&checksum, sizeof(long), 1, wfp) != 1) { fprintf(stderr, "Failed to write to %s\n", output_filename); exit(-1); }
    fclose(wfp);
  }

  long n_blocks_z = floor((double)volumesize[OR_Z] / (double)input_blocksize[OR_Z]);
  long n_blocks_y = floor((double)volumesize[OR_Y] / (double)input_blocksize[OR_Y]);
  long n_blocks_x = floor((double)volumesize[OR_X] / (double)input_blocksize[OR_X]);

  for (long bz=0; bz<n_blocks_z; bz++){
    for (long by=0; by<n_blocks_y; by++){
      for (long bx=0; bx<n_blocks_x; bx++){

        char output_filename[4096];
        // sprintf(output_filename, "%s/segment_pontlist/%s/%s-segment_pointlist.pts", output_directory, prefix, prefix);
        sprintf(output_filename, "segments_out/%s-segment-%06ld-%04ldz-%04ldy-%04ldx.pts", prefix, query_ID, bz, by, bx);

        FILE *wfp = fopen(output_filename, "wb");
        if (!wfp) { fprintf(stderr, "Failed to open %s\n", output_filename); exit(-1); }

        long n_points = global_points_block[bz][by][bx].size();
        long n_points_compare = local_points_block[bz][by][bx].size();

        if (n_points!=n_points_compare) {
          fprintf(stderr, "Failed unkown.\n");
        }

        // write the characteristics header
        WriteHeaderSegID(wfp, n_points, query_ID, input_blocksize, volumesize);
        long checksum = 0;

        std::unordered_set<long>::iterator it;

        long n_written_global = 0;
        long n_written_local = 0;

        for (it = global_points_block[bz][by][bx].begin(); it != global_points_block[bz][by][bx].end(); ++it){

          long up_iv_global = *it;
          if (fwrite(&up_iv_global, sizeof(long), 1, wfp) != 1) { fprintf(stderr, "Failed to write to %s\n", output_filename); exit(-1); }
          checksum += up_iv_global;
          n_written_global++;

        }

        for (it = local_points_block[bz][by][bx].begin(); it != local_points_block[bz][by][bx].end(); ++it){

          long up_iv_local = *it;
          if (fwrite(&up_iv_local, sizeof(long), 1, wfp) != 1) { fprintf(stderr, "Failed to write to %s\n", output_filename); exit(-1); }
          checksum += up_iv_local;
          n_written_local++;

        }

        std::cout << "written global: " << n_written_global << std::endl;
        std::cout << "written local: " << n_written_local << std::endl;
        std::cout << "n_points: " << n_points << std::endl;


        if (fwrite(&checksum, sizeof(long), 1, wfp) != 1) { fprintf(stderr, "Failed to write to %s\n", output_filename); exit(-1); }
        fclose(wfp);

      }
    }
  }
}

void WriteSurfacePoints(const char *prefix, const char *identifier, std::unordered_set<long> &points, long &query_ID, long input_blocksize[3], long volumesize[3])
{

  // create an output file for the points
  char output_filename[4096];
  // sprintf(output_filename, "%s/segment_pontlist/%s/%s-segment_pointlist.pts", output_directory, prefix, prefix);
  sprintf(output_filename, "%s_out/%s-surface-%06ld.pts", identifier, prefix, query_ID);

  FILE *wfp = fopen(output_filename, "wb");
  if (!wfp) { fprintf(stderr, "Failed to open %s\n", output_filename); exit(-1); }

  long n_points = points.size();

  // write the characteristics header
  WriteHeaderSegID(wfp, n_points, query_ID, input_blocksize, volumesize);
  long checksum = 0;

  for (std::unordered_set<long>::iterator itr = points.begin(); itr!=points.end(); ++itr){

    long up_iv_global = *itr;
    if (fwrite(&up_iv_global, sizeof(long), 1, wfp) != 1) { fprintf(stderr, "Failed to write to %s\n", output_filename); exit(-1); }
    checksum += up_iv_global;

  }

  if (fwrite(&checksum, sizeof(long), 1, wfp) != 1) { fprintf(stderr, "Failed to write to %s\n", output_filename); exit(-1); }
  fclose(wfp);
}

// function calls across cpp files
void CppGetcomponentFromPointlist(const char *prefix, long *inp_indices, long *inp_indices_somae, long n_indices, long n_indices_somae, long query_ID, long inp_blocksize[3], long volume_size[3]){

  // create new segment set
  std::unordered_set<long> segment = std::unordered_set<long>();

  std::cout << "Inserting elements: " << n_indices << std::endl;

  for (long i=0; i<n_indices; i++){
    segment.insert(inp_indices[i]);
  }


  std::stack<long> voxels = std::stack<long>();
  // create a set of vertices that are connected
  std::unordered_set<long> visited = std::unordered_set<long>();
  std::unordered_set<long> surface_voxels = std::unordered_set<long>();
  std::unordered_set<long> somae_surface_voxels = std::unordered_set<long>();
  std::unordered_set<long> somae_input_voxels = std::unordered_set<long>();


  std::cout << "Total somae points: " << n_indices_somae << std::endl;

  long somae_points_correct = 0;

  // add all correct somae voxels to the voxels list
  for (long i=0; i<n_indices_somae; i++){

    // somae input voxels is a set that holds all input somae indices
    somae_input_voxels.insert(inp_indices_somae[i]);

    // somae indices that are also listed as a segment are now added to the initial voxel list
    if (segment.find(inp_indices_somae[i]) == segment.end()) continue;

    voxels.push(inp_indices_somae[i]);
    somae_points_correct++;

  }

  // add all somae surface voxels to the according sets
  long n_surfacePoints_somae = 0;

  for (long i=0; i<n_indices_somae; i++){


    long sheet_size = volume_size[OR_Y]*volume_size[OR_X];
    long row_size = volume_size[OR_X];

    long ix, iy, iz;
    IndexToIndices(inp_indices_somae[i], ix, iy, iz, sheet_size, row_size);

    bool isSurface = 0;

    for (long iw = iz - 1; iw <= iz + 1; ++iw) {
      if (iw < 0 or iw >= volume_size[OR_Z]) continue;
      for (long iv = iy - 1; iv <= iy + 1; ++iv) {
        if (iv < 0 or iv >= volume_size[OR_Y]) continue;
        for (long iu = ix - 1; iu <= ix + 1; ++iu) {
          if (iu < 0 or iu >= volume_size[OR_X]) continue;

          long neighbor = IndicesToIndex(iu, iv, iw, sheet_size, row_size);

          // if equal, continue
          if (neighbor == inp_indices_somae[i]) continue;

          // skip background voxels
          if (somae_input_voxels.find(neighbor) == somae_input_voxels.end()) {
            // check is is 6-connected neighbor, if so, this is a surface voxel

            if ((iw!=iz && iv==iy && iu==ix)||(iw==iz && iv!=iy && iu==ix)||(iw==iz && iv==iy && iu!=ix)){
              isSurface = 1;
              n_surfacePoints_somae++;
            }

            continue;
          }

        }
      }
    }

    if (isSurface) somae_surface_voxels.insert(inp_indices_somae[i]);

  }

  const char *id = "somae_surfaces";
  WriteSurfacePoints(prefix, id, somae_surface_voxels, query_ID, inp_blocksize, volume_size);
  std::cout << "Found Somae surface points: " << n_surfacePoints_somae << std::endl;
  std::cout << "Inserted correct somae points: " << somae_points_correct << std::endl;

  long sheet_size = volume_size[OR_Y]*volume_size[OR_X];
  long row_size = volume_size[OR_X];

  long n_surfacePoints = 0;

  // perform depth first search
  while (voxels.size()) {
    // remove the pixel from the queue
    long voxel = voxels.top();
    voxels.pop();

    // if already visited skip
    if (visited.find(voxel) != visited.end()) continue;

    // label this voxel as visited
    visited.insert(voxel);

    // add the twenty six neighbors to the queue
    long ix, iy, iz;
    IndexToIndices(voxel, ix, iy, iz, sheet_size, row_size);

    bool isSurface = 0;

    for (long iw = iz - 1; iw <= iz + 1; ++iw) {
      if (iw < 0 or iw >= volume_size[OR_Z]) continue;
      for (long iv = iy - 1; iv <= iy + 1; ++iv) {
        if (iv < 0 or iv >= volume_size[OR_Y]) continue;
        for (long iu = ix - 1; iu <= ix + 1; ++iu) {
          if (iu < 0 or iu >= volume_size[OR_X]) continue;

          long neighbor = IndicesToIndex(iu, iv, iw, sheet_size, row_size);

          // if equal, continue
          if (neighbor == voxel) continue;

          // skip background voxels
          if (segment.find(neighbor) == segment.end()) {
            // check is is 6-connected neighbor, if so, this is a surface voxel

            if ((iw!=iz && iv==iy && iu==ix)||(iw==iz && iv!=iy && iu==ix)||(iw==iz && iv==iy && iu!=ix)){
              isSurface = 1;
              n_surfacePoints++;
            }

            continue;
          }
          // add this neighbor
          voxels.push(neighbor);

        }
      }
    }

    if (isSurface) surface_voxels.insert(voxel);

  }

  std::cout << "Writing segment points to File: " << visited.size() << std::endl;

  // write to file
  WritePointsOfSegment(prefix, visited, query_ID, inp_blocksize, volume_size);

  std::cout << "Writing surface points to File: " << surface_voxels.size() << std::endl;

  const char *id2 = "surfaces";
  WriteSurfacePoints(prefix, id2, surface_voxels, query_ID, inp_blocksize, volume_size);




}
