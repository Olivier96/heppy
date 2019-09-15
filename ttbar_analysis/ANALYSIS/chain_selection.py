import os, sys
import ROOT as rt
#import math
from histo_properties import *

#cards = ['tt', 'dilep', 'had', 'ww', 'zz', 'hz']
#card_index = 
#
######## DATA SELECTION######################################
## Modify the following to change the data to select
## sample_dir can be a STRING or a LIST containing strings
#sample_dir = cards[card_index]+'/'
#output_dir = sample_dir
##output_dir = 'splitmtop_1718/'
#
######## BOOK KEEPING #######################################
## Do not modify these variables:
#OUT_dir = '~/testFCC/Nicolo/heppy/ttbar_analysis/ANALYSIS/OUT/'
#PLOTS_dir = 'PLOTS/'
#input_files = ['tree_'+str(j)+'.root' for j in range(40)]
##input_files = 'tt_semilepton_ILD_Chunk0/heppy.analyzers.tree.TreeTTSemilep.TreeTTSemilep_1/tree.root'
#
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
#
## Create an empty root file, then add into it later using save_histo 
## output file
#root_outfile = rt.TFile(path_to_output_file,"RECREATE")
#root_outfile.cd() # necessary to save file
## Save and Close the root file
#root_outfile.Write()
#root_outfile.Close()
#
##creer chain object
#ch = rt.TChain("events","events") # de naam van de tree is belangrijk! Dat is hoe root die in the file vindt!
#
#
## voeg de files toe
#if type(path_to_input_file) == str:
#    ch.Add(path_to_input_file)
#elif type(path_to_input_file) == list:
#    for rootfile in path_to_input_file:
#        ch.Add(rootfile)
##ch.Add("OUT/had_*/tt_semilepton_ILD_Chunk0/heppy.analyzers.tree.TreeTTSemilep.TreeTTSemilep_1/tree.root")
#
#print "Entries in TChain: ",ch.GetEntries()
#exit()

##########################################################

############### DRAW HISTO FUNCTIONS ###########################

def save_histo(ch, histo):
    # Handle root file
    root_outfile = rt.TFile(histo.filename,"UPDATE")
    root_outfile.cd()
    # Create the no cut histo first, then write it to the root file
    temp_histo_name = histo.histo_name+"_nocut"
    temp_histo = rt.TH1D(temp_histo_name, "nocut",histo.n_bins, histo.x_min, histo.x_max)
    if histo.overflow:
        to_draw = "min({var},{x_max})".format(var = histo.var, x_max= histo.x_max-((histo.x_max-histo.x_min)/(histo.n_bins)))
        xtitle = histo.var+"_of"
    elif histo.underflow:
        to_draw = "max({var},{x_min})".format(var = histo.var, x_min=histo.x_min+((histo.x_max-histo.x_min)/(histo.n_bins)))
        xtitle = histo.var+"_uf"
    else:
        to_draw = histo.var
        xtitle = histo.var
    temp_histo.SetXTitle(xtitle)
    ch.Draw(to_draw+" >> "+temp_histo_name, histo.default_cuts)
    temp_histo.Write()
    # Now create the same plots for all cuts
    cut_string = ""
    for ic,cut in enumerate(histo.cuts):
        if cut_string == "":
            cut_string = cut
        else:
            cut_string = cut_string+" && "+cut
        # Override the histo with a new name for different cuts
        temp_histo_name = histo.histo_name+"_cut"+str(ic+1)
        temp_histo = rt.TH1D(temp_histo_name, cut_string, histo.n_bins, histo.x_min, histo.x_max)
        temp_histo.SetXTitle(xtitle)
        if histo.default_cuts != "":
            ch.Draw(to_draw+" >> "+temp_histo_name, histo.default_cuts+" && "+cut_string)
        else:
            ch.Draw(to_draw+" >> "+temp_histo_name, cut_string)
        temp_histo.Write()
    # Save and Close the root file
    root_outfile.Write()
    root_outfile.Close()
    return 0

def save_histo_list(histo_list, chain):
    for histo in histo_list:
        save_histo(chain, histo)
    return 0

########################################################

############# DEFINE CLASS OBJECTS FOR THE HISTOS ################

cuts = ["four_jets_mass > 150", "four_jets_mass < 270", "min_jets_mass > 10", "second_min_jets_mass > 20", "lep1_e < 100", "missing_rec_e > 20", "chi2_top_constrainer <= 40 ", "success == 1"]
#filename = path_to_output_file
pi_ = 3.14159

def generate_histo_properties(filename, cuts):
    jet1_e = histo_properties(filename,"jet1_e",100,0,140,"jet1_e",cuts, overflow = True)
    jet2_e = histo_properties(filename,"jet2_e",100,0,140,"jet2_e",cuts, overflow = True)
    jet3_e = histo_properties(filename,"jet3_e",100,0,140,"jet3_e",cuts, overflow = True)
    jet4_e = histo_properties(filename,"jet4_e",100,0,140,"jet4_e",cuts, overflow = True)
    jet1_m = histo_properties(filename,"jet1_m",100,0,140,"jet1_m",cuts, overflow = True)
    jet2_m = histo_properties(filename,"jet2_m",100,0,140,"jet2_m",cuts, overflow = True)
    jet3_m = histo_properties(filename,"jet3_m",100,0,140,"jet3_m",cuts, overflow = True)
    jet4_m = histo_properties(filename,"jet4_m",100,0,140,"jet4_m",cuts, overflow = True)

    jet1_logbtag = histo_properties(filename, "jet1_logbtag", 50,-1, 10, "jet1_logbtag", cuts, underflow = True)
    jet1_log10btag = histo_properties(filename, "abs(jet1_log10btag)", 50,-1, 10, "jet1_log10btag", cuts, overflow = True)

    lep1_e_full = histo_properties(filename, "lep1_e", 100, 0, 150, "lep1_e_full", cuts)
    lep1_e_cuts = histo_properties(filename, "lep1_e", 100, 0, 100, "lep1_e_cuts", cuts)

    four_jets_mass_cuts = histo_properties(filename, "four_jets_mass", 100, 150, 270, "four_jets_mass_cuts", cuts)
    four_jets_mass_full =  histo_properties(filename, "four_jets_mass", 100, 0, 300, "four_jets_mass_full", cuts)

    min_jets_mass                     = histo_properties(filename, "min_jets_mass", 100, 10, 100, "min_jets_mass", cuts)
    min_jets_mass_full              = histo_properties(filename, "min_jets_mass", 100, 0, 100, "min_jets_mass_full", cuts)
    second_min_jets_mass_full   = histo_properties(filename, "second_min_jets_mass", 100, 0, 110, "second_min_jets_mass_full", cuts)
    second_min_jets_mass          = histo_properties(filename, "second_min_jets_mass", 100, 20, 110, "second_min_jets_mass", cuts)
    max_jets_mass = histo_properties(filename, "max_jets_mass", 100, 70, 200, "max_jets_mass", cuts)

    min_jets_angle = histo_properties(filename, "min_jets_angle", 100, -pi_, pi_, "min_jets_angle", cuts)
    second_min_jets_angle = histo_properties(filename, "second_min_jets_angle", 100, -pi_, pi_, "second_min_jets_angle", cuts)
    min_jets_lepton_angle = histo_properties(filename, "min_jets_lepton_angle", 100, -pi_, pi_, "min_jets_lepton_angle", cuts)

    lep_pt_wrt_closest_jet = histo_properties(filename, "lep_pt_wrt_closest_jet", 100, 0, 100, "lep_pt_wrt_closest_jet", cuts)
    total_rec_mass = histo_properties(filename, "total_rec_mass", 100, 130, 320, "total_rec_mass", cuts)
    missing_rec_e = histo_properties(filename, "missing_rec_e", 100, 20, 170, "missing_rec_e", cuts)

    chi2_algorithm_cuts = histo_properties(filename, "chi2_algorithm", 100, 0, 40, "chi2_algorithm_cuts", cuts)#, overflow = True)
    chi2_algorithm_full = histo_properties(filename, "chi2_algorithm", 100, 0, 120, "chi2_algorithm_full", cuts)#, overflow = True)
    chi2_top_constrainer = histo_properties(filename, "chi2_top_constrainer", 100, 0, 40, "chi2_top_constrainer", cuts, overflow = True)

    mc_tquark1_e = histo_properties(filename, "mc_tquark1_e", 20, 165, 185, "mc_tquark1_e", cuts)
    mc_tquark2_e = histo_properties(filename, "mc_tquark2_e", 20, 165, 185, "mc_tquark2_e", cuts)
    mc_tquark1_m = histo_properties(filename, "mc_tquark1_m", 20, 165, 185,"mc_tquark1_m", cuts)
    mc_tquark2_m = histo_properties(filename, "mc_tquark2_m", 20, 165, 185, "mc_tquark2_m", cuts)

    mc_bquark1_e = histo_properties(filename, "mc_bquark1_e", 100, 0, 100, "mc_bquark1_e", cuts)
    mc_bquark2_e = histo_properties(filename, "mc_bquark2_e", 100, 0, 100, "mc_bquark2_e", cuts)

    mc_w1_e = histo_properties(filename, "mc_w1_e", 20, 70, 90, "mc_w1_e", cuts)
    mc_w2_e = histo_properties(filename, "mc_w2_e", 20, 70, 90, "mc_w2_e", cuts)
    mc_w1_m = histo_properties(filename, "mc_w1_m", 20, 70, 90,"mc_w1_m", cuts)
    mc_w2_m = histo_properties(filename, "mc_w2_m", 20, 70, 90, "mc_w2_m", cuts)


    tophadRec = histo_properties(filename, "tophadRec", 100, 80, 200, "tophadRec", cuts)
    whadRec = histo_properties(filename, "whadRec", 100, 30, 110, "whadRec", cuts)
    toplepRec = histo_properties(filename, "toplepRec", 100, 80, 200, "toplepRec", cuts)
    wlepRec = histo_properties(filename, "wlepRec", 100, 30, 110, "wlepRec", cuts)

    # Store vars for b > jet matching for top decay
    mc_bquark1_index_nearest_jet = histo_properties(filename, "mc_bquark1_index_nearest_jet", 4, 0, 4, "mc_bquark1_index_nearest_jet", ["mc_bquark1_index_nearest_jet > -99"])
    mc_bquark2_index_nearest_jet = histo_properties(filename, "mc_bquark2_index_nearest_jet", 4, 0, 4, "mc_bquark2_index_nearest_jet", ["mc_bquark2_index_nearest_jet > -99"])
    mc_bquark1_delta_alpha_wrt_nearest_jet = histo_properties(filename, "mc_bquark1_delta_alpha_wrt_nearest_jet", 15, 0, 2*pi_,"mc_bquark1_delta_alpha_wrt_nearest_jet", [] )
    mc_bquark2_delta_alpha_wrt_nearest_jet = histo_properties(filename, "mc_bquark2_delta_alpha_wrt_nearest_jet", 15, 0, 2*pi_,"mc_bquark2_delta_alpha_wrt_nearest_jet", [] )
    mc_bquark1_delta_alpha_wrt_nearest_jet_zoom = histo_properties(filename, "mc_bquark1_delta_alpha_wrt_nearest_jet", 40, 0, 0.5,"mc_bquark1_delta_alpha_wrt_nearest_jet_zoom", [] )
    mc_bquark2_delta_alpha_wrt_nearest_jet_zoom = histo_properties(filename, "mc_bquark2_delta_alpha_wrt_nearest_jet", 40, 0, 0.5,"mc_bquark2_delta_alpha_wrt_nearest_jet_zoom", [] )
    mc_bquark1_delta_e_wrt_nearest_jet = histo_properties(filename, "mc_bquark1_delta_e_wrt_nearest_jet", 50, -50, 50, "mc_bquark1_delta_e_wrt_nearest_jet", ["mc_bquark1_delta_e_wrt_nearest_jet > -99"])
    mc_bquark2_delta_e_wrt_nearest_jet = histo_properties(filename, "mc_bquark2_delta_e_wrt_nearest_jet", 50, -50, 50, "mc_bquark2_delta_e_wrt_nearest_jet", ["mc_bquark2_delta_e_wrt_nearest_jet > -99"])
    mc_bquark1_nearest_jet_e = histo_properties(filename, "mc_bquark1_nearest_jet_e", 100, 0, 140, "mc_bquark1_nearest_jet_e", ["mc_bquark1_nearest_jet_e > -99"])
    mc_bquark2_nearest_jet_e = histo_properties(filename, "mc_bquark2_nearest_jet_e", 100, 0, 140, "mc_bquark2_nearest_jet_e", ["mc_bquark2_nearest_jet_e > -99"])
    mc_bquark1_nearest_jet_m = histo_properties(filename, "mc_bquark1_nearest_jet_m", 100, 0, 140, "mc_bquark1_nearest_jet_m", ["mc_bquark1_nearest_jet_m > -99"])
    mc_bquark2_nearest_jet_m = histo_properties(filename, "mc_bquark2_nearest_jet_m", 100, 0, 140, "mc_bquark2_nearest_jet_m", ["mc_bquark2_nearest_jet_m > -99"])

    # Store vars for quark > jets for hadronic W matching 
    mc_quarkjet1_pdgid = histo_properties(filename, "mc_quarkjet1_pdgid", 20, -10, 10, "mc_quarkjet1_pdgid", ["mc_quarkjet1_pdgid > -99"] )
    mc_quarkjet2_pdgid = histo_properties(filename, "mc_quarkjet2_pdgid", 20, -10, 10, "mc_quarkjet2_pdgid", ["mc_quarkjet2_pdgid > -99"] )
    mc_quarkjet1_index_nearest_jet = histo_properties(filename, "mc_quarkjet1_index_nearest_jet", 4, 0, 4, "mc_quarkjet1_index_nearest_jet", ["mc_quarkjet1_index_nearest_jet > -99"])
    mc_quarkjet2_index_nearest_jet = histo_properties(filename, "mc_quarkjet2_index_nearest_jet", 4, 0, 4, "mc_quarkjet2_index_nearest_jet", ["mc_quarkjet2_index_nearest_jet > -99"])
    mc_quarkjet1_delta_alpha_wrt_nearest_jet = histo_properties(filename, "mc_quarkjet1_delta_alpha_wrt_nearest_jet", 15, 0, 2*pi_,"mc_quarkjet1_delta_alpha_wrt_nearest_jet", [] )
    mc_quarkjet2_delta_alpha_wrt_nearest_jet = histo_properties(filename, "mc_quarkjet2_delta_alpha_wrt_nearest_jet", 15, 0, 2*pi_,"mc_quarkjet2_delta_alpha_wrt_nearest_jet", [] )
    mc_quarkjet1_delta_alpha_wrt_nearest_jet_zoom = histo_properties(filename, "mc_quarkjet1_delta_alpha_wrt_nearest_jet", 40, 0, .5,"mc_quarkjet1_delta_alpha_wrt_nearest_jet_zoom", [] )
    mc_quarkjet2_delta_alpha_wrt_nearest_jet_zoom = histo_properties(filename, "mc_quarkjet2_delta_alpha_wrt_nearest_jet", 40, 0, 0.5,"mc_quarkjet2_delta_alpha_wrt_nearest_jet_zoom", [] )
    mc_quarkjet1_delta_e_wrt_nearest_jet = histo_properties(filename, "mc_quarkjet1_delta_e_wrt_nearest_jet", 50, -50, 50, "mc_quarkjet1_delta_e_wrt_nearest_jet", ["mc_quarkjet1_delta_e_wrt_nearest_jet > -99"])
    mc_quarkjet2_delta_e_wrt_nearest_jet = histo_properties(filename, "mc_quarkjet2_delta_e_wrt_nearest_jet", 50, -50, 50, "mc_quarkjet2_delta_e_wrt_nearest_jet", ["mc_quarkjet2_delta_e_wrt_nearest_jet > -99"])
    mc_quarkjet1_nearest_jet_e = histo_properties(filename, "mc_quarkjet1_nearest_jet_e", 100, 0, 140, "mc_quarkjet1_nearest_jet_e", ["mc_quarkjet1_nearest_jet_e > -99"])
    mc_quarkjet2_nearest_jet_e = histo_properties(filename, "mc_quarkjet2_nearest_jet_e", 100, 0, 140, "mc_quarkjet2_nearest_jet_e", ["mc_quarkjet2_nearest_jet_e > -99"])
    mc_quarkjet1_nearest_jet_m = histo_properties(filename, "mc_quarkjet1_nearest_jet_m", 100, 0, 140, "mc_quarkjet1_nearest_jet_m", ["mc_quarkjet1_nearest_jet_m > -99"])
    mc_quarkjet2_nearest_jet_m = histo_properties(filename, "mc_quarkjet2_nearest_jet_m", 100, 0, 140, "mc_quarkjet2_nearest_jet_m", ["mc_quarkjet2_nearest_jet_m > -99"])

    # Additional variables necessary for matching:

    mc_lepton1_e = histo_properties(filename, "mc_lepton1_e", 100, 10, 100, "mc_lepton1_e", ["mc_lepton1_e > -99"])
    mc_lepton2_e = histo_properties(filename, "mc_lepton2_e", 100, 10, 100, "mc_lepton2_e", ["mc_lepton2_e > -99"])
    lepton_ediff = histo_properties(filename, "mc_lepton_e - lep1_e", 15, -10, -10, "lepton_ediff", [])

    mc_neutrino1_e = histo_properties(filename, "mc_neutrino1_e", 40, 0, 120, "mc_neutrino1_e", ["mc_neutrino1_e > -99"])
    mc_neutrino2_e = histo_properties(filename, "mc_neutrino2_e", 40, 0, 120, "mc_neutrino2_e", ["mc_neutrino2_e > -99"])
    neutrino_ediff = histo_properties(filename, "mc_neutrino_e - missing_rec_e", 60, -80, 20, "neutrino_ediff", [])


# Add Nicolo's 



# Now create a list containing all objects
    short_list = [jet1_e,lep1_e,four_jets_mass_cuts,chi2_top_constrainer,missing_rec_e, second_min_jets_mass,min_jets_mass, tophadRec]

    histo_list = [jet1_e,
                     jet2_e,
                     jet3_e,
                     jet4_e,
                     jet1_m,
                     jet2_m,
                     jet3_m,
                     jet4_m,
                     #jet1_logbtag,
                     #jet1_log10btag,
                     lep1_e,
                     four_jets_mass_full,
                     four_jets_mass_cuts,
                     min_jets_mass,
                     second_min_jets_mass,
                     max_jets_mass,
                     min_jets_angle,
                     second_min_jets_angle,
                     min_jets_lepton_angle,
                     lep_pt_wrt_closest_jet,
                     total_rec_mass,
                     missing_rec_e,
                     #chi2_algorithm_cuts,
                     #chi2_algorithm_full,
                     chi2_top_constrainer,
                     mc_bquark1_e,
                     mc_bquark2_e,
                     mc_tquark1_e,
                     mc_tquark2_e,
                     mc_tquark1_m,
                     mc_tquark2_m,
                     mc_w1_e,
                     mc_w2_e,
                     mc_w1_m,
                     mc_w2_m,
                     tophadRec,
                     whadRec,
                     toplepRec,
                     wlepRec,
                     mc_bquark1_index_nearest_jet,
                     mc_bquark2_index_nearest_jet,
                     mc_bquark1_delta_alpha_wrt_nearest_jet,
                     mc_bquark2_delta_alpha_wrt_nearest_jet,
                     mc_bquark1_delta_e_wrt_nearest_jet,
                     mc_bquark2_delta_e_wrt_nearest_jet,
                     mc_bquark1_nearest_jet_e,
                     mc_bquark2_nearest_jet_e,
                     mc_bquark1_nearest_jet_m,
                     mc_bquark2_nearest_jet_m,
                     mc_quarkjet1_pdgid,
                     mc_quarkjet2_pdgid,
                     mc_quarkjet1_index_nearest_jet,
                     mc_quarkjet2_index_nearest_jet,
                     mc_quarkjet1_delta_alpha_wrt_nearest_jet,
                     mc_quarkjet2_delta_alpha_wrt_nearest_jet,
                     mc_quarkjet1_delta_e_wrt_nearest_jet,
                     mc_quarkjet2_delta_e_wrt_nearest_jet,
                     mc_quarkjet1_nearest_jet_e,
                     mc_quarkjet2_nearest_jet_e,
                     mc_quarkjet1_nearest_jet_m,
                     mc_bquark2_nearest_jet_m,
                     mc_lepton1_e,
                     mc_lepton2_e,
                     #lepton_ediff,
                     mc_neutrino1_e,
                     mc_neutrino2_e,
                     #neutrino_ediff,
                     mc_bquark1_delta_alpha_wrt_nearest_jet_zoom,
                     mc_bquark2_delta_alpha_wrt_nearest_jet_zoom,
                     mc_quarkjet1_delta_alpha_wrt_nearest_jet_zoom,
                     mc_quarkjet2_delta_alpha_wrt_nearest_jet_zoom
                     ]
                     
                     
    report_list = [lep1_e,
                     four_jets_mass_full,
                     four_jets_mass_cuts,
                     min_jets_mass,
                     min_jets_mass_full,
                     second_min_jets_mass,
                     second_min_jets_mass_full,
                     total_rec_mass,
                     missing_rec_e,
                     chi2_top_constrainer,
                     mc_bquark1_delta_alpha_wrt_nearest_jet_zoom,
                     mc_bquark2_delta_alpha_wrt_nearest_jet_zoom,
                     mc_quarkjet1_delta_alpha_wrt_nearest_jet_zoom,
                     mc_quarkjet2_delta_alpha_wrt_nearest_jet_zoom,
                     #lep_angle, from chain_loop!
                     #neutrino_angle, from chain_loop!
                     #chi2, from chain_loop!
                     #thad_mass,
                     #whad_mass,
                     #tlep_mass,
                     #wlep_mass,
                     ]
                 
    return (short_list, histo_list, report_list)
                 



# Finally call the function for the list 
#save_histo_list(short_list)
#print sample_dir
#save_histo_list(histo_list)
#save_histo_list([mc_bquark1_delta_alpha_wrt_nearest_jet_zoom,mc_bquark2_delta_alpha_wrt_nearest_jet_zoom,mc_quarkjet2_delta_alpha_wrt_nearest_jet_zoom,mc_quarkjet1_delta_alpha_wrt_nearest_jet_zoom])
