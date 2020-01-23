import os
import numpy as np
import sys
import dataIO

template ='''#!/bin/bash
#
# add all other SBATCH directives here
#
#SBATCH -p {PARTITION}                                       # use the COX partition
#SBATCH -n 1                                                 # Number of cores
#SBATCH -N 1                                                 # Ensure that all cores are on one matching
#SBATCH --mem={MEMORY}                                       # CPU memory in MBs
#SBATCH -t 0-{HOURS}:00                                      # time in dd-hh:mm to run the code for
#SBATCH --mail-type=NONE                                     # send all email types (start, end, error, etc.)
#SBATCH --mail-user=tfranzmeyer@g.harvard.edu                # email address to send to
#SBATCH -o {OUTPUT_PATH}/{JOBNAME}.out                       # where to write the log files
#SBATCH -e {ERROR_PATH}/{JOBNAME}.err                        # where to write the error files
#SBATCH -J fillholes_{JOBNAME}                               # jobname given to job

module load Anaconda3/5.0.1-fasrc02
module load cuda/9.0-fasrc02 cudnn/7.1_cuda9.0-fasrc01

source activate fillholes

export PYTHONPATH=$PYTHONPATH:/n/pfister_lab2/Lab/tfranzmeyer/ExpandComponent/

cd {RUNCODEDIRECTORY}

python {COMMAND}

echo "DONE"

'''


'''JWR IDS: [100, 101, 103, 10, 111, 113, 114, 121, 122, 124, 126, 127, 128, 130, 131, 132, 134, 13, 17, 19, 21,
 22, 24, 2, 32, 36, 37, 39, 46, 47, 48, 53, 54, 63, 64, 67, 68, 69, 70, 71, 72, 74, 75, 76, 7, 81, 82, 84, 85, 86, 91, 96, 98, 99, 136, 78, 6, 33, 135,
 65, 105, 94, 16, 12, 9, 20, 23, 29, 30, 31, 35, 90, 41, 55, 59, 83, 34, 27, 56, 92, 97, 104, 43, 44, 42, 45, 87, 108, 93, 88, 26]'''


def makeFolder(folder_path):
    if os.path.exists(folder_path):
        raise ValueError("Folderpath " + folder_path + " already exists!")
    else:
        os.mkdir(folder_path)

def writeFile(filename, data):
    if os.path.exists(filename):
        raise ValueError("File " + filename + " already exists!")
    else:
        with open(filename, 'w') as fd:
            fd.write(data)

if(len(sys.argv))!=5:
    raise ValueError(" Scripts needs 4 cluster partitions as input, put 0 if not less desired")
else:
    n_part = 0
    partitions = ["0","0","0","0"]

    if sys.argv[1]!="0":
        partitions[0] = sys.argv[1]
        n_part +=1
    if sys.argv[2]!="0":
        partitions[1] = sys.argv[2]
        n_part +=1
    if sys.argv[3]!="0":
        partitions[2] = sys.argv[3]
        n_part +=1
    if sys.argv[4]!="0":
        partitions[3] = sys.argv[4]
        n_part +=1

files_written = 0
code_run_path = "/n/pfister_lab2/Lab/tfranzmeyer/ExpandComponent/"
run_hours = "4"
slurm_path = "/n/pfister_lab2/Lab/tfranzmeyer/ExpandComponent/slurms/"

prefix = "Zebrafinch"
ID_MAX = 410

error_path = "/n/pfister_lab2/Lab/tfranzmeyer/ExpandComponent/error_files/"
output_path = "/n/pfister_lab2/Lab/tfranzmeyer/ExpandComponent/output_files/"
template = template.replace('{RUNCODEDIRECTORY}', code_run_path)
template = template.replace('{HOURS}', run_hours)
memory = str(40000)

SLURM_OUTPUT_FOLDER = slurm_path

step01folderpath = SLURM_OUTPUT_FOLDER+"step01/"
step02folderpath = SLURM_OUTPUT_FOLDER+"step02/"

makeFolder(step01folderpath)
makeFolder(step02folderpath)

# write slurm for step two
for ID in range(1,ID_MAX):
    command = "execute_step1.py" + " " + str(ID)
    jobname = "S1"+"_" +"ID_"+str(ID).zfill(6)

    t = template
    t = t.replace('{JOBNAME}', jobname)
    t = t.replace('{COMMAND}', command)
    t = t.replace('{ERROR_PATH}', error_path)
    t = t.replace('{OUTPUT_PATH}', output_path)
    t = t.replace('{MEMORY}', memory)
    t = t.replace('{PARTITION}', partitions[np.random.randint(0,n_part)])

    filename = step01folderpath + jobname + ".slurm"
    writeFile(filename, t)
    files_written += 1


start_blocks = dataIO.StartBlocks(prefix)
n_blocks = dataIO.NBlocks(prefix)

# reassemble blocks
for bz in range(start_blocks[0], start_blocks[0]+n_blocks[0]):
    for by in range(start_blocks[1], start_blocks[1]+n_blocks[1]):
        for bx in range(start_blocks[2], start_blocks[2]+n_blocks[2]):

            command = "execute_step2.py" + " " + str(bz) + " " + str(by) + " " + str(bx)
            jobname = "S2"+"_"+"z"+str(bz).zfill(2)+"y"+str(by).zfill(2)+"x"+str(bx).zfill(2)

            t = template
            t = t.replace('{JOBNAME}', jobname)
            t = t.replace('{COMMAND}', command)
            t = t.replace('{ERROR_PATH}', error_path)
            t = t.replace('{OUTPUT_PATH}', output_path)
            t = t.replace('{MEMORY}', memory)
            t = t.replace('{PARTITION}', partitions[np.random.randint(0,n_part)])

            filename = step02folderpath + jobname + ".slurm"
            writeFile(filename, t)
            files_written += 1











print ("Files written: " + str(files_written))
