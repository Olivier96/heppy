import os, sys
import ROOT as rt
from copy import copy


####### BOOK KEEPING #######################################
# Do not modify these variables:
OUT_dir = '~/testFCC/Nicolo/heppy/ttbar_analysis/ANALYSIS/OUT/'
PLOTS_dir = 'PLOTS/'
#input_files = ['tree_'+str(j)+'.root' for j in range(40)]
#input_files = 'tt_semilepton_ILD_Chunk0/heppy.analyzers.tree.TreeTTSemilep.TreeTTSemilep_1/tree.root'

## Full paths:
#if type(input_files) == str:
#    path_to_input_file = OUT_dir+sample_dir+input_files
#elif type(input_files) == list:
#    path_to_input_file = [OUT_dir+sample_dir+s for s in input_files]
#path_to_output_dir = PLOTS_dir+output_dir
#path_to_output_file = path_to_output_dir+'selection_histograms.root'
#
## Create directory of output_dir if it doesn't exist
#if not os.path.isdir(path_to_output_dir):
#    os.makedirs(path_to_output_dir)

# Create an empty root file, then add into it later using save_histo 
# output file
#root_outfile = rt.TFile(path_to_output_file,"RECREATE")
#root_outfile.cd() # necessary to save file
## Save and Close the root file
#root_outfile.Write()
#root_outfile.Close()

#creer chain object
#ch = rt.TChain("events","events") # de naam van de tree is belangrijk! Dat is hoe root die in the file vindt!


# voeg de files toe
#if type(path_to_input_file) == str:
#    ch.Add(path_to_input_file)
#elif type(path_to_input_file) == list:
#    for rootfile in path_to_input_file:
#        ch.Add(rootfile)
#ch.Add("OUT/had_*/tt_semilepton_ILD_Chunk0/heppy.analyzers.tree.TreeTTSemilep.TreeTTSemilep_1/tree.root")

#print "Entries in TChain: ",ch.GetEntries()

def get_chainlist(sample_directory, root_tree_name, N_tree, N_tree_max,Ttree_name = "events"):
    if not sample_directory.endswith("/"):
        sample_directory = sample_directory+"/"
    input_trees = [ OUT_dir+sample_directory+root_tree_name+str(i)+'.root' for i in range(N_tree_max) ]
    
    #print input_trees
    chain = rt.TChain(Ttree_name,Ttree_name)
    it = 0
    files_added = 0
    while it < N_tree:
        #print it
        N_entries = chain.GetEntries()
        chain.Add(input_trees[it])
        # Did not add succesfully:
        if chain.GetEntries() == N_entries:
            if N_tree < N_tree_max:
                # Make it add another tree if count did not increase, but stops after the maximum reserve tress are reached.
                N_tree += 1
        else:
            files_added += 1
        it += 1
    
    if chain.GetEntries() == 0:
        print "Something went wrong, your chain is empty!"
        return 1
    return (copy(chain),files_added)


def get_chainsingle(sample_directory, root_tree_name,Ttree_name = "events"):
    if not sample_directory.endswith("/"):
        sample_directory = sample_directory+"/"
    if root_tree_name.endswith(".root"):
        input_tree = OUT_dir+sample_directory+root_tree_name
    else:
        input_tree = OUT_dir+sample_directory+root_tree_name+".root"
    chain = rt.TChain(Ttree_name,Ttree_name)
    chain.Add(input_tree)
    if chain.GetEntries() == 0:
        print "Something went wrong, your chain is empty!"
        return 1
    return copy(chain)



# Unit tests

def test_getchainsingle():
    my_chain1 = get_chainsingle("tt/","tree_1.root")
    my_chain2 = get_chainsingle("tt/","tree_2")
    
    print my_chain1
    print "My chain for tt/tree_1.root has ",my_chain1.GetEntries()," entries"
    print "My chain for tt/tree_2.root has ",my_chain2.GetEntries()," entries"
    
    return 0
    
def test_getchainlist():
    
    chain,nfiles = get_chainlist("dilep/","tree_",20,28)
    
    print "This chain contains TTrees from ",nfiles," files, and has ",chain.GetEntries(), " events inside! "
    
    return 0


#test_getchainsingle()
#test_getchainlist()











