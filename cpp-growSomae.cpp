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

  // create an output file for the points
  char output_filename[4096];
  // sprintf(output_filename, "%s/segment_pontlist/%s/%s-segment_pointlist.pts", output_directory, prefix, prefix);
  sprintf(output_filename, "%s-segment_pointlist.pts", prefix);

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

void WriteSurfacePoints(const char *prefix, std::unordered_set<long> &points, long &query_ID, long input_blocksize[3], long volumesize[3])
{

  // create an output file for the points
  char output_filename[4096];
  // sprintf(output_filename, "%s/segment_pontlist/%s/%s-segment_pointlist.pts", output_directory, prefix, prefix);
  sprintf(output_filename, "%s-surface_pointlist.pts", prefix);

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


  std::cout << "Total somae points: " << n_indices_somae << std::endl;

  long somae_points_correct = 0;

  for (long i=0; i<n_indices_somae; i++){

    if (segment.find(inp_indices_somae[i]) == segment.end()) continue;

    voxels.push(inp_indices_somae[i]);
    somae_points_correct++;
  }

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

  WriteSurfacePoints(prefix, surface_voxels, query_ID, inp_blocksize, volume_size);




}
