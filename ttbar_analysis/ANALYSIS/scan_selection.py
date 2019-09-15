from get_chain import * #get_chainsingle,get_chainlist  # NOTE: no need to add OUT_dir to the sample!! 
import ROOT as rt
from chain_selection import save_histo_list, generate_histo_properties
from histo_properties import *
from nice_histo import save_histo_to_image, save_params_to_txt, get_params_fit
from layered_histos import save_thstack_to_image, save_thstack_to_image_noratio, prepare_ROC_histos
from chain_loop import mcmatch_histo_wtop, chi2_algorithm, chi2_algorithm_withcuts,chi2_algorithm_withcuts_ROC
from nice_graphs import prepare_ROC_graphs,make_graphs_pythia
from nice_table import full_cutflow_table_to_file, full_cutflow_table_to_file_eff,mtop_sqrts_table
from cut_flow import efficiency_uncertainty
from generate_scales import scale_matrix_list

mtop = ["1718","1726","1730","1734","1742"]
sqrts = ["340","342","344", "346", "350"]
cards = ["tt", "dilep", "had", "hz", "zz", "ww"]

sample_dirs = [[ "m"+mtop[i]+"_s"+sqrts[j]+"/" for i in range(len(mtop)) ] for j in range(len(sqrts)) ]
sample_dirs = [item for sublist in sample_dirs for item in sublist]
sample_subdirs = []

for sample in sample_dirs:
    if "1730" in sample:
        for c in cards:
            sample_subdirs.append(sample+c+"/")
    else:
        sample_subdirs.append(sample+"tt/")
        
print sample_subdirs,len(sample_subdirs)
#exit()
#print report_list 

cuts = ["four_jets_mass > 150", "four_jets_mass < 270", "min_jets_mass > 10", "second_min_jets_mass > 20", "lep1_e < 100", "missing_rec_e > 20"]# "chi2_top_constrainer <= 40 ", "success == 1"]
cuts_tt = [ "decay_channel == 1" , "four_jets_mass > 150", "four_jets_mass < 270", "min_jets_mass > 10", "second_min_jets_mass > 20", "lep1_e < 100", "missing_rec_e > 20"]


############ HELPER FUNCTION ##########################

def histo_list_setfilename(histo_list, filename):
    for object in histo_list:
        object.filename = filename
    return histo_list

def histo_list_setcuts(histo_list, cuts):
    for object in histo_list:
        object.cuts = cuts
    return histo_list
    
def histo_list_setdefaultcuts(histo_list, default_cuts):
    for object in histo_list:
        object.default_cuts = default_cuts
    return histo_list
    
 
########## END HELPER FUNCTION ##########################

sample_chi2params = "tt/"


# In the same order as cards!
# Note: need to recalculate first 3 numbers using data from Mail Freya TODO !!
scales = [337500, 67500, 345000, 130000, 500000, 5000000]
 
 
 
 # Determine CHI2 parameters:
 
def run_chi2params():
    sample= 'chi2_params/'
    OUT_dir = 'OUT/'
    PLOTS_dir = 'PLOTS/'

    #rootname = 'selection_histograms.root'
    rootname = 'looper_histograms.root'
    fitname= 'fit_chi2_parameters.txt'
    sample_dir = PLOTS_dir+sample
    fitter = "gaus"
    extension = 'pdf'
    
    # UNCOMMENT HERE TO RERUN params rootfile
    chain_chi2params, nfiles_chi2params = get_chainlist(sample, "tree_", 400, 400)
    
    # Calculate the efficiency and uncertainties of the chi2_param
#    chi2_param_eventsmcmatched = 50484.0 # grabbed this value manually from the histos in looper_histograms.root (rootname)
#    chi2_param_eventstotal = nfiles_chi2params*2500.
#    eff_chi2_param = efficiency_uncertainty(chi2_param_eventsmcmatched, chi2_param_eventstotal)
#    print eff_chi2_param
#    exit()
    #mcmatch_histo_wtop(chain_chi2params, PLOTS_dir+sample+rootname)

    # Function calls for determining chi2 parameters:
    chi2_parameters = []

    chi2_parameters.append( save_histo_to_image(sample_dir, rootname, "wmass_had1", "m_{W}^{had}     (GeV)", "arbitrary units", extension, fit = fitter, subrange = True, scale = -1))
    chi2_parameters.append( save_histo_to_image(sample_dir, rootname, "tmass_had1", "m_{t}^{had}     (GeV)", "arbitrary units", extension, fit = fitter, subrange = True, scale = -1))
    chi2_parameters.append( save_histo_to_image(sample_dir, rootname, "wmass_lep", "m_{W}^{lep}     (GeV)", "arbitrary units", extension, fit = fitter, subrange = True, scale = -1))
    chi2_parameters.append( save_histo_to_image(sample_dir, rootname, "tmass_lep", "m_{t}^{lep}     (GeV)", "arbitrary units", extension, fit = fitter, subrange = True, scale = -1))
    
    save_params_to_txt(chi2_parameters, sample_dir+fitname)
    return 0
 
# UNCOMMENT HERE TO RUN CHI2PARAM DETERMINATION
#run_chi2params()

# Results from chi2 fit:
# mw_had,sw_had,mt_had,st_had,mw_lep,sw_lep,mt_lep,st_lep
param_list_Nicolo = [81.88, 16.69, 164.59, 17.13, 105.43, 17.37, 177.37, 20.25]
param_list_self = [97.3, 25.31, 163.74, 32.9, 87.5, 9.79, 151.6 , 25.6]


# Now create the histograms using the CHI2 algorithm using the values obtained before
sample_chi2 = [c+"/" for c in cards]
chains_chi2 = [None] * len(sample_chi2)
outnames_chi2 = [None] * len(sample_chi2)
outnames_chi2cuts = [None] * len(sample_chi2)
outnames_chi2_ROC = [None] * len(sample_chi2)
nfiles_chains_chi2 = [None] * len(sample_chi2)

def run_chi2histos(skip = False,skip_ROC = False, chi2_cut = 100000,chi2_alt_cut = 10000000,chi2_alt2_cut = 10000000, chi2_nicolo_cut = 1000000):
    for i,sample in enumerate(sample_chi2):
        chains_chi2[i],nfiles_chains_chi2[i]  = get_chainlist(sample, "tree_", 40, 40)
        #print chains_chi2
        is_full_tt = ('tt' in sample)
        outnames_chi2[i] = PLOTS_dir+sample+"chi2_algorithm.root"
        outnames_chi2cuts[i] = PLOTS_dir+sample+"chi2_algorithm_cuts.root"
        outnames_chi2_ROC[i] = PLOTS_dir+sample+"chi2_algorithm_ROC.root"
        # NO chi2 cut yet:
        if not skip:
            #chi2_algorithm(chains_chi2[i], outnames_chi2[i] ,param_list_self ,is_full_tt)
            chi2_algorithm_withcuts(chains_chi2[i], outnames_chi2cuts[i], param_list_self, is_full_tt, chi2_cut,chi2_alt_cut,chi2_alt2_cut,chi2_nicolo_cut)
        if not skip_ROC:
            chi2_algorithm_withcuts_ROC(chains_chi2[i], outnames_chi2_ROC[i], param_list_self, is_full_tt)
    return 0

# UNCOMMENT HERE TO RUN CHI2 HSITOGRAMS /// set skip = False
skip = True
skip_ROC = True
chi2_cut_4 = 1.35
chi2_cut_3 = 0.45
chi2_cut_5 = 1.5
chi2_nicolo_cut = 6.3
run_chi2histos(skip, skip_ROC,chi2_cut = chi2_cut_4,chi2_alt_cut = chi2_cut_3, chi2_alt2_cut = chi2_cut_5, chi2_nicolo_cut = chi2_nicolo_cut)



# Now use the chi2 graphs to produce the stack plots for chi2 and for the cuts! 
fitter = "gaus"
extension = 'pdf'
def run_chi2graphs_individual(sample, rootname):
    if "PLOTS/" not in sample:
        sample = PLOTS_dir+sample
    print sample+rootname
    save_histo_to_image(sample,rootname, "wmass_had1", "m_{W}^{had}     (GeV)", "arbitrary units", extension, fit = fitter, subrange = True, scale = -1)
    save_histo_to_image(sample,rootname, "tmass_had1", "m_{t}^{had}     (GeV)", "arbitrary units", extension, fit = fitter, subrange = True, scale = -1)
    save_histo_to_image(sample,rootname, "wmass_lep", "m_{W}^{lep}     (GeV)", "arbitrary units", extension, fit = fitter, subrange = True, scale = -1)
    save_histo_to_image(sample,rootname, "tmass_lep", "m_{t}^{lep}     (GeV)", "arbitrary units", extension, fit = fitter, subrange = True, scale = -1)
    save_histo_to_image(sample,rootname, "chi2_histo1", "#chi^{2}", "arbitrary units", extension, scale = -1)
    save_histo_to_image(sample,rootname, "chi2_histo2", "#chi^{2}", "arbitrary units", extension, scale = -1)
    return 0

rootname = "chi2_algorithm.root"
#run_chi2graphs_individual(sample_chi2[0], rootname)
#print outnames_chi2

rootname_cuts = "chi2_algorithm_cuts.root"
#run_chi2graphs_individual(sample_chi2[0], rootname_cuts)
N_ww = 1000000
N_hz = 26000
N_zz = 100000
# Deprecated values, use the ones from generate_scales.py import!
#scales_list_340 = [7277, 1720, 7542 ,N_hz, N_zz, N_ww ]
#scales_list_342 = [20886, 4936, 21645,N_hz, N_zz, N_ww ]
#scales_list_344 = [47857,11311, 49597,N_hz, N_zz, N_ww ]
#scales_list_346 = [46326,10949,48011,N_hz, N_zz, N_ww ]
#scales_list_350 = [48352, 11428, 50111,N_hz, N_zz, N_ww ]
#scales_matrix = [scales_list_340,scales_list_342 ,scales_list_344 ,scales_list_346 ,scales_list_350]
# Extract the matrix for mtop = 173 GeV
scales_matrix = scale_matrix_list[2]
scales_list_350 = scales_matrix[-1]



fillstyles_original = [3001, 3002, 3003, 3004, 3005, 3006, 3007]
fillcolours_original = [rt.kBlue,rt.kGreen+1, rt.kRed, rt.kAzure+7, rt.kCyan+2,rt.kTeal+7, rt.kSpring+7, rt.kOrange+7, rt.kPink-3, rt.kMagenta, rt.kViolet-6]


# ALL = bad combo + good combo together, combinations = good and bad separated!!!!
#             WW, ZZ, HZ, had, dilep, bad combo signal, good combo signal
fillstyles_combinations = [3010, 3017, 3018, 3004, 3005, 3002, 3144]
fillstyles_all = [3010, 3017, 3018, 3004, 3005, 3144]
fillcolours_combinations = [rt.kGreen, rt.kGreen+1, rt.kGreen+2,rt.kBlue, rt.kBlue-4,rt.kMagenta+1,rt.kRed]
fillcolours_all = [rt.kGreen, rt.kGreen+1, rt.kGreen+2,rt.kBlue, rt.kBlue-4,rt.kRed]

legend_title = "#cuts: 7 " # before chi2 cut!
flavour_text = "FCC-ee ILD L_{int} = 0.2 ab^{-1} #sqrt{s} = 350 GeV"
frac = "fraction"
frac_text = "N_{BG}-N_{S} / N_{S}"
diff = "diff"
diff_text = "N_{BG}-N_{S}"
div = "divide"
divide_text = "N_{BG}/N_{S}"

def run_chi2graphs_stack(outnames_chi2, output_dir, legend_title= ""):
    #save_thstack_to_image(rootname_list, histo_name_list,legend_list,legend_spot, output_file,xlabel,ylabel, log = "", stack_option = "", rebin = 0, ratiomode = None, ref_ratio_index = -1, ylabel_ratio):
    tr = "topright"
    tl = "topleft"
    cr = "centre"
    legend_list = ["t#bar{t} semi-lepton", "t#bar{t} di-lepton", "t#bar{t} hadronic", "HZ", "ZZ", "WW"]
    legend_list.reverse()
    # Style predefined objects:
    ylabel = "Events"
    
    n_rebin = 2
    print outnames_chi2[::-1],nfiles_chains_chi2[::-1],scales_list_350[::-1] ,"chi2_histo1", legend_list, tr,  PLOTS_dir+output_dir+"chi2_histo1"+"."+extension,  "#chi^{2}_{3}", ylabel, fillcolours_all
    ###############################################################
    #                                                                   REGULAR STACKS                                                         #
    ###############################################################
    save_thstack_to_image(outnames_chi2[::-1],nfiles_chains_chi2[::-1],scales_list_350[::-1] ,"chi2_histo1", legend_list, tr,  PLOTS_dir+output_dir+"chi2_histo1"+"."+extension,  "#chi^{2}_{3}", ylabel, fillcolours_all, fillstyles_all,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y")
    save_thstack_to_image(outnames_chi2[::-1], nfiles_chains_chi2[::-1],scales_list_350[::-1] ,"chi2_histo2", legend_list, tr,  PLOTS_dir+output_dir+"chi2_histo2"+"."+extension,  "#chi^{2}_{3}", ylabel, fillcolours_all, fillstyles_all,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y")
    save_thstack_to_image(outnames_chi2[::-1], nfiles_chains_chi2[::-1],scales_list_350[::-1] ,"wmass_had1", legend_list, tr,  PLOTS_dir+output_dir+"wmass_had1"+"."+extension,  "m_{W}^{had}     (GeV)", ylabel, fillcolours_all, fillstyles_all,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin=n_rebin)
    save_thstack_to_image(outnames_chi2[::-1], nfiles_chains_chi2[::-1],scales_list_350[::-1] ,"tmass_had1", legend_list, tr,  PLOTS_dir+output_dir+"tmass_had1"+"."+extension, "m_{t}^{had}     (GeV)",ylabel, fillcolours_all, fillstyles_all, ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin=n_rebin)
    save_thstack_to_image(outnames_chi2[::-1], nfiles_chains_chi2[::-1],scales_list_350[::-1] ,"wmass_lep", legend_list, tr,  PLOTS_dir+output_dir+"wmass_lep"+"."+extension,  "m_{W}^{lep}     (GeV)",ylabel, fillcolours_all, fillstyles_all, ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin=n_rebin)
    save_thstack_to_image(outnames_chi2[::-1], nfiles_chains_chi2[::-1],scales_list_350[::-1] ,"tmass_lep", legend_list, tr,  PLOTS_dir+output_dir+"tmass_lep"+"."+extension,  "m_{t}^{lep}     (GeV)",ylabel, fillcolours_all, fillstyles_all,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin=n_rebin)
#    save_thstack_to_image(outnames_chi2[::-1],nfiles_chains_chi2[::-1],scales_list_350[::-1] ,"chi2_nicolo1", legend_list, tr,  PLOTS_dir+output_dir+"chi2_nicolo1"+"."+extension,  "#chi^{2}_{Kin}", ylabel, fillcolours_all, fillstyles_all,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y")
    
    ###############################################################
    #                                                                   TAU STACKS                                                                   #
    ###############################################################
    # discriminate for signal for tau leptons vs e,mu leptons
    
    stacks_outnames_chi2 = outnames_chi2[::-1]
    stacks_outnames_chi2.append(outnames_chi2[0])
    scales_350_stacks = scales_list_350[::-1]
    scales_350_stacks.append(scales_list_350[0])
    nfiles_stacks = nfiles_chains_chi2[:]
    nfiles_stacks.insert(0,nfiles_chains_chi2[0])
    nfiles_stacks.reverse()
    
    output_dir_tau = output_dir[:-1]+"_tau/"
    fillcolours_combinations = [rt.kGreen, rt.kGreen+1, rt.kGreen+2,rt.kBlue, rt.kBlue-4,rt.kViolet+2,rt.kRed]
    legends_tau = ["WW","ZZ","HZ", "t#bar{t} hadronic","t#bar{t} di-lepton","t#bar{t} semi-lep (#tau^{-})","t#bar{t} semi-lep (e^{-},#mu^{-})"]
    chi2_histo1_taus = ["chi2_histo1"]*(len(legends_tau))
    chi2_histo1_taus[-2] = chi2_histo1_taus[-2]+"_tau"
    chi2_histo1_taus[-1] = chi2_histo1_taus[-1]+"_notau"
    
    chi2_histo2_taus = ["chi2_histo2"]*(len(legends_tau))
    chi2_histo2_taus[-2] = chi2_histo2_taus[-2]+"_tau"
    chi2_histo2_taus[-1] = chi2_histo2_taus[-1]+"_notau"
    
    wmass_had1_taus = ["wmass_had1"]*(len(legends_tau))
    wmass_had1_taus[-2] = wmass_had1_taus[-2]+"_tau"
    wmass_had1_taus[-1] = wmass_had1_taus[-1]+"_notau"
    
    tmass_had1_taus = ["tmass_had1"]*(len(legends_tau))
    tmass_had1_taus[-2] = tmass_had1_taus[-2]+"_tau"
    tmass_had1_taus[-1] = tmass_had1_taus[-1]+"_notau"
    
    wmass_lep_taus = ["wmass_lep"]*(len(legends_tau))
    wmass_lep_taus[-2] = wmass_lep_taus[-2]+"_tau"
    wmass_lep_taus[-1] = wmass_lep_taus[-1]+"_notau"
    
    tmass_lep_taus = ["tmass_lep"]*(len(legends_tau))
    tmass_lep_taus[-2] = tmass_lep_taus[-2]+"_tau"
    tmass_lep_taus[-1] = tmass_lep_taus[-1]+"_notau"
    
    print stacks_outnames_chi2, chi2_histo1_taus, chi2_histo2_taus, wmass_had1_taus, tmass_had1_taus, wmass_lep_taus, tmass_lep_taus
    
    save_thstack_to_image(stacks_outnames_chi2,nfiles_stacks,scales_350_stacks ,chi2_histo1_taus, legends_tau, tr,  PLOTS_dir+output_dir_tau+"chi2_histo1"+"."+extension,  "#chi^{2}_{3}", ylabel, fillcolours_combinations, fillstyles_combinations,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y")
    save_thstack_to_image(stacks_outnames_chi2,nfiles_stacks,scales_350_stacks ,chi2_histo2_taus, legends_tau, tr,  PLOTS_dir+output_dir_tau+"chi2_histo2"+"."+extension,  "#chi^{2}_{3}", ylabel, fillcolours_combinations, fillstyles_combinations,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y")
    save_thstack_to_image(stacks_outnames_chi2,nfiles_stacks,scales_350_stacks ,wmass_had1_taus, legends_tau, tr,  PLOTS_dir+output_dir_tau+"wmass_had1"+"."+extension,  "m_{W}^{had}     (GeV)", ylabel, fillcolours_combinations, fillstyles_combinations,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin=n_rebin)
    save_thstack_to_image(stacks_outnames_chi2,nfiles_stacks,scales_350_stacks ,tmass_had1_taus, legends_tau, tr,  PLOTS_dir+output_dir_tau+"tmass_had1"+"."+extension, "m_{t}^{had}     (GeV)",ylabel, fillcolours_combinations, fillstyles_combinations, ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin=n_rebin)
    save_thstack_to_image(stacks_outnames_chi2,nfiles_stacks,scales_350_stacks ,wmass_lep_taus, legends_tau, tr,  PLOTS_dir+output_dir_tau+"wmass_lep"+"."+extension,  "m_{W}^{lep}     (GeV)",ylabel, fillcolours_combinations, fillstyles_combinations, ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin=n_rebin)
    save_thstack_to_image(stacks_outnames_chi2,nfiles_stacks,scales_350_stacks ,tmass_lep_taus, legends_tau, tr,  PLOTS_dir+output_dir_tau+"tmass_lep"+"."+extension,  "m_{t}^{lep}     (GeV)",ylabel, fillcolours_combinations, fillstyles_combinations,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin=n_rebin)
    
    
    ###############################################################
    #                                                                   GOOD/BAD STACKS                                                       #
    ###############################################################
    # discriminate between signal for good combination vs bad combination
    
    output_dir_combo = output_dir[:-1]+"_combo/"
    fillcolours_combinations = [rt.kGreen, rt.kGreen+1, rt.kGreen+2,rt.kBlue, rt.kBlue-4,rt.kRed-7,rt.kRed]
    fillstyles_combinations2 = [3010, 3017, 3018, 3004, 3005, 3244, 3144]
    legends_combo = ["WW","ZZ","HZ", "t#bar{t} hadronic","t#bar{t} di-lepton","t#bar{t} semi-lep (BC)","t#bar{t} semi-lep (GC)"]
    chi2_histo1_combo = ["chi2_alt_histo1"]*(len(legends_tau))
    chi2_histo1_combo[-2] = chi2_histo1_combo[-2]+"_bc"
    chi2_histo1_combo[-1] = chi2_histo1_combo[-1]+"_gc"
    
    chi2_histo2_combo = ["chi2_alt_histo2"]*(len(legends_tau))
    chi2_histo2_combo[-2] = chi2_histo2_combo[-2]+"_bc"
    chi2_histo2_combo[-1] = chi2_histo2_combo[-1]+"_gc"
    
    wmass_had1_combo = ["wmass_had1"]*(len(legends_tau))
    wmass_had1_combo[-2] = wmass_had1_combo[-2]+"_bc"
    wmass_had1_combo[-1] = wmass_had1_combo[-1]+"_gc"
    
    tmass_had1_combo = ["tmass_had1"]*(len(legends_tau))
    tmass_had1_combo[-2] = tmass_had1_combo[-2]+"_bc"
    tmass_had1_combo[-1] = tmass_had1_combo[-1]+"_gc"
    
    wmass_lep_combo = ["wmass_lep"]*(len(legends_tau))
    wmass_lep_combo[-2] = wmass_lep_combo[-2]+"_bc"
    wmass_lep_combo[-1] = wmass_lep_combo[-1]+"_gc"
    
    tmass_lep_combo = ["tmass_lep"]*(len(legends_tau))
    tmass_lep_combo[-2] = tmass_lep_combo[-2]+"_bc"
    tmass_lep_combo[-1] = tmass_lep_combo[-1]+"_gc"
    
    print stacks_outnames_chi2, chi2_histo1_combo, chi2_histo2_combo, wmass_had1_combo, tmass_had1_combo, wmass_lep_combo, tmass_lep_combo
    
    save_thstack_to_image(stacks_outnames_chi2,nfiles_stacks,scales_350_stacks ,chi2_histo1_combo, legends_combo, tr,  PLOTS_dir+output_dir_combo+"chi2_histo1"+"."+extension,  "#chi^{2}_{3}", ylabel, fillcolours_combinations, fillstyles_combinations2,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y")
    save_thstack_to_image(stacks_outnames_chi2,nfiles_stacks,scales_350_stacks ,chi2_histo2_combo, legends_combo, tr,  PLOTS_dir+output_dir_combo+"chi2_histo2"+"."+extension,  "#chi^{2}_{3}", ylabel, fillcolours_combinations, fillstyles_combinations2,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y")
    save_thstack_to_image(stacks_outnames_chi2,nfiles_stacks,scales_350_stacks ,wmass_had1_combo, legends_combo, tr,  PLOTS_dir+output_dir_combo+"wmass_had1"+"."+extension,  "m_{W}^{had}     (GeV)", ylabel, fillcolours_combinations, fillstyles_combinations2,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin=n_rebin)
    save_thstack_to_image(stacks_outnames_chi2,nfiles_stacks,scales_350_stacks ,tmass_had1_combo, legends_combo, tr,  PLOTS_dir+output_dir_combo+"tmass_had1"+"."+extension, "m_{t}^{had}     (GeV)",ylabel, fillcolours_combinations, fillstyles_combinations2, ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin=n_rebin)
    save_thstack_to_image(stacks_outnames_chi2,nfiles_stacks,scales_350_stacks ,wmass_lep_combo, legends_combo, tr,  PLOTS_dir+output_dir_combo+"wmass_lep"+"."+extension,  "m_{W}^{lep}     (GeV)",ylabel, fillcolours_combinations, fillstyles_combinations2, ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin=n_rebin)
    save_thstack_to_image(stacks_outnames_chi2,nfiles_stacks,scales_350_stacks ,tmass_lep_combo, legends_combo, tr,  PLOTS_dir+output_dir_combo+"tmass_lep"+"."+extension,  "m_{t}^{lep}     (GeV)",ylabel, fillcolours_combinations, fillstyles_combinations2,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin=n_rebin)
    
    
    
    
    ###############################################################
    #                                                                   SPECIAL STACKS                                                            #
    ###############################################################
    # Specials == stack histograms for the pre-selection!
    
    # Done for thesis
    
    save_thstack_to_image(outnames_chi2[::-1],nfiles_chains_chi2[::-1],scales_list_350[::-1] ,"four_jets_mass_special", legend_list, tr,  PLOTS_dir+output_dir+"four_jets_mass_special"+"."+extension,  "m_{4j}     (GeV)", ylabel, fillcolours_all, fillstyles_all,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y")
    save_thstack_to_image(outnames_chi2[::-1], nfiles_chains_chi2[::-1],scales_list_350[::-1] ,"min_jets_mass_special", legend_list, tr,  PLOTS_dir+output_dir+"min_jets_mass_special"+"."+extension,  "m_{2j}^{min}     (GeV)", ylabel, fillcolours_all, fillstyles_all,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin = 2)
    save_thstack_to_image(outnames_chi2[::-1], nfiles_chains_chi2[::-1],scales_list_350[::-1] ,"second_min_jets_mass_special", legend_list, tr,  PLOTS_dir+output_dir+"second_min_jets_mass_special"+"."+extension,  "m_{2j}^{2^{nd} min}     (GeV)", ylabel, fillcolours_all, fillstyles_all,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin = 2)
    save_thstack_to_image(outnames_chi2[::-1], nfiles_chains_chi2[::-1],scales_list_350[::-1] ,"lep1_e_special", legend_list, tr,  PLOTS_dir+output_dir+"lep1_e_special"+"."+extension, "E_{lepton}     (GeV)",ylabel, fillcolours_all, fillstyles_all, ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin = 2)
    save_thstack_to_image(outnames_chi2[::-1], nfiles_chains_chi2[::-1],scales_list_350[::-1] ,"missing_rec_e_special", legend_list, tr,  PLOTS_dir+output_dir+"missing_rec_e_special"+"."+extension,  "#slash{E}^{reco}     (GeV)",ylabel, fillcolours_all, fillstyles_all, ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y",rebin = 2)
    
    
    ###############################################################
    #                                                                   EXTRA STACKS                                                              #
    ###############################################################
    # Additional stacks for interesting plots
    
    file_dR = ["PLOTS/tt/chi2_algorithm_cuts.root"]*6
    scales_dR = [ scales_list_350[0] ]*6
    nfiles_dR = [nfiles_chains_chi2[0]] *6
    histos_dR = ["b1_dR","b2_dR","q1_dR","q2_dR","lep_dR","neu_dR"]
    legend_dR = ["#scale[0.8]{b_{1}}","#scale[0.8]{b_{2}}","#scale[0.8]{q_{1}}","#scale[0.8]{q_{2}}","#scale[0.8]{lepton}","#scale[0.8]{#nu_{l}}"]
    legend_dR.reverse()
    histos_dR.reverse()
    
    # IMPORTANT NOTE: PLACED A QUICK HACK INTO LAYERED HISTOS for dR STACKPLOTS! where yMax is rescaled feel free to remove
    
    save_thstack_to_image(file_dR,nfiles_dR, scales_dR, histos_dR, legend_dR, tr, PLOTS_dir+output_dir+"dR"+"."+extension, "#Delta R     (rad)", ylabel, fillcolours_combinations, fillstyles_combinations, ratiomode=frac, ref_ratio_index=0, ylabel_ratio=frac_text, legend_title="", latex_text = flavour_text, latex_corner=tl, log="", stack_option = "nostack")
    
    
    return 0

combined_dir = "combined/"
combined_dir_cuts = "combined_cuts/"
#run_chi2graphs_stack(outnames_chi2, combined_dir)
#run_chi2graphs_stack(outnames_chi2cuts, combined_dir_cuts)

outnames_samples = []
#short_list, histo_list, report_list = generate_histo_properties("",cuts)


def run_chainselection_histolist(histolist, chain_list, sample_list, skip = False):
    for i, sample in enumerate(sample_list):
        if "tt" in sample:
            outnames_samples.append(PLOTS_dir+sample+"selection_histograms_emu.root")
            histo_list_setdefaultcuts(histolist, "decay_channel == 1 && abs(mc_lepton1_pdgid) < 14")
            histo_list_setfilename(histolist, PLOTS_dir+sample+"selection_histograms_emu.root")
            save_histo_list(histolist,chain_list[i])
            histo_list_setdefaultcuts(histolist, "decay_channel == 1 && abs(mc_lepton1_pdgid) == 15")
            outnames_samples.append(PLOTS_dir+sample+"selection_histograms_tau.root")
            histo_list_setfilename(histolist, PLOTS_dir+sample+"selection_histograms_tau.root")
            save_histo_list(histolist,chain_list[i])
            histo_list_setdefaultcuts(histolist, "decay_channel == 1")
            outnames_samples.append(PLOTS_dir+sample+"selection_histograms_all.root")
            histo_list_setfilename(histolist, PLOTS_dir+sample+"selection_histograms_all.root")
            save_histo_list(histolist,chain_list[i])
        else:
            outnames_samples.append(PLOTS_dir+sample+"selection_histograms.root")
            histo_list_setfilename(histolist, PLOTS_dir+sample+"selection_histograms.root")
            save_histo_list(histolist,chain_list[i])
    return 0

# Deprecated
#skip_samples = True
#run_chainselection_histolist(report_list, chains_chi2, sample_chi2, skip_samples)


def run_selection_stack(outnames):
    # First generate the lists necessary to produce the stack plots: Decide if tau separate or not
    tr = "topright"
    tl = "topleft"
    legend_list = ["t#bar{t} semi-lepton", "t#bar{t} di-lepton", "t#bar{t} hadronic", "HZ", "ZZ", "WW"]
    # Want to remove: 
    outnames_no_tau_emu = [x for x in outnames if not ("tau" in x or "emu" in x)]
    outnames_no_all = [x for x in outnames if not ("all" in x)]
    print outnames_no_all, outnames_no_tau_emu
    
    return 0    
# Deprecated        
#run_selection_stack(outnames_samples)


list_ROC = ["chi2_histo1","chi2_histo2", "chi2_whad_h","chi2_thad_h","chi2_wlep_h","chi2_tlep_h", "chi2_alt_histo1","chi2_alt_histo2","chi2_alt2_histo1","chi2_alt2_histo2","chi2_nicolo1","chi2_nicolo2","lep1_e_full","total_rec_mass_full","four_jets_mass_full"]
output_ROC_histos = PLOTS_dir+"ROC_histos.root"
def ROC_curves_histos():
    index_signal = 0
    # TODO: add Nicolo & chi2 3 termen 
    print outnames_chi2cuts,nfiles_chains_chi2,scales_list_350 ,list_ROC,index_signal,output_ROC_histos
    prepare_ROC_histos(outnames_chi2_ROC,nfiles_chains_chi2,scales_list_350 ,list_ROC,index_signal,output_ROC_histos)
    return 0

# DONE for thesis
ROC_curves_histos()

# Now create the actual graphs, not just the histograms!
list_ROC_signal = [x+"_signal" for x in list_ROC]
list_ROC_background= [x+"_background" for x in list_ROC]

list_ROC_short = ["chi2_alt_histo1","chi2_histo1","chi2_alt2_histo1"]
list_ROC_other = ["lep1_e_full","total_rec_mass_full","four_jets_mass_full"]
list_ROC_chi2_comps = ["chi2_whad_h","chi2_thad_h","chi2_wlep_h","chi2_tlep_h"]

legend_ROC_short = ["#chi^{2}_{3}","#chi^{2}_{4}","#chi^{2}_{5}"]
legend_ROC_other = ["E_{lep}","m_{total}^{reco}","m_{4j}"]
legend_ROC_chi2_comps = ["#chi^{2}_{W_{had}}","#chi^{2}_{t_{had}}","#chi^{2}_{W_{lep}}","#chi^{2}_{t_{lep}}"]

list_ROC_short_signal = [x+"_signal" for x in list_ROC_short]
list_ROC_short_background= [x+"_background" for x in list_ROC_short]
list_ROC_other_signal = [x+"_signal" for x in list_ROC_other]
list_ROC_other_background= [x+"_background" for x in list_ROC_other]
list_ROC_chi2_comps_signal = [x+"_signal" for x in list_ROC_chi2_comps]
list_ROC_chi2_comps_background= [x+"_background" for x in list_ROC_chi2_comps]

output_ROC_short_graphs = PLOTS_dir+"ROC/"+"curves_short.pdf"
output_ROC_other_graphs = PLOTS_dir+"ROC/"+"curves_other.pdf"
output_ROC_chi2_comps_graphs = PLOTS_dir+"ROC/"+"curves_chi2_comps.pdf"

def ROC_curves_graphs(eff_bg):
    output_ROC_graphs = PLOTS_dir+"ROC/"+"curves_all.pdf"
    
    legend_ROC = list_ROC
    legend_spot = "bottomright"
    xlabel_ROC = "Background efficiency"
    ylabel_ROC = "Signal efficiency"
    xlim_ROC = [0,1.1]
    ylim_ROC = xlim_ROC
    
    colours_ROC = [rt.kBlue,rt.kGreen+1, rt.kRed, rt.kMagenta]#, rt.kViolet-6]
    
    
    
    #prepare_ROC_graphs(output_ROC_histos,list_ROC_signal,list_ROC_background,eff_bg,output_ROC_graphs, legend_ROC,legend_spot, xlabel_ROC,ylabel_ROC,fillcolours_original,xlim_ROC,ylim_ROC, graph_options = "la",larger_than = False)
    
    prepare_ROC_graphs(output_ROC_histos,list_ROC_short_signal,list_ROC_short_background,eff_bg,output_ROC_short_graphs, legend_ROC_short,"topright", xlabel_ROC,ylabel_ROC,colours_ROC,xlim_ROC,ylim_ROC, graph_options = "la",larger_than = False)
    
    #prepare_ROC_graphs(output_ROC_histos,list_ROC_other_signal,list_ROC_other_background,eff_bg,output_ROC_other_graphs, legend_ROC_other,legend_spot, xlabel_ROC,ylabel_ROC,colours_ROC,xlim_ROC,ylim_ROC, graph_options = "la",larger_than = True)
    
    #prepare_ROC_graphs(output_ROC_histos,list_ROC_chi2_comps_signal,list_ROC_chi2_comps_background,eff_bg,output_ROC_chi2_comps_graphs, legend_ROC_chi2_comps,"bottomright_big", xlabel_ROC,ylabel_ROC,colours_ROC,xlim_ROC,ylim_ROC, graph_options = "la", larger_than = False)
    
    return 0

# DONE for thesis
ROC_curves_graphs(0.1)


# name of pythia cross sections graph
# DONE for thesis
#make_graphs_pythia(PLOTS_dir+"Pythia_cross/cross.pdf")


# Let's produce some cut flow tables now:

def full_cutflow_tables():
    header_list = ["cuts","\multicolumn{3}{c|}{$\mathrm{t\\bar{t}}$ semi-lep}","\multicolumn{3}{c|}{$\mathrm{t\\bar{t}}$ di-lep}","\multicolumn{3}{c|}{$\mathrm{t\\bar{t}}$ had}","\multicolumn{3}{c|}{HZ}","\multicolumn{3}{c|}{ZZ}","\multicolumn{3}{c|}{WW}"]
    histo_name = "cut_flow_histo"
    output_file = PLOTS_dir+"cutflow/yields.txt"
    #print outnames_chi2cuts,nfiles_chains_chi2,histo_name,scales_list_350,output_file,header_list
    full_cutflow_table_to_file(outnames_chi2cuts,nfiles_chains_chi2,histo_name,scales_list_350,output_file,header_list)
    
    header_list_eff = ["cuts","$\mathrm{t\\bar{t}}$ semi-lep", "$\mathrm{t\\bar{t}}$ di-lep", "$\mathrm{t\\bar{t}}$ had", "HZ", "ZZ", "WW"]
    output_file_eff = PLOTS_dir+"cutflow/eff.txt"
    
    full_cutflow_table_to_file_eff(outnames_chi2cuts,nfiles_chains_chi2,histo_name,scales_list_350,output_file_eff,header_list_eff)
    
    
    return 0

#full_cutflow_tables()





def good_combo_efficiency():
    # total chi^2_3 distribution
    # NOT CORRECT recalculate for good diagrams!!!!!!
    GC_events = 2585
    BC_events = 10824
    TOTAL_events = GC_events + BC_events
    
    eff = efficiency_uncertainty(GC_events, TOTAL_events) 
    print eff
    
    # (0,0.45) bincontent (can be done by quickly rebinning with an array!)
    GC_aftercut= 927
    BC_aftercut = 3755
    TOTAL_aftercut = GC_aftercut + BC_aftercut
    eff_after = efficiency_uncertainty(GC_aftercut, TOTAL_aftercut)
    print eff_after
    
    # tau:
    tau = 557
    eff_tau = efficiency_uncertainty(tau, TOTAL_aftercut)
    print eff_tau
    return 0

#good_combo_efficiency()

#chi2_cut_4 = 1.35
#chi2_cut_3 = 0.45
#chi2_cut_5 = 1.5
#chi2_nicolo_cut = 6.3

chains_fullscan = [None]*len(sample_subdirs)
nfiles_fullscan = [None]*len(sample_subdirs)
outnames_fullscan = [None]*50

# IMPORTANT: WITHOUT SKIPPING? THIS WILL BE KILLED ON mshort server iihe(20min)! takes a while to run through the scan (roughly 30-35min)! 
# in principle this is done once and the histograms will be fine. The get_chains is necessary to know how many files you have, which you use to scale after.
def run_loop_fullscan(skip_fullscan):
    for i,sample in enumerate(sample_subdirs):
        is_full_tt = ('tt' in sample)
        chains_fullscan[i], nfiles_fullscan[i] = get_chainlist(sample,"tree_",40,45)
        outnames_fullscan[i] = PLOTS_dir+sample+"chi2_algorithm_cuts.root"
        if not os.path.exists(PLOTS_dir+sample):
            os.makedirs(PLOTS_dir+sample)
        if not skip_fullscan:
            chi2_algorithm_withcuts(chains_fullscan[i],outnames_fullscan[i], param_list_self, is_full_tt, chi2_cut= chi2_cut_4,chi2_alt_cut=chi2_cut_3,chi2_alt2_cut=chi2_cut_5,chi2_nicolo_cut=chi2_nicolo_cut)
    return 0

skip_fullscan = True
#run_loop_fullscan(skip_fullscan)

# sample_subdirs:
#['m1718_s340/tt/', 'm1726_s340/tt/', 'm1730_s340/tt/', 'm1730_s340/dilep/', 'm1730_s340/had/', 'm1730_s340/hz/', 'm1730_s340/zz/', 'm1730_s340/ww/', 'm1734_s340/tt/', 'm1742_s340/tt/', 'm1718_s342/tt/', 'm1726_s342/tt/', 'm1730_s342/tt/', 'm1730_s342/dilep/', 'm1730_s342/had/', 'm1730_s342/hz/', 'm1730_s342/zz/', 'm1730_s342/ww/', 'm1734_s342/tt/', 'm1742_s342/tt/', 'm1718_s344/tt/', 'm1726_s344/tt/', 'm1730_s344/tt/', 'm1730_s344/dilep/', 'm1730_s344/had/', 'm1730_s344/hz/', 'm1730_s344/zz/', 'm1730_s344/ww/', 'm1734_s344/tt/', 'm1742_s344/tt/', 'm1718_s346/tt/', 'm1726_s346/tt/', 'm1730_s346/tt/', 'm1730_s346/dilep/', 'm1730_s346/had/', 'm1730_s346/hz/', 'm1730_s346/zz/', 'm1730_s346/ww/', 'm1734_s346/tt/', 'm1742_s346/tt/', 'm1718_s350/tt/', 'm1726_s350/tt/', 'm1730_s350/tt/', 'm1730_s350/dilep/', 'm1730_s350/had/', 'm1730_s350/hz/', 'm1730_s350/zz/', 'm1730_s350/ww/', 'm1734_s350/tt/', 'm1742_s350/tt/']

# Use smart indexing to recover variables
index_scan_mtop = [40,41,42,48,49]
# Run for sqrt(s) = 350, change scale value if you change this
scan_mtop_dirs = [x for ix,x in enumerate(outnames_fullscan) if ix in index_scan_mtop]
scan_mtop_nfiles = [x for ix,x in enumerate(nfiles_fullscan) if ix in index_scan_mtop]
scan_mtop_scales = [scale_matrix_list[0][4][0],scale_matrix_list[1][4][0],scale_matrix_list[2][4][0],scale_matrix_list[3][4][0],scale_matrix_list[4][4][0]]
scan_mtop_legend = ["m_{t} = 171.8 GeV","m_{t} = 172.6 GeV","m_{t} = 173.0 GeV","m_{t} = 173.4 GeV","m_{t} = 174.2 GeV"]

#print scan_mtop_dirs,scan_mtop_nfiles

index_scan_energy = [2,12,22,32,42]
# Run for mtop = 173
scan_energy_dirs = [x for ix,x in enumerate(outnames_fullscan) if ix in index_scan_energy]
scan_energy_dirs.reverse()
scan_energy_nfiles = [x for ix,x in enumerate(nfiles_fullscan) if ix in index_scan_energy]
scan_energy_nfiles.reverse()

mtops = [171.8,172.6,173,173.4,174.2]
for i,mat in enumerate(scale_matrix_list):
    print "mt = {}".format(mtops[i])+"="*30
    for row in mat:
        print row


#scan_energy_scales = [7277,20886,47857,46326,48352]
scan_energy_scales = [scale_matrix_list[2][0][0],scale_matrix_list[2][1][0],scale_matrix_list[2][2][0],scale_matrix_list[2][3][0],scale_matrix_list[2][4][0]]
print scan_energy_scales
scan_energy_scales.reverse()
scan_energy_legend = ["#sqrt{s} = 340 GeV","#sqrt{s} = 342 GeV","#sqrt{s} = 344 GeV","#sqrt{s} = 346 GeV","#sqrt{s} = 350 GeV"]
scan_energy_legend.reverse()

#print scan_energy_dirs, scan_energy_nfiles

fillcolours_scan =[rt.kCyan+1,rt.kGreen+1,rt.kBlue, rt.kOrange+7,rt.kRed]

#fillstyles_scan = [3144,3244,3010, 3017,3004]
#fillstyles_scan.reverse()

fillstyles_scan = [0]*5


def run_fullscan_stacks():
    
    #save_thstack_to_image(stacks_outnames_chi2,nfiles_stacks,scales_350_stacks ,chi2_histo1_taus, legends_tau, tr,  PLOTS_dir+output_dir_tau+"chi2_histo1"+"."+extension,  "#chi^{2}_3", ylabel, fillcolours_combinations, fillstyles_combinations,ratiomode = frac, ref_ratio_index = len(legend_list)-1, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text, latex_corner=tl, log="y")
    
    tr = "topright"
    tl = "topleft"
    cr = "centre"
    # Style predefined objects:
    ylabel = "Events"
    
    n_rebin = 2
    
    flavour_text_mtop = "FCC-ee ILD L_{int} = 0.2 ab^{-1} #sqrt{s} = 350 GeV"
    flavour_text_energy = "FCC-ee ILD L_{int} = 0.2 ab^{-1} m_{t} = 173.0 GeV"
    
    output_dir_scan = PLOTS_dir+"scans/"
    legend_title = ""
    print scan_mtop_dirs,scan_mtop_nfiles,scan_mtop_scales ,"chi2_alt_histo2", scan_mtop_legend, tr, output_dir_scan+"mtop_chi2_alt_histo2"+"."+extension,  "#chi^{2}_3", ylabel, fillcolours_scan, fillstyles_scan
    scan_stack_option = "nostack"
    
    frac_text = "N_{X} - N_{173} / N_{173}"
    
    # SCAN MTOP
    save_thstack_to_image(scan_mtop_dirs,scan_mtop_nfiles,scan_mtop_scales ,"chi2_alt_histo2", scan_mtop_legend, tr, output_dir_scan+"mtop_chi2_alt_histo2"+"."+extension,  "#chi^{2}_{3}", ylabel, fillcolours_scan, fillstyles_scan,ratiomode = frac, ref_ratio_index =2, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text_mtop, latex_corner=tl, log="y",stack_option = scan_stack_option, rebin = n_rebin)
    save_thstack_to_image(scan_mtop_dirs,scan_mtop_nfiles,scan_mtop_scales ,"tmass_had1", scan_mtop_legend, tr, output_dir_scan+"mtop_tmass_had1"+"."+extension,  "m_{t}^{had}     (GeV)", ylabel, fillcolours_scan, fillstyles_scan,ratiomode = frac, ref_ratio_index =2, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text_mtop, latex_corner=tl, log="y",stack_option = scan_stack_option, rebin = n_rebin)
    save_thstack_to_image(scan_mtop_dirs,scan_mtop_nfiles,scan_mtop_scales ,"tmass_had2", scan_mtop_legend, tr, output_dir_scan+"mtop_tmass_had2"+"."+extension,  "m_{t}^{had}     (GeV)", ylabel, fillcolours_scan, fillstyles_scan,ratiomode = frac, ref_ratio_index =2, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text_mtop, latex_corner=tl, log="y",stack_option = scan_stack_option, rebin = n_rebin)
    save_thstack_to_image(scan_mtop_dirs,scan_mtop_nfiles,scan_mtop_scales ,"tmass_lep", scan_mtop_legend, tr, output_dir_scan+"mtop_tmass_lep"+"."+extension,  "m_{t}^{lep}     (GeV)", ylabel, fillcolours_scan, fillstyles_scan,ratiomode = frac, ref_ratio_index =2, ylabel_ratio = frac_text, legend_title= legend_title, latex_text = flavour_text_mtop, latex_corner=tl, log="y",stack_option = scan_stack_option, rebin = n_rebin)
    
    # SCAN SQRT(S)
    
    div_text = "N_{X} / N_{350}"
    
    
    save_thstack_to_image(scan_energy_dirs,scan_energy_nfiles,scan_energy_scales ,"chi2_alt_histo2", scan_energy_legend, tr, output_dir_scan+"energy_chi2_alt_histo2"+"."+extension,  "#chi^{2}_{3}", ylabel, fillcolours_scan, fillstyles_scan,ratiomode = div, ref_ratio_index =0, ylabel_ratio = div_text, legend_title= legend_title, latex_text = flavour_text_energy, latex_corner=tl, log="y",stack_option = scan_stack_option, rebin = n_rebin)
    save_thstack_to_image(scan_energy_dirs,scan_energy_nfiles,scan_energy_scales ,"tmass_had1", scan_energy_legend, tr, output_dir_scan+"energy_tmass_had1"+"."+extension,  "m_{t}^{had}     (GeV)", ylabel, fillcolours_scan, fillstyles_scan,ratiomode = div, ref_ratio_index =0, ylabel_ratio = div_text, legend_title= legend_title, latex_text = flavour_text_energy, latex_corner=tl, log="y",stack_option = scan_stack_option, rebin = n_rebin)
    save_thstack_to_image(scan_energy_dirs,scan_energy_nfiles,scan_energy_scales ,"tmass_had2", scan_energy_legend, tr, output_dir_scan+"energy_tmass_had2"+"."+extension,  "m_{t}^{had}     (GeV)", ylabel, fillcolours_scan, fillstyles_scan,ratiomode = div, ref_ratio_index =0, ylabel_ratio = div_text, legend_title= legend_title, latex_text = flavour_text_energy, latex_corner=tl, log="y",stack_option = scan_stack_option, rebin = n_rebin)
    save_thstack_to_image(scan_energy_dirs,scan_energy_nfiles,scan_energy_scales ,"tmass_lep", scan_energy_legend, tr, output_dir_scan+"energy_tmass_lep"+"."+extension,  "m_{t}^{lep}     (GeV)", ylabel, fillcolours_scan, fillstyles_scan,ratiomode = div, ref_ratio_index =0, ylabel_ratio = div_text, legend_title= legend_title, latex_text = flavour_text_energy, latex_corner=tl, log="y",stack_option = scan_stack_option, rebin = n_rebin)
    
    
    return 0
    
#run_fullscan_stacks()


# sample_subdirs:
#['m1718_s340/tt/', 'm1726_s340/tt/', 'm1730_s340/tt/', 'm1730_s340/dilep/', 'm1730_s340/had/', 'm1730_s340/hz/', 'm1730_s340/zz/', 'm1730_s340/ww/', 'm1734_s340/tt/', 'm1742_s340/tt/', 'm1718_s342/tt/', 'm1726_s342/tt/', 'm1730_s342/tt/', 'm1730_s342/dilep/', 'm1730_s342/had/', 'm1730_s342/hz/', 'm1730_s342/zz/', 'm1730_s342/ww/', 'm1734_s342/tt/', 'm1742_s342/tt/', 'm1718_s344/tt/', 'm1726_s344/tt/', 'm1730_s344/tt/', 'm1730_s344/dilep/', 'm1730_s344/had/', 'm1730_s344/hz/', 'm1730_s344/zz/', 'm1730_s344/ww/', 'm1734_s344/tt/', 'm1742_s344/tt/', 'm1718_s346/tt/', 'm1726_s346/tt/', 'm1730_s346/tt/', 'm1730_s346/dilep/', 'm1730_s346/had/', 'm1730_s346/hz/', 'm1730_s346/zz/', 'm1730_s346/ww/', 'm1734_s346/tt/', 'm1742_s346/tt/', 'm1718_s350/tt/', 'm1726_s350/tt/', 'm1730_s350/tt/', 'm1730_s350/dilep/', 'm1730_s350/had/', 'm1730_s350/hz/', 'm1730_s350/zz/', 'm1730_s350/ww/', 'm1734_s350/tt/', 'm1742_s350/tt/']

#print outnames_fullscan, nfiles_fullscan


def sqrts_mtop_tables():
    
    # Each entry is 1 file for a number in the table, each row = fixed sqrt(s), each column fixed mtop
    
    # Should use the amount of files from get_chain, but since I have produced reserves I always have my 40 files I want
    semilep_matrix_nfiles = [[40]*5]*5
    semilep_matrix_files = [[PLOTS_dir+"m"+m+"_s"+s+"/tt/chi2_algorithm_cuts.root" for m in mtop] for s in sqrts]
    #[[ "m"+mtop[i]+"_s"+sqrts[j]+"/" for i in range(len(mtop)) ] for j in range(len(sqrts)) ]
    histo_name = "cut_flow_histo"
    
    #semilep_matrix_scales = [[scales_list_340[0]]*5,[scales_list_342[0]]*5,[scales_list_344[0]]*5,[scales_list_346[0]]*5,[scales_list_350[0]]*5]
    #[scale_matrix_list[mtop index][sqrts index][sample index]]
    # Slicing did not seem to work :/
    semilep_matrix_scales = [[scale_matrix_list[0][0][0],scale_matrix_list[1][0][0],scale_matrix_list[2][0][0],scale_matrix_list[3][0][0],scale_matrix_list[4][0][0]], # 340
                                        [scale_matrix_list[0][1][0],scale_matrix_list[1][1][0],scale_matrix_list[2][1][0],scale_matrix_list[3][1][0],scale_matrix_list[4][1][0]], # 342
                                        [scale_matrix_list[0][2][0],scale_matrix_list[1][2][0],scale_matrix_list[2][2][0],scale_matrix_list[3][2][0],scale_matrix_list[4][2][0]], # 344
                                        [scale_matrix_list[0][3][0],scale_matrix_list[1][3][0],scale_matrix_list[2][3][0],scale_matrix_list[3][3][0],scale_matrix_list[4][3][0]], # 346
                                        [scale_matrix_list[0][4][0],scale_matrix_list[1][4][0],scale_matrix_list[2][4][0],scale_matrix_list[3][4][0],scale_matrix_list[4][4][0]]] # 350
#    print semilep_matrix_scales
#    return 0
    # Each entry is a list of files to sum up the backgrounds 
    background_list_files = [[PLOTS_dir+"m1730"+"_s"+s+"/"+c+"/chi2_algorithm_cuts.root" for c in ["dilep", "had", "hz", "zz", "ww"] ] for s in sqrts]
    background_list_nfiles = semilep_matrix_nfiles[:]
    background_list_scales = [scales[1:] for scales in scales_matrix]
    
    headers_table = ["\backslashbox{$\sqrt{s}$}{$m_{\mathrm{t}}$}", "171.8","172.6","173.0","173.4","174.2"]
    output_table = PLOTS_dir+"cutflow/mtop_sqrts_tab.txt"
    
    # Works as expected
    #print semilep_matrix_files
    #print background_list_files
    #print semilep_matrix_scales
    #print background_list_scales
    
    mtop_sqrts_table(semilep_matrix_files, semilep_matrix_nfiles, semilep_matrix_scales, background_list_files, background_list_nfiles, background_list_scales,histo_name, output_table, headers_table)
    
    
    
    
    return 0
    
#sqrts_mtop_tables()







