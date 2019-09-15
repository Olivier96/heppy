import os, sys
import ROOT
import math


############## FUNCTIONS #################

def draw_and_save(distribution_list, canvas, chain, output_directory ,format='png'):
    canvas.cd()
    for dist in distribution_list:
        chain.Draw(dist)
        canvas.SaveAs(output_directory+dist+'.'+format)
    return 0
    
    
def cut_flow_table(chain, cut_list, output_directory, table_name):
    # Get total amount of events in root file
    N_total = chain.GetEntries()
    # Do not proceed if there are no events
    if N_total == 0:
        print "This file is empty!"
        return 0
    # Prepare the cut flow table file
    file = open(output_directory+table_name,"wt")
    file.write("Cut Flow table\n")
    file.write("cuts \t; Yield \t; Efficiency \t; Efficiency uncertainty \t; Compare Nicolo \t; Uncertainty \n")
    # Prepare root utility necessary for cut_flow table
    var = "jet1_e"
    for cut in cut_list:
        n = ch.Draw(var,cut)
        eff = float(n)/N_total
        eff_sig = uncertainty_efficiency(n,N_total)
        file.write(cut+"\t;"+str(n)+"\t;"+str(eff)+"\t;"+str(eff_sig)+"\t;"+str(eff*0.649)+"\t;"+str(eff_sig*0.649)+"\n")
    file.close()
    return 1
    
# https://indico.cern.ch/event/66256/contributions/2071577/attachments/1017176/1447814/EfficiencyErrors.pdf
# Bayesian slide 13
def uncertainty_efficiency(k,N):
    k = float(k)
    N = float(N)
    variance = (((k+1)*(k+2))/((N+2)*(N+3))) - ((k+1)/(N+2))**2
    sigma = variance**(0.5)
    return sigma
    
    

        
############## SCRIPT #################



# Modify the following to change the data to select
sample_dir = 'mtop_1718/'

# Do not modify these variables:
OUT_dir = '~/testFCC/Nicolo/heppy/ttbar_analysis/ANALYSIS/OUT/'
PLOTS_dir = 'PLOTS/'
input_files = 'tt_semilepton_ILD_Chunk0/heppy.analyzers.tree.TreeTTSemilep.TreeTTSemilep_1/tree.root'

# Full paths:
path_to_input_file = OUT_dir+sample_dir+input_files
path_to_output_dir = PLOTS_dir+sample_dir
path_to_output_file = path_to_output_dir+'histograms.root'

# Create directory of output_dir if it doesn't exist
if not os.path.isdir(path_to_output_dir):
    os.makedirs(path_to_output_dir)


# Modify the following to change the data to select

# output file
outfile = ROOT.TFile(path_to_output_file,"RECREATE")
outfile.cd() # necessary to save file

# Create Root TH1D object
histojetdeltaphi = ROOT.TH1D("histojetdeltaphi","histojetdeltaphi",100,-3.1415,3.1415)

#creer chain object
ch = ROOT.TChain("events","events") # de naam van de tree is belangrijk! Dat is hoe root die in the file vindt!

# voeg de files toe
ch.Add(path_to_input_file)

# print wat er in die tree zit
#ch.Print()

# Create a Canvas to draw plots and histograms on
c1 =ROOT.TCanvas("c1","c1")

# Select the canvas
c1.cd()

# direct iets plotten:
#ch.Draw("jet1_e")
# Save the canvas to pdf/png:
#c1.SaveAs(path_to_output_dir+"jet1_e"+".png")

# Or use the convenient function to draw and save a bunch of parameters 
distributions = ["jet1_e", "jet1_logbtag" , "jet1_log10btag", "jet2_e", "four_jets_mass", "min_jets_mass", "second_min_jets_mass", "max_jets_mass", "min_jets_angle", "second_min_jets_angle", "min_jets_lepton_angle", "lep_pt_wrt_closest_jet", "total_rec_mass", "missing_rec_e", "lep1_e", "chi2_algorithm", "chi2_top_constrainer"]

#draw_and_save(distributions, c1, ch, path_to_output_dir)

#Saving a file to a .root file: IN PROGRESS! TO DO
outfile.cd()
print "--"*20
print "Saving all distributions into a .root file:"
for id,dist in enumerate(distributions):
    print "Saving the distribution: "+str(dist)
    ch.Write(dist)
    #c1.SetTitle(dist)
    #c1.Write()
print "--"*20

# CUT FLOW table

cuts = ["", "four_jets_mass > 150", "four_jets_mass < 270", "min_jets_mass > 10", "second_min_jets_mass > 20", "lep1_e < 100", "missing_rec_e > 20", "chi2_top_constrainer <= 40 ", "success == 1"]
table_name = "cut_flow.txt"

#cut_flow_table(ch, cuts, path_to_output_dir, table_name)


# of nog interessanter: code schrijven die ingewikkelder dingen doet, per event
nevents=ch.GetEntries()
if nevents==0 :
    print "bummer, the tree is empty. Probably the wrong tree name or wrong file name?"

print "this tree has ",nevents," events"

ii = 0
for iev in ch: # dit is de event loop
    if ii % 100 ==0 :
        #print ii, "/", nevents
        ii+=1

    # nu kan je over alle dingen itereren:
    if iev.jet1_e > 50 :
        #break
        # een extra variabele, de hoek tussen de jets?
        newvariable = iev.jet1_phi - iev.jet2_phi
        # en die kan je bijvoorbeeld ook in een histogram stoppen
        histojetdeltaphi.Fill(newvariable)



# buiten de event loop kan je plots maken
#canvas = ROOT.TCanvas()
#canvas.cd()
#histojetdeltaphi.Draw()

# Need to close the file after saving the contents of the distributions into it
outfile.Write()
outfile.Close() # or save/close ..
