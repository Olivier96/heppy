import os,sys
import argparse

# Script intended to easily create a python sampler for 1 pythia .root file

parser = argparse.ArgumentParser()
parser.add_argument("--output-directory",dest="output_directory", default = "./", help = "Name of the output directory, default is the ./", type = str)
parser.add_argument("-o","--filename", dest = "output_file", default = "", help = "Name of the sampler including extension", type= str)
parser.add_argument("-n","--ntuple", dest = "ntuple", default = "", help = "Name of the input ntuple to use for the analysis", type = str, nargs='+')
parser.add_argument("-d", "--ntuple-dir", dest = "ntuple_dir", default = "", help = "Name of the subdirectory inside PYTHIA/ntuples/; default is empty, meaning the directory PYTHIA/ntuples", type = str)
parser.add_argument("-a","--analysis-dir", dest = "analysis_dir", default = "tt_semilepton_ILD", help = "Name of the directory inside the analysis directory, not really required to modify in most cases", type = str)
#parser.add_argument("--test", dest = "test", type = int)


# ASSIGN parsed arguments to DICTIONNARY options:
options = parser.parse_args()
#print options.test

if options.output_file == "":
    print "please provide a name for the output file, see example"
    print "python sampler_creator.py -o mtop_sampler.py -n ee_ttbar.root -d <subdir if necessary>"
    exit()

# Create directory of output_dir if it doesn't exist
if not os.path.isdir(options.output_directory):
    os.makedirs(options.output_directory)
    
# Check if directory contains a __init__.py directory and create one if necessary
if not ("__init__.py" in os.listdir(options.output_directory)):
    file = open(options.output_directory+"__init__.py","wt")
    file.write("\n\n")
    file.close()


# Now to the sampler:
file_sampler = open(options.output_directory+options.output_file,"wt")
file_sampler.write("import heppy.framework.config as cfg\n")
file_sampler.write("import os\n")
file_sampler.write("\n")
file_sampler.write("\n")
file_sampler.write("name_outdir = '{analysis_dir}'\n".format(analysis_dir=options.analysis_dir))
file_sampler.write("path_to_ntuples = '/storage_mnt/storage/user/odupon/heppy/ttbar_analysis/ANALYSIS/PYTHIA/ntuples/{ntuple_dir}'\n".format(ntuple_dir=options.ntuple_dir))
for i,ntup in enumerate(options.ntuple):
    file_sampler.write("ntuple{i} = '{ntuple}'\n".format(i=i,ntuple=ntup))
    file_sampler.write("\n")
    file_sampler.write("sample{i} = cfg.Component(\n".format(i=i))
    file_sampler.write("    name_outdir,\n")
    file_sampler.write("    files=path_to_ntuples+ntuple{i} \n".format(i=i))
    file_sampler.write("    ) \n")
    
file_sampler.write("\n\n")
file_sampler.write("selectedComponents = [\n")
for i,ntup in enumerate(options.ntuple):
    file_sampler.write("                        sample{},\n".format(i))
file_sampler.write("                     ]\n")


file_sampler.close()



