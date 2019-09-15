import os,sys
from optparse import OptionParser


# This script is intended to create easily a single gen_card where all parameters are easily accesible via the parser.


# Setup the parser to read in the name of the output file
parser = OptionParser()
parser.add_option("--output-directory",dest="output_directory", default = "../ntuples_generator_copies/", help = "Name of the output directory, absolute or relative path", type = str)
parser.add_option("-o","--filename", dest = "output_file", default = "", help = "Name of the generator card including extension", type= str)
parser.add_option("-m","--mass-top", dest="mtop", default = 173.0, help = "mass of the top quark, default value = 173.0 (pdg)", type=float)
parser.add_option("-W", "--width-top", dest = "topwidth", default = 1.41, help = "Width of the top quark, default value = 1.41 (pdg)", type = float)
parser.add_option("-N", "--number-events", dest = "N", default = 10000, help = "Number of events to simulate", type = int)
parser.add_option("-E", "--com-energy", dest = "E", default = 350, help = "Center of mass energy of the collision", type = float)
parser.add_option("-c", "--card", dest = "card", default = 'tt', type = str, help = "Type of card, options are: [tt, dilep, had, ww, zz, hz]")


# ASSIGN parsed arguments to DICTIONNARY options:
(options, args) = parser.parse_args()

options.card = options.card.lower()
cards = ['tt', 'dilep', 'had', 'ww', 'zz', 'hz']

if options.output_file == "" or not options.card in cards:
    print "please provide a name for the output file using -o: example and "
    print "python card_creator.py -o ee_ttbar.txt -m 173 -W 1.41 -N 10000 -E 350 -c tt"
    print "card options -c : ",cards
    exit()

# Prepare files to read and write
file_template = open('../ntuples_generator_copies/ee_ttbar_template.txt',"rt")
file_output = open(options.output_directory+options.output_file,"wt")

# Copy first section
for iline in range(11):
    file_output.write(file_template.readline())
    
# Skip amount of events line and define our own
file_template.readline()
file_output.write("Main:numberOfEvents = {nevents}  ! number of events to generate\n".format(nevents = options.N))

# Copy second section from template
for iline in range(16):
    file_output.write(file_template.readline())
    
file_template.readline()
file_output.write("Beams:eCM = {sqrts}                 ! CM energy of collision\n".format(sqrts= options.E))

file_output.write("\n")
file_output.write("! 5) Scan over parameters: top mass, top decay width, top yukawa coupling\n")
file_output.write("\n")
file_output.write("6:m0 = {mtop}    ! Mass of the top quark\n".format(mtop=options.mtop))
file_output.write("6:mWidth = {topwidth}    ! Width of the top quark\n".format(topwidth= options.topwidth))
file_output.write("\n")
if options.card == 'tt':
    file_output.write("Top:All = on\n")
elif options.card == 'dilep':
    file_output.write("Top:ffbar2ttbar(s:gmZ) = on\n")
    file_output.write("24:onMode = off  ! switch off all W decays\n")
    file_output.write("24:onIfAny = 11, 13, 15  ! switch on W->lep only\n")
    file_output.write("PartonLevel:ISR = on               ! no initial-state radiation\n")
    file_output.write("PartonLevel:FSR = on               ! no final-state radiation\n")
    file_output.write("HadronLevel:Hadronize = on         ! no hadronization\n")
elif options.card == 'had':
    file_output.write("Top:ffbar2ttbar(s:gmZ) = on\n")
    file_output.write("24:onMode = off  ! switch off all W decays\n")
    file_output.write("24:onIfAny = 1, 2, 3, 4, 5  ! switch on W->had only\n")
    file_output.write("PartonLevel:ISR = on               ! no initial-state radiation\n")
    file_output.write("PartonLevel:FSR = on               ! no final-state radiation\n")
    file_output.write("HadronLevel:Hadronize = on         ! no hadronization\n")
elif options.card == 'ww':
    file_output.write("WeakDoubleBoson:ffbar2WW = on\n\n")
    file_output.write("PartonLevel:ISR = on               ! no initial-state radiation\n")
    file_output.write("PartonLevel:FSR = on               ! no final-state radiation\n")
    file_output.write("HadronLevel:Hadronize = on         ! no hadronization\n")
elif options.card == 'zz':
    file_output.write("WeakDoubleBoson:ffbar2gmZgmZ = on\n\n")
    file_output.write("PartonLevel:ISR = on               ! no initial-state radiation\n")
    file_output.write("PartonLevel:FSR = on               ! no final-state radiation\n")
    file_output.write("HadronLevel:Hadronize = on         ! no hadronization\n")
elif options.card == 'hz':
    file_output.write("HiggsSM:ffbar2HZ = on \n\n")
    file_output.write("PartonLevel:ISR = on               ! no initial-state radiation\n")
    file_output.write("PartonLevel:FSR = on               ! no final-state radiation\n")
    file_output.write("HadronLevel:Hadronize = on         ! no hadronization\n")


file_output.close()
file_template.close()













