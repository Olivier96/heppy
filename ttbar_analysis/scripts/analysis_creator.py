import os,sys
from optparse import OptionParser


# This script is intended to create a single ee_tt_analysis_cfg.py file with easily accessible parameters via the parser.

parser = OptionParser()
parser.add_option("--output-directory",dest="output_directory", default = "../CONFIGS/", help = "Name of the output directory, default = ../CONFIGS/", type = str)
parser.add_option("--output-subdir",dest="output_subdir", default= "", help = "Name of the subdirectory where the output is stored")
parser.add_option("-o","--filename", dest = "output_file", default = "", help = "Name of the analyzer including extension", type= str)
parser.add_option("-E", "--com-energy", dest = "E", default = 350., help = "Center of mass energy of the collision", type = float)
parser.add_option("-D","--detector", dest = "detector", default = "ILD", help = "Name of the detector", type = str)
parser.add_option("-s","--sampler", dest = "sampler", default = "", help = "Name of the python sampler", type = str)
parser.add_option("--sample-dir", dest = "sample_dir", default = "", help = "Name of the subdirectory of the sampler, if none the default is ./", type = str)
parser.add_option("-N", "--n-nodes", dest = "n_nodes", default = 1, help = "Amount of nodes for the t2 cluster", type = int)
parser.add_option("-n", "--n-cores", dest = "n_cores", default = 1, help = "Amount of cores per nodes for the t2 cluster", type = int)
parser.add_option("--n-jets", dest = "n_jets", default = 4, help = "Amount of jets for the analysis to look for, default = 4", type = int)


# ASSIGN parsed arguments to DICTIONNARY options:
(options, args) = parser.parse_args()

if options.output_file == "" or options.sampler == "":
    print "please provide a name for the output file using -o and a sampler using -s, see example"
    print "python analysis_creator.py -o ee_tt_analysis_cfg_test.py -E 350 -D ILD -s <sampler.py> -N 2 -n 4"
    exit()

if not os.path.isdir(options.output_directory+options.output_subdir):
    os.makedirs(options.output_directory+options.output_subdir)


# Prepare files to read and write
file_template = open('../CONFIGS/ee_tt_analysis_template.py',"rt")
file_output = open(options.output_directory+options.output_subdir+options.output_file,"wt")


# Copy first section
for iline in range(17):
    file_output.write(file_template.readline())

file_template.readline()
file_output.write("Collider.SQRTS = {sqrts}\n".format(sqrts = options.E))
file_template.readline()
file_output.write("Collider.DETECTOR = '{detector}'\n".format(detector = options.detector))

for iline in range(6):
    file_output.write(file_template.readline())

file_template.readline()
# Make sure the sampler is in the right format for an import, removing .py if necessary
if options.sampler.endswith(".py"):
    options.sampler=options.sampler[:-3]
# Add a dot if there is a sample_dir subfolder and remove slashes if necessary
if options.sample_dir != "":
    options.sample_dir = options.sample_dir.replace("/",".")
    if not options.sample_dir.endswith("."):
        options.sample_dir = options.sample_dir+"."
while options.sample_dir.startswith("."):
    options.sample_dir = options.sample_dir[1:]

file_output.write("from heppy.ttbar_analysis.ANALYSIS.PYTHIA.python_samplers.{sample_dir}{sampler} import selectedComponents \n".format(sample_dir = options.sample_dir, sampler = options.sampler))

file_template.readline()
file_template.readline()
file_output.write("\n\n")
file_template.readline()
file_output.write("n_cores = {n_nodes}*{n_cores}\n".format(n_nodes=options.n_nodes, n_cores = options.n_cores))
file_template.readline()
file_output.write("number_jets = {n_jets}\n".format(n_jets=options.n_jets))


for iline in range(68):
    file_output.write(file_template.readline())



file_output.close()
file_template.close()

