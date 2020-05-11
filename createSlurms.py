import os
import numpy as np
import sys
import dataIO

template = #TODO

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
