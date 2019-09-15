import os, sys
import ROOT as rt
from itertools import permutations
#import math
from histo_properties import *

##########################################################

################## LOOP FUNCTIONS ############################

def simple_loop(chain):
    N = chain.GetEntries()
    print "This chain contains {} events".format(N)
    i = 0
    for ev in chain:
        i += 1
        # ev.jet1_e == python FLOAT!!!!!
        print "{}, object class:{}".format(i,ev)
        if i > 0:
            break
    
    return 0


def testangle():
    v1 = rt.TLorentzVector()
    v1.SetPxPyPzE(1,0,0,1)
    e1 = v1.E()
    v2 = rt.TLorentzVector()
    v2.SetPxPyPzE(0,1,0,1)
    print e1
    return v1.Angle(v2.Vect())

def mcmatch_histo(chain, output_file):
    # Handle root file
    root_outfile = rt.TFile(output_file,"RECREATE")
    root_outfile.cd()
    pi_ = 3.14159
    n_events = chain.GetEntries()
    n_bins_angles = 20
    n_bins_dE = 30
    min_angle_b1 = rt.TH1D("min_angle_b1","min_angle_b1", n_bins_angles, 0, pi_)
    min_ediff_b1 = rt.TH1D("min_ediff_b1","E_{b1} - E_{j}",n_bins_dE, -50, 50)
    min_angle_b2 = rt.TH1D("min_angle_b2","min_angle_b2", n_bins_angles, 0, pi_)
    min_ediff_b2 = rt.TH1D("min_ediff_b2","E_{b2} - E_{j}",70, -150, 150)
    b1 = rt.TLorentzVector()
    b2 = rt.TLorentzVector()
    j1 = rt.TLorentzVector()
    j2 = rt.TLorentzVector()
    j3 = rt.TLorentzVector()
    j4 = rt.TLorentzVector()
    # warn the user if the same jet is chosen as the closest angle 
    warning_histo = rt.TH1D("warning_histo", "warning_histo", 3, 0, 3)
    # Warning bin 1:
    warning_samejetangles = []
    # Warning bin 2:
    warning_diffjetanglevsE_1 = []
    # Warning bin 3:
    warning_diffjetanglevsE_2 = []
    
    for iev,ev in enumerate(chain):
        # Init P4 of particles
        b1.SetPxPyPzE(ev.mc_bquark1_px,ev.mc_bquark1_py,ev.mc_bquark1_pz,ev.mc_bquark1_e)
        b2.SetPxPyPzE(ev.mc_bquark2_px,ev.mc_bquark2_py,ev.mc_bquark2_pz,ev.mc_bquark2_e)
        j1.SetPxPyPzE(ev.jet1_px,ev.jet1_py,ev.jet1_pz,ev.jet1_e)
        j2.SetPxPyPzE(ev.jet2_px,ev.jet2_py,ev.jet2_pz,ev.jet2_e)
        j3.SetPxPyPzE(ev.jet3_px,ev.jet3_py,ev.jet3_pz,ev.jet3_e)
        j4.SetPxPyPzE(ev.jet4_px,ev.jet4_py,ev.jet4_pz,ev.jet4_e)
        jets = [j1, j2, j3, j4]
        b1_angle = 10
        b1_angle_idx = 0
        b2_angle = 10
        b2_angle_idx = 0
        b1_ediff = 350
        b1_ediff_idx = 0
        b2_ediff = 350
        b2_ediff_idx = 0
        # Loop over jets 
        for ijet,jet in enumerate(jets):
            angle1 = b1.Angle(jet.Vect())
            angle2 = b2.Angle(jet.Vect())
            ediff1 = b1.E() - jet.E()
            ediff2 = b2.E() - jet.E()
            # Testing: 
            #ediff1 = b1.E()
            #ediff2 = b2.E()
            #print ediff1, ediff2
            # Grab and replace minimum if smaller
            if angle1 < b1_angle:
                b1_angle = angle1
                b1_angle_idx = ijet
            if angle2 < b2_angle:
                b2_angle = angle2
                b2_angle_idx = ijet
            if abs(ediff1) < abs(b1_ediff):
                b1_ediff = ediff1
                b1_ediff_idx = ijet
            if abs(ediff2) < abs(b2_ediff):
                b2_ediff = ediff2
                b2_ediff_idx = ijet
        # end jet loop
        # Now fill the histograms and check for warnings
        if b1_angle_idx == b2_angle_idx:
            warning_samejetangles.append(iev)
            warning_histo.Fill(0.5)
        if b1_ediff_idx != b1_angle_idx:
            warning_diffjetanglevsE_1.append(iev)
            warning_histo.Fill(1.5)
        if b2_ediff_idx != b2_angle_idx:
            warning_diffjetanglevsE_2.append(iev)
            warning_histo.Fill(2.5)
        min_angle_b1.Fill(b1_angle)
        min_ediff_b1.Fill(b1_ediff)
        min_angle_b2.Fill(b2_angle)
        min_ediff_b2.Fill(b2_ediff)
    # end event loop
    n_warning_samejetangles = len(warning_samejetangles)
    n_warning_diffjetanglevsE_1 = len(warning_diffjetanglevsE_1)
    n_warning_diffjetanglevsE_2 = len(warning_diffjetanglevsE_2)
    print "Same jet with closest angle for b quarks: {}/{}, fraction = {}".format(n_warning_samejetangles,n_events, float(n_warning_samejetangles)/n_events)
    print "Different jet for angle vs dE (b quark 1): {}/{}, fraction = {}".format(n_warning_diffjetanglevsE_1,n_events,float(n_warning_diffjetanglevsE_1)/n_events)
    print "Different jet for angle vs dE (b quark 2): {}/{}, fraction = {}".format(n_warning_diffjetanglevsE_2,n_events,float(n_warning_diffjetanglevsE_2)/n_events)
    # Save and Close the root file
    root_outfile.Write()
    root_outfile.Close()
    return 0


def mcmatch_histo_wtop(chain, output_file, filename = ""):
    
    # Helper functions
    def get_params_fit(fitter, distribution_name):
        chi2 = fitter.GetChisquare()
        ndof = fitter.GetNDF()
        mean = fitter.GetParameter(1)
        width = fitter.GetParameter(2)
        return [distribution_name ,mean, width, chi2, ndof]
        
    def save_params_to_txt(param_list, filename):
        file = open(filename, "wt")
        file.write("dist;\tmean;\twidth;\tchi2/ndof\n")
        for list in param_list:
            file.write("{:20};\t{:.5};\t{:.5};\t{:.5}\n".format(list[0],list[1],list[2],list[3]/list[4]))
        file.close()
        return 0
    
    
    
    # Handle root file
    root_outfile = rt.TFile(output_file,"RECREATE")
    root_outfile.cd()
    pi_ = 3.14159
    n_events = chain.GetEntries()
    n_bins_topmass = 100
    n_bins_wmass = 100
    n_bins_angles1 = 15
    n_bins_angles2 = 40
    wmass_had1 = rt.TH1D("wmass_had1", "wmass_had1", n_bins_wmass, 30, 150) 
    wmass_had2 = rt.TH1D("wmass_had2", "wmass_had2", n_bins_wmass, 70, 90)
    wmass_lep = rt.TH1D("wmass_lep","wmass_lep", n_bins_wmass, 30, 150)
    tmass_had1 = rt.TH1D("tmass_had1", "tmass_had1", n_bins_topmass, 80, 240)
    tmass_had2 = rt.TH1D("tmass_had2", "tmass_had2", n_bins_topmass, 140, 190)
    tmass_lep = rt.TH1D("tmass_lep", "tmass_lep", n_bins_topmass, 80, 240)
    lep_angle1 = rt.TH1D("lep_angle1", "lep_angle1", n_bins_angles1, 0, 2*pi_)
    lep_angle2 = rt.TH1D("lep_angle2", "lep_angle2", n_bins_angles2, 0, 0.5)
    neutrino_angle1 = rt.TH1D("neutrino_angle1", "neutrino_angle1", n_bins_angles1, 0, 2*pi_)
    neutrino_angle2 = rt.TH1D("neutrino_angle2", "neutrino_angle2", n_bins_angles2, 0, 0.5)
    b1_dR = rt.TH1D("b1_dR", "b1_dR", n_bins_angles2, 0, 0.5)
    b2_dR = rt.TH1D("b2_dR", "b2_dR", n_bins_angles2, 0, 0.5)
    q1_dR = rt.TH1D("q1_dR", "q1_dR", n_bins_angles2, 0, 0.5)
    q2_dR = rt.TH1D("q2_dR", "q2_dR", n_bins_angles2, 0, 0.5)
    # Save the b quarks & associated jets
    #b1 = rt.TLorentzVector()
    #b2 = rt.TLorentzVector()
    b1_jet = rt.TLorentzVector()
    b2_jet = rt.TLorentzVector()
    b1_id = 0
    b2_id = 0
    # Save the (quarks) & associated jets
    #q1 = rt.TLorentzVector()
    #q2 = rt.TLorentzVector()
    q1_jet = rt.TLorentzVector()
    q2_jet = rt.TLorentzVector()
    # Save the leptons and neutrino
    mc_lep = rt.TLorentzVector()
    lep = rt.TLorentzVector()
    lep_id = 0
    mc_neutrino = rt.TLorentzVector()
    missing_e = rt.TLorentzVector()
    # Save some 4vectors for the W and t particles
    thad = rt.TLorentzVector()
    tlep = rt.TLorentzVector()
    whad = rt.TLorentzVector()
    wlep =  rt.TLorentzVector()
    wlep_charge = 0
    whad_charge = 0
    correct_combination = True
    dR = 0.1
    for iev,ev in enumerate(chain):
        
        # Init the p4 for the leptons and neutrinos in all cases
        mc_lep.SetPxPyPzE(ev.mc_lepton1_px,ev.mc_lepton1_py,ev.mc_lepton1_pz,ev.mc_lepton1_e)
        lep.SetPxPyPzE(ev.lep1_px,ev.lep1_py,ev.lep1_pz,ev.lep1_e)
        lep_id = ev.lep1_pdgid
        mc_neutrino.SetPxPyPzE(ev.mc_neutrino1_px,ev.mc_neutrino1_py,ev.mc_neutrino1_pz,ev.mc_neutrino1_e)
        missing_e.SetPxPyPzE(ev.missing_rec_px,ev.missing_rec_py,ev.missing_rec_pz,ev.missing_rec_e)
        lep_angle = lep.Angle(mc_lep.Vect())
        neut_angle = missing_e.Angle(mc_neutrino.Vect())
        # Correct combination requirements:
        jets_dR = (ev.mc_quarkjet1_delta_alpha_wrt_nearest_jet < dR and ev.mc_quarkjet2_delta_alpha_wrt_nearest_jet < dR and ev.mc_bquark1_delta_alpha_wrt_nearest_jet < dR and ev.mc_bquark2_delta_alpha_wrt_nearest_jet < dR)
        leptons_ids = (abs(ev.mc_lepton1_pdgid) < 15 and abs(lep_id) < 15)
        jets_exist = (ev.mc_bquark1_nearest_jet_e > 0 and ev.mc_bquark2_nearest_jet_e > 0 and ev.mc_quarkjet1_nearest_jet_e > 0 and ev.mc_quarkjet2_nearest_jet_e > 0)
        leptons_dR = (lep_angle < dR and neut_angle < dR)
        start_condition = (jets_exist and ev.decay_channel == 1 and  leptons_ids and jets_dR and leptons_dR)
        if start_condition:
            correct_combination = True
            # Init P4 of particles
            #b1.SetPxPyPzE(ev.mc_bquark1_px,ev.mc_bquark1_py,ev.mc_bquark1_pz,ev.mc_bquark1_e)
            #b2.SetPxPyPzE(ev.mc_bquark2_px,ev.mc_bquark2_py,ev.mc_bquark2_pz,ev.mc_bquark2_e)
            b1_jet.SetPxPyPzE(ev.mc_bquark1_nearest_jet_px, ev.mc_bquark1_nearest_jet_py, ev.mc_bquark1_nearest_jet_pz, ev.mc_bquark1_nearest_jet_e)
            b2_jet.SetPxPyPzE(ev.mc_bquark2_nearest_jet_px, ev.mc_bquark2_nearest_jet_py, ev.mc_bquark2_nearest_jet_pz, ev.mc_bquark2_nearest_jet_e)
            b1_id = ev.mc_bquark1_pdgid
            b2_id = ev.mc_bquark2_pdgid
            q1_jet.SetPxPyPzE(ev.mc_quarkjet1_nearest_jet_px,ev.mc_quarkjet1_nearest_jet_py,ev.mc_quarkjet1_nearest_jet_pz,ev.mc_quarkjet1_nearest_jet_e)
            q2_jet.SetPxPyPzE(ev.mc_quarkjet2_nearest_jet_px,ev.mc_quarkjet2_nearest_jet_py,ev.mc_quarkjet1_nearest_jet_pz,ev.mc_quarkjet1_nearest_jet_e)
            # Fill in some other vectors
            whad = q1_jet+q2_jet
            wlep = lep+missing_e
            # Figure out how to associate the hadronic W and leptonic W to the correct b quarks:
            if lep_id > 0:
                wlep_charge = -1
            else:
                wlep_charge = 1
            whad_charge = -wlep_charge
            
            if whad_charge > 0:
                if b1_id > 0:
                    thad = whad + b1_jet
                    tlep = wlep + b2_jet
                elif b1_id < 0:
                    thad = whad + b2_jet
                    tlep = wlep + b1_jet
            elif whad_charge < 0:
                if b1_id > 0:
                    thad = whad + b2_jet
                    tlep = wlep + b1_jet
                elif b1_id < 0:
                    thad = whad + b1_jet
                    tlep = wlep +  b2_jet
            else:
                correct_combination = False
                print "could not identify the correct pairing for the top quarks"
                print "b1_id ={};\tb2_id = {};\twhad_charge = {};\twlep_charge = {}".format(b1_id, b2_id, whad_charge, wlep_charge)
            
            # Fill in the histograms
            if correct_combination:
                tmass_had1.Fill(thad.M())
                tmass_had2.Fill(thad.M())
                tmass_lep.Fill(tlep.M())
            wmass_had1.Fill(whad.M())
            wmass_had2.Fill(whad.M())
            wmass_lep.Fill(wlep.M())
        lep_angle1.Fill(lep_angle)
        lep_angle2.Fill(lep_angle)
        neutrino_angle1.Fill(neut_angle)
        neutrino_angle2.Fill(neut_angle)
        b1_dR.Fill(ev.mc_bquark1_delta_alpha_wrt_nearest_jet)
        b2_dR.Fill(ev.mc_bquark2_delta_alpha_wrt_nearest_jet)
        q1_dR.Fill(ev.mc_quarkjet1_delta_alpha_wrt_nearest_jet)
        q2_dR.Fill(ev.mc_quarkjet2_delta_alpha_wrt_nearest_jet)
    # end event loop
    
    # Save and Close the root file
    root_outfile.Write()
    root_outfile.Close()
    return 0



## CHI2 ALGO ###############

def chi2_algorithm(chain, output_file, param_list,is_full_tt = False):#, filename):
    print chain
    
    # Recover the param list into easier vars:
    mw_had,sw_had,mt_had,st_had,mw_lep,sw_lep,mt_lep,st_lep = param_list 
    
    # Disclaimer: 
    print "You are running this script for the chain with output: ",output_file
    print "The script chi2_algorithm is running assuming this file contains a full ee > ttbar collision: ",is_full_tt
    if is_full_tt:
        print "If this is not correct do not use the data acquired running this script! It will not correct for the decay channels as intended"
    else:
        print "This script is not correcting for decay channels, do not use this mode for files other than the tt!"

    # Handle root file
    root_outfile = rt.TFile(output_file,"RECREATE")
    root_outfile.cd()
    pi_ = 3.14159
    n_events = chain.GetEntries()
    n_bins_topmass = 100
    n_bins_wmass = 100
    #n_bins_angles1 = 15
    #n_bins_angles2 = 40
    # Init the histograms
    wmass_had1 = rt.TH1D("wmass_had1", "wmass_had1", n_bins_wmass, 40, 140) 
    wmass_had2 = rt.TH1D("wmass_had2", "wmass_had2", n_bins_wmass, 70, 90)
    wmass_lep = rt.TH1D("wmass_lep","wmass_lep", n_bins_wmass, 40, 140)
    tmass_had1 = rt.TH1D("tmass_had1", "tmass_had1", n_bins_topmass, 100, 220)
    tmass_had2 = rt.TH1D("tmass_had2", "tmass_had2", n_bins_topmass, 140, 190)
    tmass_lep = rt.TH1D("tmass_lep", "tmass_lep", n_bins_topmass, 100, 220)
    chi2_histo1 = rt.TH1D("chi2_histo1", "chi2_histo1", 100, 0, 150)
    chi2_histo2 = rt.TH1D("chi2_histo2", "chi2_histo2", 50, 0, 20)
    chi2_whad_h = rt.TH1D("chi2_whad_h", "chi2_whad", 100, 0, 150)
    chi2_thad_h = rt.TH1D("chi2_thad_h", "chi2_thad", 100, 0, 150)
    chi2_wlep_h = rt.TH1D("chi2_wlep_h", "chi2_wlep", 100, 0, 150)
    chi2_tlep_h = rt.TH1D("chi2_tlep_h", "chi2_tlep", 100, 0, 150)
    # Save all the jets for the chi2 algorithm as well as the missing_rec and lep1
    j1 = rt.TLorentzVector()
    j2 = rt.TLorentzVector()
    j3 = rt.TLorentzVector()
    j4 = rt.TLorentzVector()
    lep1 = rt.TLorentzVector()
    missing_rec = rt.TLorentzVector()
    # Save some 4vectors for the W and t particles to be used as temp in the 
    thad = rt.TLorentzVector()
    tlep = rt.TLorentzVector()
    whad = rt.TLorentzVector()
    wlep =  rt.TLorentzVector()
    # Save extra variables useful for the chi2 analysis:
    chi2 = 1000000
    # Replace the real vars with temp only if chi2 is lower!
    thad_save = rt.TLorentzVector()
    tlep_save = rt.TLorentzVector()
    whad_save = rt.TLorentzVector()
    wlep_save =  rt.TLorentzVector()
    # Save associated chi2 as well:
    chi2_whad_save = 0
    chi2_thad_save = 0
    chi2_wlep_save = 0
    chi2_tlep_save = 0
    
    for iev,ev in enumerate(chain):
        # reset value
        chi2 = 1000000
        chi2_condition = True
        if is_full_tt:
            # Keep only the semileptonic decays for the tt pythia files:
            chi2_condition = (ev.decay_channel == 1) and chi2_condition
        if chi2_condition:
            #combinations_found = True
            # Init P4 of particles
            j1.SetPxPyPzE(ev.jet1_px,ev.jet1_py,ev.jet1_pz,ev.jet1_e)
            j2.SetPxPyPzE(ev.jet2_px,ev.jet2_py,ev.jet2_pz,ev.jet2_e)
            j3.SetPxPyPzE(ev.jet3_px,ev.jet3_py,ev.jet3_pz,ev.jet3_e)
            j4.SetPxPyPzE(ev.jet4_px,ev.jet4_py,ev.jet4_pz,ev.jet4_e)
            lep1.SetPxPyPzE(ev.lep1_px, ev.lep1_py, ev.lep1_pz, ev.lep1_e)
            missing_rec.SetPxPyPzE(ev.missing_rec_px, ev.missing_rec_py, ev.missing_rec_pz, ev.missing_rec_e)
            # Create a list of the 4 jets 
            jet_list = [j1, j2, j3, j4]
            jet_perm = list(permutations(jet_list))
            
            ################DETERMINE CHI2 USING JET INFO ###################
            for jets in jet_perm:
                # Assume index 0 and 1 represent the W hadronic:
                whad = jets[0] + jets[1]
                # Assume the index 2 represents the b quark for top hadronic:
                thad = whad + jets [2]
                # Assume the index 3 represents the b quark for top leptonic:
                wlep = lep1 + missing_rec
                tlep = wlep + jets [3]
                
                # Now we have all 4vectors to perform the chi2
                chi2_whad =((whad.M()-float(mw_had))/float(sw_had))**2
                chi2_thad = ((thad.M()-float(mt_had))/float(st_had))**2
                chi2_wlep = ((wlep.M()-float(mw_lep))/float(sw_lep))**2
                chi2_tlep = ((tlep.M()-float(mt_lep))/float(st_lep))**2
                
                chi2_temp = chi2_whad + chi2_thad + chi2_wlep + chi2_tlep
                
                # If the chi2 is smaller than the value of the current chi2: overwrite the 4 vectors & chi2 values
                if chi2_temp < chi2:
                    chi2 = chi2_temp
                    whad_save = whad
                    thad_save = thad
                    wlep_save = wlep
                    tlep_save = tlep
                    chi2_whad_save = chi2_whad
                    chi2_thad_save = chi2_thad
                    chi2_wlep_save = chi2_wlep
                    chi2_tlep_save = chi2_tlep 
                
            ################END OF CHI2 ################################
            # Fill in the histograms
            tmass_had1.Fill(thad_save.M())
            tmass_had2.Fill(thad_save.M())
            tmass_lep.Fill(tlep_save.M())
            wmass_had1.Fill(whad_save.M())
            wmass_had2.Fill(whad_save.M())
            wmass_lep.Fill(wlep_save.M())
            chi2_histo1.Fill(chi2)
            chi2_histo2.Fill(chi2)
            chi2_whad_h.Fill(chi2_whad)
            chi2_thad_h.Fill(chi2_thad)
            chi2_wlep_h.Fill(chi2_wlep)
            chi2_tlep_h.Fill(chi2_tlep)
            
    # end event loop
    root_outfile.Write()
    root_outfile.Close()
    return 0



def chi2_algorithm_withcuts(chain, output_file, param_list,is_full_tt = False, chi2_cut = 100000, chi2_alt_cut = 100000, chi2_alt2_cut = 1000000, chi2_nicolo_cut = 100000):#, filename):
    print chain
    #print chi2_cut, chi2_alt_cut, chi2_alt2_cut, chi2_nicolo_cut
    
    # Recover the param list into easier vars:
    mw_had,sw_had,mt_had,st_had,mw_lep,sw_lep,mt_lep,st_lep = param_list 
    
    # Disclaimer: 
    print "You are running this script for the chain with output: ",output_file
    print "The script chi2_algorithm is running assuming this file contains a full ee > ttbar collision: ",is_full_tt
    if is_full_tt:
        print "If this is not correct do not use the data acquired running this script! It will not correct for the decay channels as intended"
    else:
        print "This script is not correcting for decay channels, do not use this mode for files other than the tt!"

    # Handle root file
    root_outfile = rt.TFile(output_file,"RECREATE")
    root_outfile.cd()
    pi_ = 3.14159
    n_events = chain.GetEntries()
    n_bins_topmass = 100
    n_bins_wmass = 100
    #n_bins_angles1 = 15
    #n_bins_angles2 = 40
    ########################################################
    #                                                               ALL                                                                  #
    ########################################################
    # Init the histograms with all combinations together
    wmass_had1 = rt.TH1D("wmass_had1", "wmass_had1", n_bins_wmass, 40, 140)
    wmass_had2 = rt.TH1D("wmass_had2", "wmass_had2", n_bins_wmass, 70, 90)
    wmass_lep = rt.TH1D("wmass_lep","wmass_lep", n_bins_wmass, 40, 140)
    tmass_had1 = rt.TH1D("tmass_had1", "tmass_had1", n_bins_topmass, 100, 220)
    tmass_had2 = rt.TH1D("tmass_had2", "tmass_had2", n_bins_topmass, 140, 190)
    
    tmass_lep = rt.TH1D("tmass_lep", "tmass_lep", n_bins_topmass, 100, 220)
    chi2_histo1 = rt.TH1D("chi2_histo1", "chi2_histo1", 100, 0, 150)
    chi2_histo2 = rt.TH1D("chi2_histo2", "chi2_histo2", 50, 0, 20)
    chi2_alt_histo1 = rt.TH1D("chi2_alt_histo1", "chi2_alt_histo1", 100, 0, 150)
    chi2_alt_histo2 = rt.TH1D("chi2_alt_histo2", "chi2_alt_histo2", 50, 0, 20)
    
    chi2_alt2_histo1 = rt.TH1D("chi2_alt2_histo1", "chi2_alt2_histo1", 100, 0, 150)
    chi2_alt2_histo2 = rt.TH1D("chi2_alt2_histo2", "chi2_alt2_histo2", 50, 0, 20)
    
    chi2_whad_h = rt.TH1D("chi2_whad_h", "chi2_whad", 100, 0, 150)
    chi2_thad_h = rt.TH1D("chi2_thad_h", "chi2_thad", 100, 0, 150)
    chi2_wlep_h = rt.TH1D("chi2_wlep_h", "chi2_wlep", 100, 0, 150)
    chi2_tlep_h = rt.TH1D("chi2_tlep_h", "chi2_tlep", 100, 0, 150)
    chi2_tt_h = rt.TH1D("chi2_tt_h", "chi2_tt", 100, 0, 150)
    #also init the other important histograms
    four_jets_mass_cuts            =  rt.TH1D("four_jets_mass_cuts","four_jets_mass_cuts", 100, 150, 270)
    
    four_jets_mass_full             =   rt.TH1D("four_jets_mass_full", "four_jets_mass_full",100, 0, 300)
    min_jets_mass_cuts            =  rt.TH1D(   "min_jets_mass_cuts", "min_jets_mass_cuts",100, 10, 100)
    min_jets_mass_full             =  rt.TH1D(   "min_jets_mass_full", "min_jets_mass_full",100, 0, 100)
    second_min_jets_mass_full  =  rt.TH1D(   "second_min_jets_mass_full","second_min_jets_mass_full", 100, 0, 110)
    second_min_jets_mass_cuts = rt.TH1D(   "second_min_jets_mass_cuts", "second_min_jets_mass_cuts",100, 20, 110)
    
    lep1_e_full                         =  rt.TH1D("lep1_e_full","lep1_e_full", 100, 0, 150) 
    lep1_e_cuts                        = rt.TH1D("lep1_e_cuts", "lep1_e_cuts",100, 0, 100)
    missing_rec_e_full               = rt.TH1D( "missing_rec_e_full","missing_rec_e_full", 100, 0, 170)
    missing_rec_e_cuts              = rt.TH1D( "missing_rec_e_cuts","missing_rec_e_cuts", 100, 20, 170)
    chi2_nicolo1                         = rt.TH1D( "chi2_nicolo1","chi2_nicolo1", 100, 0, 150)
    
    chi2_nicolo2                         = rt.TH1D( "chi2_nicolo2","chi2_nicolo2", 50, 0, 20)
    total_rec_mass_full              = rt.TH1D( "total_rec_mass_full","total_rec_mass_full", 100, 0, 350)
    total_rec_mass_cuts             = rt.TH1D("total_rec_mass_cuts","total_rec_mass_cuts", 100, 130, 320)
    
    ########################################################
    #                                                          TAU                                                                       #
    ########################################################
    # Init the histograms with taus
    wmass_had1_tau = rt.TH1D("wmass_had1_tau", "wmass_had1_tau", n_bins_wmass, 40, 140) 
    wmass_had2_tau = rt.TH1D("wmass_had2_tau", "wmass_had2_tau", n_bins_wmass, 70, 90)
    wmass_lep_tau = rt.TH1D("wmass_lep_tau","wmass_lep_tau", n_bins_wmass, 40, 140)
    tmass_had1_tau = rt.TH1D("tmass_had1_tau", "tmass_had1_tau", n_bins_topmass, 100, 220)
    tmass_had2_tau = rt.TH1D("tmass_had2_tau", "tmass_had2_tau", n_bins_topmass, 140, 190)
    tmass_lep_tau = rt.TH1D("tmass_lep_tau", "tmass_lep_tau", n_bins_topmass, 100, 220)
    chi2_histo1_tau = rt.TH1D("chi2_histo1_tau", "chi2_histo1_tau", 100, 0, 150)
    chi2_histo2_tau = rt.TH1D("chi2_histo2_tau", "chi2_histo2_tau", 50, 0, 20)
    chi2_alt_histo1_tau = rt.TH1D("chi2_alt_histo1_tau", "chi2_alt_histo1_tau", 100, 0, 150)
    chi2_alt_histo2_tau = rt.TH1D("chi2_alt_histo2_tau", "chi2_alt_histo2_tau", 50, 0, 20)
    chi2_alt2_histo1_tau = rt.TH1D("chi2_alt2_histo1_tau", "chi2_alt2_histo1_tau", 100, 0, 150)
    chi2_alt2_histo2_tau = rt.TH1D("chi2_alt2_histo2_tau", "chi2_alt2_histo2_tau", 50, 0, 20)
    chi2_whad_h_tau = rt.TH1D("chi2_whad_h_tau", "chi2_whad_tau", 100, 0, 150)
    chi2_thad_h_tau = rt.TH1D("chi2_thad_h_tau", "chi2_thad_tau", 100, 0, 150)
    chi2_wlep_h_tau = rt.TH1D("chi2_wlep_h_tau", "chi2_wlep_tau", 100, 0, 150)
    chi2_tlep_h_tau = rt.TH1D("chi2_tlep_h_tau", "chi2_tlep_tau", 100, 0, 150)
    chi2_tt_h_tau = rt.TH1D("chi2_tt_h_tau", "chi2_tt_tau", 100, 0, 150)
    #also init the other important histograms
    four_jets_mass_cuts_tau =  rt.TH1D("four_jets_mass_cuts_tau","four_jets_mass_cuts_tau", 100, 150, 270)
    four_jets_mass_full_tau =   rt.TH1D("four_jets_mass_full_tau", "four_jets_mass_full_tau",100, 0, 300)
    min_jets_mass_cuts_tau           =  rt.TH1D(   "min_jets_mass_cuts_tau", "min_jets_mass_cuts_tau",100, 10, 100)
    min_jets_mass_full_tau           =  rt.TH1D(   "min_jets_mass_full_tau", "min_jets_mass_full_tau",100, 0, 100)
    second_min_jets_mass_full_tau =  rt.TH1D(   "second_min_jets_mass_full_tau","second_min_jets_mass_full_tau", 100, 0, 110)
    second_min_jets_mass_cuts_tau = rt.TH1D(   "second_min_jets_mass_cuts_tau", "second_min_jets_mass_cuts_tau",100, 20, 110)
    lep1_e_full_tau =  rt.TH1D("lep1_e_full_tau","lep1_e_full_tau", 100, 0, 150) 
    lep1_e_cuts_tau = rt.TH1D("lep1_e_cuts_tau", "lep1_e_cuts_tau",100, 0, 100)
    missing_rec_e_full_tau = rt.TH1D( "missing_rec_e_full_tau","missing_rec_e_full_tau", 100, 0, 170)
    missing_rec_e_cuts_tau = rt.TH1D( "missing_rec_e_cuts_tau","missing_rec_e_cuts_tau", 100, 20, 170)
    chi2_nicolo1_tau = rt.TH1D( "chi2_nicolo1_tau","chi2_nicolo1_tau", 100, 0, 150)
    chi2_nicolo2_tau = rt.TH1D( "chi2_nicolo2_tau","chi2_nicolo2_tau", 50, 0, 20)
    total_rec_mass_full_tau = rt.TH1D( "total_rec_mass_full_tau","total_rec_mass_full_tau", 100, 0, 350)
    total_rec_mass_cuts_tau = rt.TH1D("total_rec_mass_cuts_tau","total_rec_mass_cuts_tau",100, 130, 320)
    
    ########################################################
    #                                                               NO TAU                                                            #
    ########################################################
    # Init the histograms with no taus
    wmass_had1_notau = rt.TH1D("wmass_had1_notau", "wmass_had1_notau", n_bins_wmass, 40, 140) 
    wmass_had2_notau = rt.TH1D("wmass_had2_notau", "wmass_had2_notau", n_bins_wmass, 70, 90)
    wmass_lep_notau = rt.TH1D("wmass_lep_notau","wmass_lep_notau", n_bins_wmass, 40, 140)
    tmass_had1_notau = rt.TH1D("tmass_had1_notau", "tmass_had1_notau", n_bins_topmass, 100, 220)
    tmass_had2_notau = rt.TH1D("tmass_had2_notau", "tmass_had2_notau", n_bins_topmass, 140, 190)
    tmass_lep_notau = rt.TH1D("tmass_lep_notau", "tmass_lep_notau", n_bins_topmass, 100, 220)
    chi2_histo1_notau = rt.TH1D("chi2_histo1_notau", "chi2_histo1_notau", 100, 0, 150)
    chi2_histo2_notau = rt.TH1D("chi2_histo2_notau", "chi2_histo2_notau", 50, 0, 20)
    chi2_alt_histo1_notau = rt.TH1D("chi2_alt_histo1_notau", "chi2_alt_histo1_notau", 100, 0, 150)
    chi2_alt_histo2_notau = rt.TH1D("chi2_alt_histo2_notau", "chi2_alt_histo2_notau", 50, 0, 20)
    chi2_alt2_histo1_notau = rt.TH1D("chi2_alt2_histo1_notau", "chi2_alt2_histo1_notau", 100, 0, 150)
    chi2_alt2_histo2_notau = rt.TH1D("chi2_alt2_histo2_notau", "chi2_alt2_histo2_notau", 50, 0, 20)
    chi2_whad_h_notau = rt.TH1D("chi2_whad_h_notau", "chi2_whad_notau", 100, 0, 150)
    chi2_thad_h_notau = rt.TH1D("chi2_thad_h_notau", "chi2_thad_notau", 100, 0, 150)
    chi2_wlep_h_notau = rt.TH1D("chi2_wlep_h_notau", "chi2_wlep_notau", 100, 0, 150)
    chi2_tlep_h_notau = rt.TH1D("chi2_tlep_h_notau", "chi2_tlep_notau", 100, 0, 150)
    chi2_tt_h_notau = rt.TH1D("chi2_tt_h_notau", "chi2_tt_notau", 100, 0, 150)
    #also init the other important histograms
    four_jets_mass_cuts_notau =  rt.TH1D("four_jets_mass_cuts_notau","four_jets_mass_cuts_notau", 100, 150, 270)
    four_jets_mass_full_notau =   rt.TH1D("four_jets_mass_full_notau", "four_jets_mass_full_notau",100, 0, 300)
    min_jets_mass_cuts_notau           =  rt.TH1D(   "min_jets_mass_cuts_notau", "min_jets_mass_cuts_notau",100, 10, 100)
    min_jets_mass_full_notau            =  rt.TH1D(   "min_jets_mass_full_notau", "min_jets_mass_full_notau",100, 0, 100)
    second_min_jets_mass_full_notau =  rt.TH1D(   "second_min_jets_mass_full_notau","second_min_jets_mass_full_notau", 100, 0, 110)
    second_min_jets_mass_cuts_notau= rt.TH1D(   "second_min_jets_mass_cuts_notau", "second_min_jets_mass_cuts_notau",100, 20, 110)
    lep1_e_full_notau =  rt.TH1D("lep1_e_full_notau","lep1_e_full_notau", 100, 0, 150) 
    lep1_e_cuts_notau = rt.TH1D("lep1_e_cuts_notau", "lep1_e_cuts_notau",100, 0, 100)
    missing_rec_e_full_notau = rt.TH1D( "missing_rec_e_full_notau","missing_rec_e_full_notau", 100, 0, 170)
    missing_rec_e_cuts_notau = rt.TH1D( "missing_rec_e_cuts_notau","missing_rec_e_cuts_notau", 100, 20, 170)
    chi2_nicolo1_notau = rt.TH1D( "chi2_nicolo1_notau","chi2_nicolo1_notau", 100, 0, 150)
    chi2_nicolo2_notau = rt.TH1D( "chi2_nicolo2_notau","chi2_nicolo2_notau", 50, 0, 20)
    total_rec_mass_full_notau = rt.TH1D( "total_rec_mass_full_notau","total_rec_mass_full_notau", 100, 0, 350)
    total_rec_mass_cuts_notau = rt.TH1D("total_rec_mass_cuts_notau","total_rec_mass_cuts_notau", 100, 130, 320)
    
    ########################################################
    #                                                          COMBO                                                                 #
    ########################################################
    # Init the histograms with good combinations
    wmass_had1_gc = rt.TH1D("wmass_had1_gc", "wmass_had1_gc", n_bins_wmass, 40, 140) 
    wmass_had2_gc = rt.TH1D("wmass_had2_gc", "wmass_had2_gc", n_bins_wmass, 70, 90)
    wmass_lep_gc = rt.TH1D("wmass_lep_gc","wmass_lep_gc", n_bins_wmass, 40, 140)
    tmass_had1_gc = rt.TH1D("tmass_had1_gc", "tmass_had1_gc", n_bins_topmass, 100, 220)
    tmass_had2_gc = rt.TH1D("tmass_had2_gc", "tmass_had2_gc", n_bins_topmass, 140, 190)
    tmass_lep_gc = rt.TH1D("tmass_lep_gc", "tmass_lep_gc", n_bins_topmass, 100, 220)
    chi2_histo1_gc = rt.TH1D("chi2_histo1_gc", "chi2_histo1_gc", 100, 0, 150)
    chi2_histo2_gc = rt.TH1D("chi2_histo2_gc", "chi2_histo2_gc", 50, 0, 20)
    chi2_alt_histo1_gc = rt.TH1D("chi2_alt_histo1_gc", "chi2_alt_histo1_gc", 100, 0, 150)
    chi2_alt_histo2_gc = rt.TH1D("chi2_alt_histo2_gc", "chi2_alt_histo2_gc", 50, 0, 20)
    chi2_alt2_histo1_gc = rt.TH1D("chi2_alt2_histo1_gc", "chi2_alt2_histo1_gc", 100, 0, 150)
    chi2_alt2_histo2_gc = rt.TH1D("chi2_alt2_histo2_gc", "chi2_alt2_histo2_gc", 50, 0, 20)
    chi2_whad_h_gc = rt.TH1D("chi2_whad_h_gc", "chi2_whad_gc", 100, 0, 150)
    chi2_thad_h_gc = rt.TH1D("chi2_thad_h_gc", "chi2_thad_gc", 100, 0, 150)
    chi2_wlep_h_gc = rt.TH1D("chi2_wlep_h_gc", "chi2_wlep_gc", 100, 0, 150)
    chi2_tlep_h_gc = rt.TH1D("chi2_tlep_h_gc", "chi2_tlep_gc", 100, 0, 150)
    chi2_tt_h_gc = rt.TH1D("chi2_tt_h_gc", "chi2_tt_gc", 100, 0, 150)
    #also init the other important histograms
    four_jets_mass_cuts_gc =  rt.TH1D("four_jets_mass_cuts_gc","four_jets_mass_cuts_gc", 100, 150, 270)
    four_jets_mass_full_gc =   rt.TH1D("four_jets_mass_full_gc", "four_jets_mass_full_gc",100, 0, 300)
    min_jets_mass_cuts_gc           =  rt.TH1D(   "min_jets_mass_cuts_gc", "min_jets_mass_cuts_gc",100, 10, 100)
    min_jets_mass_full_gc           =  rt.TH1D(   "min_jets_mass_full_gc", "min_jets_mass_full_gc",100, 0, 100)
    second_min_jets_mass_full_gc =  rt.TH1D(   "second_min_jets_mass_full_gc","second_min_jets_mass_full_gc", 100, 0, 110)
    second_min_jets_mass_cuts_gc = rt.TH1D(   "second_min_jets_mass_cuts_gc", "second_min_jets_mass_cuts_gc",100, 20, 110)
    lep1_e_full_gc =  rt.TH1D("lep1_e_full_gc","lep1_e_full_gc", 100, 0, 150) 
    lep1_e_cuts_gc = rt.TH1D("lep1_e_cuts_gc", "lep1_e_cuts_gc",100, 0, 100)
    missing_rec_e_full_gc = rt.TH1D( "missing_rec_e_full_gc","missing_rec_e_full_gc", 100, 0, 170)
    missing_rec_e_cuts_gc = rt.TH1D( "missing_rec_e_cuts_gc","missing_rec_e_cuts_gc", 100, 20, 170)
    chi2_nicolo1_gc = rt.TH1D( "chi2_nicolo1_gc","chi2_nicolo1_gc", 100, 0, 150)
    chi2_nicolo2_gc = rt.TH1D( "chi2_nicolo2_gc","chi2_nicolo2_gc", 50, 0, 20)
    total_rec_mass_full_gc = rt.TH1D( "total_rec_mass_full_gc","total_rec_mass_full_gc", 100, 0, 350)
    total_rec_mass_cuts_gc = rt.TH1D("total_rec_mass_cuts_gc","total_rec_mass_cuts_gc",100, 130, 320)
    
    ########################################################
    #                                                          BAD COMBO                                                          #
    ########################################################
    # Init the histograms with bad combiantions
    wmass_had1_bc = rt.TH1D("wmass_had1_bc", "wmass_had1_bc", n_bins_wmass, 40, 140) 
    wmass_had2_bc = rt.TH1D("wmass_had2_bc", "wmass_had2_bc", n_bins_wmass, 70, 90)
    wmass_lep_bc = rt.TH1D("wmass_lep_bc","wmass_lep_bc", n_bins_wmass, 40, 140)
    tmass_had1_bc = rt.TH1D("tmass_had1_bc", "tmass_had1_bc", n_bins_topmass, 100, 220)
    tmass_had2_bc = rt.TH1D("tmass_had2_bc", "tmass_had2_bc", n_bins_topmass, 140, 190)
    tmass_lep_bc = rt.TH1D("tmass_lep_bc", "tmass_lep_bc", n_bins_topmass, 100, 220)
    chi2_histo1_bc = rt.TH1D("chi2_histo1_bc", "chi2_histo1_bc", 100, 0, 150)
    chi2_histo2_bc = rt.TH1D("chi2_histo2_bc", "chi2_histo2_bc", 50, 0, 20)
    chi2_alt_histo1_bc = rt.TH1D("chi2_alt_histo1_bc", "chi2_alt_histo1_bc", 100, 0, 150)
    chi2_alt_histo2_bc = rt.TH1D("chi2_alt_histo2_bc", "chi2_alt_histo2_bc", 50, 0, 20)
    chi2_alt2_histo1_bc = rt.TH1D("chi2_alt2_histo1_bc", "chi2_alt2_histo1_bc", 100, 0, 150)
    chi2_alt2_histo2_bc = rt.TH1D("chi2_alt2_histo2_bc", "chi2_alt2_histo2_bc", 50, 0, 20)
    chi2_whad_h_bc = rt.TH1D("chi2_whad_h_bc", "chi2_whad_bc", 100, 0, 150)
    chi2_thad_h_bc = rt.TH1D("chi2_thad_h_bc", "chi2_thad_bc", 100, 0, 150)
    chi2_wlep_h_bc = rt.TH1D("chi2_wlep_h_bc", "chi2_wlep_bc", 100, 0, 150)
    chi2_tlep_h_bc = rt.TH1D("chi2_tlep_h_bc", "chi2_tlep_bc", 100, 0, 150)
    chi2_tt_h_bc = rt.TH1D("chi2_tt_h_bc", "chi2_tt_bc", 100, 0, 150)
    #also init the other important histograms
    four_jets_mass_cuts_bc =  rt.TH1D("four_jets_mass_cuts_bc","four_jets_mass_cuts_bc", 100, 150, 270)
    four_jets_mass_full_bc =   rt.TH1D("four_jets_mass_full_bc", "four_jets_mass_full_bc",100, 0, 300)
    min_jets_mass_cuts_bc           =  rt.TH1D(   "min_jets_mass_cuts_bc", "min_jets_mass_cuts_bc",100, 10, 100)
    min_jets_mass_full_bc            =  rt.TH1D(   "min_jets_mass_full_bc", "min_jets_mass_full_bc",100, 0, 100)
    second_min_jets_mass_full_bc =  rt.TH1D(   "second_min_jets_mass_full_bc","second_min_jets_mass_full_bc", 100, 0, 110)
    second_min_jets_mass_cuts_bc= rt.TH1D(   "second_min_jets_mass_cuts_bc", "second_min_jets_mass_cuts_bc",100, 20, 110)
    lep1_e_full_bc =  rt.TH1D("lep1_e_full_bc","lep1_e_full_bc", 100, 0, 150) 
    lep1_e_cuts_bc = rt.TH1D("lep1_e_cuts_bc", "lep1_e_cuts_bc",100, 0, 100)
    missing_rec_e_full_bc = rt.TH1D( "missing_rec_e_full_bc","missing_rec_e_full_bc", 100, 0, 170)
    missing_rec_e_cuts_bc = rt.TH1D( "missing_rec_e_cuts_bc","missing_rec_e_cuts_bc", 100, 20, 170)
    chi2_nicolo1_bc = rt.TH1D( "chi2_nicolo1_bc","chi2_nicolo1_bc", 100, 0, 150)
    chi2_nicolo2_bc = rt.TH1D( "chi2_nicolo2_bc","chi2_nicolo2_bc", 50, 0, 20)
    total_rec_mass_full_bc = rt.TH1D( "total_rec_mass_full_bc","total_rec_mass_full_bc", 100, 0, 350)
    total_rec_mass_cuts_bc = rt.TH1D("total_rec_mass_cuts_bc","total_rec_mass_cuts_bc", 100, 130, 320)
    
    ########################################################
    #                                                          SPECIALS                                                              #
    ########################################################
    
    # Extra dR histograms:
    n_bins_angles = 40
    min_angles = 0
    max_angles = 0.5
    b1_dR = rt.TH1D("b1_dR","b1_dR",n_bins_angles,min_angles,max_angles)
    b2_dR = rt.TH1D("b2_dR","b2_dR",n_bins_angles,min_angles,max_angles)
    q1_dR = rt.TH1D("q1_dR","q1_dR",n_bins_angles,min_angles,max_angles)
    q2_dR = rt.TH1D("q2_dR","q2_dR",n_bins_angles,min_angles,max_angles)
    lep_dR = rt.TH1D("lep_dR","lep_dR",n_bins_angles,min_angles,max_angles)
    neu_dR = rt.TH1D("neu_dR","neu_dR",n_bins_angles,min_angles,max_angles)
    
    # Extra cut_flow_table
    cut_flow_histo = rt.TH1D("cut_flow_histo","cut_flow_histo",21,-1,20)
    
    # Extra SPECIAL histograms for intermediary steps for the cut flow table!
    # only do "full" scale so we can see how much background is eliminated
    four_jets_mass_special = rt.TH1D("four_jets_mass_special","four_jets_mass_special", 100, 0, 300)
    min_jets_mass_special = rt.TH1D("min_jets_mass_special","min_jets_mass_special",100, 0, 100)
    second_min_jets_mass_special = rt.TH1D("second_min_jets_mass_special","second_min_jets_mass_special",100, 0, 110)
    lep1_e_special = rt.TH1D("lep1_e_special","lep1_e_special",100, 0, 150) 
    missing_rec_e_special = rt.TH1D("missing_rec_e_special","missing_rec_e_special",100, 0, 170)
    
    
    
    # Save all the jets for the chi2 algorithm as well as the missing_rec and lep1
    j1 = rt.TLorentzVector()
    j2 = rt.TLorentzVector()
    j3 = rt.TLorentzVector()
    j4 = rt.TLorentzVector()
    lep1 = rt.TLorentzVector()
    missing_rec = rt.TLorentzVector()
    mc_lepton1 = rt.TLorentzVector()
    mc_neutrino1 = rt.TLorentzVector()
    # Save some 4vectors for the W and t particles to be used as temp in the 
    thad = rt.TLorentzVector()
    tlep = rt.TLorentzVector()
    whad = rt.TLorentzVector()
    wlep =  rt.TLorentzVector()
    # Save extra variables useful for the chi2 analysis:
    chi2 = 1000000
    chi2_alt = 1000000
    chi2_alt2 = 1000000
    #note: no need to have a value for chi2_nicolo, all of that is handled inside the HEPPY loop level already! 
    # Replace the real vars with temp only if chi2 is lower!
    thad_save = rt.TLorentzVector()
    tlep_save = rt.TLorentzVector()
    whad_save = rt.TLorentzVector()
    wlep_save =  rt.TLorentzVector()
    # Save associated chi2 components as well:
    chi2_whad_save = 10000000
    chi2_thad_save = 100000
    chi2_wlep_save = 1000000
    chi2_tlep_save = 1000000
    chi2_2tops_save = 1000000
    
    # dR limit to define the smallest angle between MC and reco, default 0.1
    dR = 0.1
    
    counter_all = 0
    counter_tau = 0
    counter_gc = 0
    
    for iev,ev in enumerate(chain):
        # reset value
        chi2 = 1000000
        chi2_alt = 1000000
        chi2_alt2 = 1000000
        chi2_condition = True
        # is_full_tt denotes that the pythia generated file is a full ee > ttbar collision, no particular decay channel selected
        if is_full_tt:
            # Keep only the semileptonic decays for the tt pythia files:
            chi2_condition = (ev.decay_channel == 1)
        cut1 = ev.four_jets_mass > 150
        cut2 = ev.four_jets_mass < 270
        cut3 = ev.min_jets_mass > 10
        cut4 = ev.second_min_jets_mass > 20
        cut5 = ev.lep1_e < 100
        cut6 = ev.missing_rec_e > 20
        all_cuts = cut1 and cut2 and cut3 and cut4 and cut5 and cut6 and chi2_condition
        is_tau_event = abs(ev.mc_lepton1_pdgid) == 15
        
        # Find if event is a good combo:
        lep1.SetPxPyPzE(ev.lep1_px, ev.lep1_py, ev.lep1_pz, ev.lep1_e)
        missing_rec.SetPxPyPzE(ev.missing_rec_px, ev.missing_rec_py, ev.missing_rec_pz, ev.missing_rec_e)
        mc_lepton1.SetPxPyPzE(ev.mc_lepton1_px,ev.mc_lepton1_py, ev.mc_lepton1_pz,ev.mc_lepton1_e)
        mc_neutrino1.SetPxPyPzE(ev.mc_neutrino1_px,ev.mc_neutrino1_py,ev.mc_neutrino1_pz, ev.mc_neutrino1_e)
        lep_angle = lep1.Angle(mc_lepton1.Vect())
        neutrino_angle = missing_rec.Angle(mc_neutrino1.Vect())
        is_goodcombo = (ev.mc_quarkjet1_delta_alpha_wrt_nearest_jet < dR and ev.mc_quarkjet2_delta_alpha_wrt_nearest_jet < dR and ev.mc_bquark2_delta_alpha_wrt_nearest_jet < dR and ev.mc_bquark1_delta_alpha_wrt_nearest_jet < dR and neutrino_angle < dR and lep_angle < dR)
        
        # DO the loop for all events, selection happens when filling! This allows the creation of the cut_flow histogram and special histos
        if chi2_condition:
            # Init P4 of jets
            j1.SetPxPyPzE(ev.jet1_px,ev.jet1_py,ev.jet1_pz,ev.jet1_e)
            j2.SetPxPyPzE(ev.jet2_px,ev.jet2_py,ev.jet2_pz,ev.jet2_e)
            j3.SetPxPyPzE(ev.jet3_px,ev.jet3_py,ev.jet3_pz,ev.jet3_e)
            j4.SetPxPyPzE(ev.jet4_px,ev.jet4_py,ev.jet4_pz,ev.jet4_e)
            # Create a list of the 4 jets 
            jet_list = [j1, j2, j3, j4]
            jet_perm = list(permutations(jet_list))
            
            ################DETERMINE CHI2 USING JET INFO ###################
            for jets in jet_perm:
                # Assume index 0 and 1 represent the W hadronic:
                whad = jets[0] + jets[1]
                # Assume the index 2 represents the b quark for top hadronic:
                thad = whad + jets [2]
                # Assume the index 3 represents the b quark for top leptonic:
                wlep = lep1 + missing_rec
                tlep = wlep + jets [3]
                
                
                # Now we have all 4vectors to perform the chi2
                chi2_whad =((whad.M()-float(mw_had))/float(sw_had))**2
                chi2_thad = ((thad.M()-float(mt_had))/float(st_had))**2
                chi2_wlep = ((wlep.M()-float(mw_lep))/float(sw_lep))**2
                chi2_tlep = ((tlep.M()-float(mt_lep))/float(st_lep))**2
                chi2_2tops = (((tlep.M() + thad.M())-(float(mt_had)+float(mt_lep)))/(float(st_lep)+float(st_had)))**2
                
                # This is referred to as chi2_4 (4 terms) in my thesis 
                chi2_temp = chi2_whad + chi2_thad + chi2_wlep + chi2_tlep
                # chi2_3
                chi2_alt_temp = chi2_whad + chi2_thad + chi2_tlep
                # chi2_5
                chi2_alt2_temp = chi2_whad + chi2_thad + chi2_wlep + chi2_tlep + chi2_2tops
                
                # This is where the chi2 that is used for the plots is chosen! 
                # Set all the _save variables to the chi2 that you want
                # Right now it is setup for chi2_alt:
                
                
                # If the chi2 is smaller than the value of the current chi2: overwrite the 4 vectors & chi2 values
                if chi2_temp < chi2:
                    chi2 = chi2_temp
                    
                # If chi2_alt is smaller than the value 
                if chi2_alt_temp < chi2_alt:
                    chi2_alt = chi2_alt_temp
                    whad_save = whad
                    thad_save = thad
                    wlep_save = wlep
                    tlep_save = tlep
                    chi2_whad_save = chi2_whad
                    chi2_thad_save = chi2_thad
                    chi2_wlep_save = chi2_wlep
                    chi2_tlep_save = chi2_tlep
                    chi2_2tops_save = chi2_2tops
                
                if chi2_alt2_temp < chi2_alt2:
                    chi2_alt2 = chi2_alt2_temp
                
            ################END OF CHI2 ################################
            # Fill in the histograms
            
            # Eliminate the default chi2 values and need success == 1
            if ev.chi2_top_constrainer < 0 or ev.success != 1:
                chi2_nicolo = 1000000
            else:
                chi2_nicolo = ev.chi2_top_constrainer
            
            # First the CUT FLOW TABLE & specials along the way
            four_jets_mass_special.Fill(ev.four_jets_mass)
            cut_flow_histo.Fill(1)
            if cut1: #4j > 150
                cut_flow_histo.Fill(2)
                if cut2: #4j < 270
                    cut_flow_histo.Fill(3)
                    min_jets_mass_special.Fill(ev.min_jets_mass)
                    if cut3: #min_j_mass > 10
                        cut_flow_histo.Fill(4)
                        second_min_jets_mass_special.Fill(ev.second_min_jets_mass)
                        if cut4: # 2nd min j mass > 20
                            cut_flow_histo.Fill(5)
                            lep1_e_special.Fill(ev.lep1_e)
                            if cut5: #lepE < 100
                                cut_flow_histo.Fill(6)
                                missing_rec_e_special.Fill(ev.missing_rec_e)
                                if cut6: #missing_rec_e > 20
                                    cut_flow_histo.Fill(7)
                                    # At this stage the entire pre selection is done
                                    
                                    # Let's fill in the chi2 distributions, these are filled until pre selection only! 
                                    # ALL
                                    chi2_histo1.Fill(chi2)
                                    chi2_histo2.Fill(chi2)
                                    chi2_nicolo1.Fill(chi2_nicolo)
                                    chi2_nicolo2.Fill(chi2_nicolo)
                                    chi2_alt_histo1.Fill(chi2_alt)
                                    chi2_alt_histo2.Fill(chi2_alt)
                                    chi2_alt2_histo1.Fill(chi2_alt2)
                                    chi2_alt2_histo2.Fill(chi2_alt2)
                                        # TAU
                                    if is_tau_event:
                                        chi2_histo1_tau.Fill(chi2)
                                        chi2_histo2_tau.Fill(chi2)
                                        chi2_nicolo1_tau.Fill(chi2_nicolo)
                                        chi2_nicolo2_tau.Fill(chi2_nicolo)
                                        chi2_alt_histo1_tau.Fill(chi2_alt)
                                        chi2_alt_histo2_tau.Fill(chi2_alt)
                                        chi2_alt2_histo1_tau.Fill(chi2_alt2)
                                        chi2_alt2_histo2_tau.Fill(chi2_alt2)
                                    else:
                                        # NO TAU
                                        chi2_histo1_notau.Fill(chi2)
                                        chi2_histo2_notau.Fill(chi2)
                                        chi2_nicolo1_notau.Fill(chi2_nicolo)
                                        chi2_nicolo2_notau.Fill(chi2_nicolo)
                                        chi2_alt_histo1_notau.Fill(chi2_alt)
                                        chi2_alt_histo2_notau.Fill(chi2_alt)
                                        chi2_alt2_histo1_notau.Fill(chi2_alt2)
                                        chi2_alt2_histo2_notau.Fill(chi2_alt2)
                                    if is_goodcombo:
                                        # COMBO
                                        chi2_histo1_gc.Fill(chi2)
                                        chi2_histo2_gc.Fill(chi2)
                                        chi2_nicolo1_gc.Fill(chi2_nicolo)
                                        chi2_nicolo2_gc.Fill(chi2_nicolo)
                                        chi2_alt_histo1_gc.Fill(chi2_alt)
                                        chi2_alt_histo2_gc.Fill(chi2_alt)
                                        chi2_alt2_histo1_gc.Fill(chi2_alt2)
                                        chi2_alt2_histo2_gc.Fill(chi2_alt2)
                                    else:
                                        # BAD COMBO
                                        chi2_histo1_bc.Fill(chi2)
                                        chi2_histo2_bc.Fill(chi2)
                                        chi2_nicolo1_bc.Fill(chi2_nicolo)
                                        chi2_nicolo2_bc.Fill(chi2_nicolo)
                                        chi2_alt_histo1_bc.Fill(chi2_alt)
                                        chi2_alt_histo2_bc.Fill(chi2_alt)
                                        chi2_alt2_histo1_bc.Fill(chi2_alt2)
                                        chi2_alt2_histo2_bc.Fill(chi2_alt2)
                                    
                                    if chi2 < chi2_cut:
                                        cut_flow_histo.Fill(10)
                                    if chi2_alt < chi2_alt_cut:
                                        cut_flow_histo.Fill(11)
                                    if chi2_alt2 < chi2_alt2_cut:
                                        cut_flow_histo.Fill(12)
                                    if chi2_nicolo < chi2_nicolo_cut:
                                        cut_flow_histo.Fill(13)
            # Within if chi2_condition: (True or decay_channel == 1 if full tt)
            
            
            # if within chi2 cuts: all the other histograms
            if chi2_alt < chi2_alt_cut and all_cuts:
                counter_all += 1
                b1_dR.Fill(ev.mc_bquark1_delta_alpha_wrt_nearest_jet)
                b2_dR.Fill(ev.mc_bquark2_delta_alpha_wrt_nearest_jet)
                q1_dR.Fill(ev.mc_quarkjet1_delta_alpha_wrt_nearest_jet)
                q2_dR.Fill(ev.mc_quarkjet2_delta_alpha_wrt_nearest_jet)
                lep_dR.Fill(lep_angle)
                neu_dR.Fill(neutrino_angle)
            ########################################################
            #                                                               ALL                                                                  #
            ########################################################
                tmass_had1.Fill(thad_save.M())
                tmass_had2.Fill(thad_save.M())
                tmass_lep.Fill(tlep_save.M())
                wmass_had1.Fill(whad_save.M())
                wmass_had2.Fill(whad_save.M())
                
                wmass_lep.Fill(wlep_save.M())
                chi2_whad_h.Fill(chi2_whad_save)
                chi2_thad_h.Fill(chi2_thad_save)
                
                chi2_wlep_h.Fill(chi2_wlep_save)
                chi2_tlep_h.Fill(chi2_tlep_save)
                chi2_tt_h.Fill(chi2_2tops_save)
                four_jets_mass_cuts.Fill(ev.four_jets_mass)
                four_jets_mass_full.Fill(ev.four_jets_mass)
                min_jets_mass_cuts.Fill(ev.min_jets_mass)
                
                min_jets_mass_full.Fill(ev.min_jets_mass)
                second_min_jets_mass_full.Fill(ev.second_min_jets_mass)
                second_min_jets_mass_cuts.Fill(ev.second_min_jets_mass)
                lep1_e_full.Fill(ev.lep1_e)
                lep1_e_cuts.Fill(ev.lep1_e)
                
                missing_rec_e_full.Fill(ev.missing_rec_e)
                missing_rec_e_cuts.Fill(ev.missing_rec_e)
                total_rec_mass_full.Fill(ev.total_rec_mass)
                
                total_rec_mass_cuts.Fill(ev.total_rec_mass)
            ########################################################
            #                                                               TAU                                                                  #
            ########################################################
                if is_tau_event:
                    counter_tau += 1
                    tmass_had1_tau.Fill(thad_save.M())
                    tmass_had2_tau.Fill(thad_save.M())
                    tmass_lep_tau.Fill(tlep_save.M())
                    wmass_had1_tau.Fill(whad_save.M())
                    wmass_had2_tau.Fill(whad_save.M())
                    
                    wmass_lep_tau.Fill(wlep_save.M())
                    chi2_whad_h_tau.Fill(chi2_whad_save)
                    chi2_thad_h_tau.Fill(chi2_thad_save)
                    
                    chi2_wlep_h_tau.Fill(chi2_wlep_save)
                    chi2_tlep_h_tau.Fill(chi2_tlep_save)
                    chi2_tt_h_tau.Fill(chi2_2tops_save)
                    four_jets_mass_cuts_tau.Fill(ev.four_jets_mass)
                    four_jets_mass_full_tau.Fill(ev.four_jets_mass)
                    min_jets_mass_cuts_tau.Fill(ev.min_jets_mass)
                    
                    min_jets_mass_full_tau.Fill(ev.min_jets_mass)
                    second_min_jets_mass_full_tau.Fill(ev.second_min_jets_mass)
                    second_min_jets_mass_cuts_tau.Fill(ev.second_min_jets_mass)
                    lep1_e_full_tau.Fill(ev.lep1_e)
                    lep1_e_cuts_tau.Fill(ev.lep1_e)
                    
                    missing_rec_e_full_tau.Fill(ev.missing_rec_e)
                    missing_rec_e_cuts_tau.Fill(ev.missing_rec_e)
                    total_rec_mass_full_tau.Fill(ev.total_rec_mass)
                    
                    total_rec_mass_cuts_tau.Fill(ev.total_rec_mass)
            ########################################################
            #                                                               TAU                                                                  #
            ########################################################
                else:
                    tmass_had1_notau.Fill(thad_save.M())
                    tmass_had2_notau.Fill(thad_save.M())
                    tmass_lep_notau.Fill(tlep_save.M())
                    wmass_had1_notau.Fill(whad_save.M())
                    wmass_had2_notau.Fill(whad_save.M())
                    
                    wmass_lep_notau.Fill(wlep_save.M())
                    chi2_whad_h_notau.Fill(chi2_whad_save)
                    chi2_thad_h_notau.Fill(chi2_thad_save)
                    
                    chi2_wlep_h_notau.Fill(chi2_wlep_save)
                    chi2_tlep_h_notau.Fill(chi2_tlep_save)
                    chi2_tt_h_notau.Fill(chi2_2tops_save)
                    four_jets_mass_cuts_notau.Fill(ev.four_jets_mass)
                    four_jets_mass_full_notau.Fill(ev.four_jets_mass)
                    min_jets_mass_cuts_notau.Fill(ev.min_jets_mass)
                    
                    min_jets_mass_full_notau.Fill(ev.min_jets_mass)
                    second_min_jets_mass_full_notau.Fill(ev.second_min_jets_mass)
                    second_min_jets_mass_cuts_notau.Fill(ev.second_min_jets_mass)
                    lep1_e_full_notau.Fill(ev.lep1_e)
                    lep1_e_cuts_notau.Fill(ev.lep1_e)
                    
                    missing_rec_e_full_notau.Fill(ev.missing_rec_e)
                    missing_rec_e_cuts_notau.Fill(ev.missing_rec_e)
                    total_rec_mass_full_notau.Fill(ev.total_rec_mass)
                    
                    total_rec_mass_cuts_notau.Fill(ev.total_rec_mass)
            ########################################################
            #                                                        COMBO                                                                   #
            ########################################################
                if is_goodcombo:
                    counter_gc += 1
                    tmass_had1_gc.Fill(thad_save.M())
                    tmass_had2_gc.Fill(thad_save.M())
                    tmass_lep_gc.Fill(tlep_save.M())
                    wmass_had1_gc.Fill(whad_save.M())
                    wmass_had2_gc.Fill(whad_save.M())
                    
                    wmass_lep_gc.Fill(wlep_save.M())
                    chi2_whad_h_gc.Fill(chi2_whad_save)
                    chi2_thad_h_gc.Fill(chi2_thad_save)
                    
                    chi2_wlep_h_gc.Fill(chi2_wlep_save)
                    chi2_tlep_h_gc.Fill(chi2_tlep_save)
                    chi2_tt_h_gc.Fill(chi2_2tops_save)
                    four_jets_mass_cuts_gc.Fill(ev.four_jets_mass)
                    four_jets_mass_full_gc.Fill(ev.four_jets_mass)
                    min_jets_mass_cuts_gc.Fill(ev.min_jets_mass)
                    
                    min_jets_mass_full_gc.Fill(ev.min_jets_mass)
                    second_min_jets_mass_full_gc.Fill(ev.second_min_jets_mass)
                    second_min_jets_mass_cuts_gc.Fill(ev.second_min_jets_mass)
                    lep1_e_full_gc.Fill(ev.lep1_e)
                    lep1_e_cuts_gc.Fill(ev.lep1_e)
                    
                    missing_rec_e_full_gc.Fill(ev.missing_rec_e)
                    missing_rec_e_cuts_gc.Fill(ev.missing_rec_e)
                    total_rec_mass_full_gc.Fill(ev.total_rec_mass)
                    
                    total_rec_mass_cuts_gc.Fill(ev.total_rec_mass)
                    
            ########################################################
            #                                             BAD COMBO                                                                       #
            ########################################################
                else:
                    tmass_had1_bc.Fill(thad_save.M())
                    tmass_had2_bc.Fill(thad_save.M())
                    tmass_lep_bc.Fill(tlep_save.M())
                    wmass_had1_bc.Fill(whad_save.M())
                    wmass_had2_bc.Fill(whad_save.M())
                    
                    wmass_lep_bc.Fill(wlep_save.M())
                    chi2_whad_h_bc.Fill(chi2_whad_save)
                    chi2_thad_h_bc.Fill(chi2_thad_save)
                    
                    chi2_wlep_h_bc.Fill(chi2_wlep_save)
                    chi2_tlep_h_bc.Fill(chi2_tlep_save)
                    chi2_tt_h_bc.Fill(chi2_2tops_save)
                    four_jets_mass_cuts_bc.Fill(ev.four_jets_mass)
                    four_jets_mass_full_bc.Fill(ev.four_jets_mass)
                    min_jets_mass_cuts_bc.Fill(ev.min_jets_mass)
                    
                    min_jets_mass_full_bc.Fill(ev.min_jets_mass)
                    second_min_jets_mass_full_bc.Fill(ev.second_min_jets_mass)
                    second_min_jets_mass_cuts_bc.Fill(ev.second_min_jets_mass)
                    lep1_e_full_bc.Fill(ev.lep1_e)
                    lep1_e_cuts_bc.Fill(ev.lep1_e)
                    
                    missing_rec_e_full_bc.Fill(ev.missing_rec_e)
                    missing_rec_e_cuts_bc.Fill(ev.missing_rec_e)
                    total_rec_mass_full_bc.Fill(ev.total_rec_mass)
                    
                    total_rec_mass_cuts_bc.Fill(ev.total_rec_mass)
                    # end of normal chi2 plots
                
            
    # end event loop
#    print "chi2_3 cut:{}".format(chi2_alt_cut)
#    print "Total chi2_3 < cut: {}".format(counter_all)
#    print "Total tau: {}".format(counter_tau)
#    print "Total GC: {}".format(counter_gc)
    
    root_outfile.Write()
    root_outfile.Close()
    return 0
    
    
# Same function but for ROC curves, much thinner binning for all chi2 histos over full range: 0,150

def chi2_algorithm_withcuts_ROC(chain, output_file, param_list,is_full_tt = False, chi2_cut = 100000, chi2_alt_cut = 100000, chi2_alt2_cut = 1000000, chi2_nicolo_cut = 100000):#, filename):
    print chain
    
    # Recover the param list into easier vars:
    mw_had,sw_had,mt_had,st_had,mw_lep,sw_lep,mt_lep,st_lep = param_list 
    
    # Disclaimer: 
    print "You are running this script for the chain with output: ",output_file
    print "The script chi2_algorithm is running assuming this file contains a full ee > ttbar collision: ",is_full_tt
    if is_full_tt:
        print "If this is not correct do not use the data acquired running this script! It will not correct for the decay channels as intended"
    else:
        print "This script is not correcting for decay channels, do not use this mode for files other than the tt!"

    # Handle root file
    root_outfile = rt.TFile(output_file,"RECREATE")
    root_outfile.cd()
    pi_ = 3.14159
    n_events = chain.GetEntries()
    n_bins_topmass = 100
    n_bins_wmass = 100
    #n_bins_angles1 = 15
    #n_bins_angles2 = 40
    ########################################################
    #                                                               ALL                                                                  #
    ########################################################
    # Init the histograms with all combinations together
    wmass_had1 = rt.TH1D("wmass_had1", "wmass_had1", n_bins_wmass, 40, 140)
    wmass_had2 = rt.TH1D("wmass_had2", "wmass_had2", n_bins_wmass, 70, 90)
    wmass_lep = rt.TH1D("wmass_lep","wmass_lep", n_bins_wmass, 40, 140)
    tmass_had1 = rt.TH1D("tmass_had1", "tmass_had1", n_bins_topmass, 100, 220)
    tmass_had2 = rt.TH1D("tmass_had2", "tmass_had2", n_bins_topmass, 140, 190)
    
    tmass_lep = rt.TH1D("tmass_lep", "tmass_lep", n_bins_topmass, 100, 220)
    chi2_histo1 = rt.TH1D("chi2_histo1", "chi2_histo1", 1000, 0, 150)
    chi2_histo2 = rt.TH1D("chi2_histo2", "chi2_histo2", 50, 0, 20)
    chi2_alt_histo1 = rt.TH1D("chi2_alt_histo1", "chi2_alt_histo1", 1000, 0, 150)
    chi2_alt_histo2 = rt.TH1D("chi2_alt_histo2", "chi2_alt_histo2", 50, 0, 20)
    
    chi2_alt2_histo1 = rt.TH1D("chi2_alt2_histo1", "chi2_alt2_histo1", 1000, 0, 150)
    chi2_alt2_histo2 = rt.TH1D("chi2_alt2_histo2", "chi2_alt2_histo2", 50, 0, 20)
    
    chi2_whad_h = rt.TH1D("chi2_whad_h", "chi2_whad", 100, 0, 150)
    chi2_thad_h = rt.TH1D("chi2_thad_h", "chi2_thad", 100, 0, 150)
    chi2_wlep_h = rt.TH1D("chi2_wlep_h", "chi2_wlep", 100, 0, 150)
    chi2_tlep_h = rt.TH1D("chi2_tlep_h", "chi2_tlep", 100, 0, 150)
    chi2_tt_h = rt.TH1D("chi2_tt_h", "chi2_tt", 100, 0, 150)
    #also init the other important histograms
    four_jets_mass_cuts            =  rt.TH1D("four_jets_mass_cuts","four_jets_mass_cuts", 100, 150, 270)
    
    four_jets_mass_full             =   rt.TH1D("four_jets_mass_full", "four_jets_mass_full",100, 0, 300)
    min_jets_mass_cuts            =  rt.TH1D(   "min_jets_mass_cuts", "min_jets_mass_cuts",100, 10, 100)
    min_jets_mass_full             =  rt.TH1D(   "min_jets_mass_full", "min_jets_mass_full",100, 0, 100)
    second_min_jets_mass_full  =  rt.TH1D(   "second_min_jets_mass_full","second_min_jets_mass_full", 100, 0, 110)
    second_min_jets_mass_cuts = rt.TH1D(   "second_min_jets_mass_cuts", "second_min_jets_mass_cuts",100, 20, 110)
    
    lep1_e_full                         =  rt.TH1D("lep1_e_full","lep1_e_full", 100, 0, 150) 
    lep1_e_cuts                        = rt.TH1D("lep1_e_cuts", "lep1_e_cuts",100, 0, 100)
    missing_rec_e_full               = rt.TH1D( "missing_rec_e_full","missing_rec_e_full", 100, 0, 170)
    missing_rec_e_cuts              = rt.TH1D( "missing_rec_e_cuts","missing_rec_e_cuts", 100, 20, 170)
    chi2_nicolo1                         = rt.TH1D( "chi2_nicolo1","chi2_nicolo1", 1000, 0, 150)
    
    chi2_nicolo2                         = rt.TH1D( "chi2_nicolo2","chi2_nicolo2", 50, 0, 20)
    total_rec_mass_full              = rt.TH1D( "total_rec_mass_full","total_rec_mass_full", 100, 0, 350)
    total_rec_mass_cuts             = rt.TH1D("total_rec_mass_cuts","total_rec_mass_cuts", 100, 130, 320)
    
    ########################################################
    #                                                          TAU                                                                       #
    ########################################################
    # Init the histograms with taus
    wmass_had1_tau = rt.TH1D("wmass_had1_tau", "wmass_had1_tau", n_bins_wmass, 40, 140) 
    wmass_had2_tau = rt.TH1D("wmass_had2_tau", "wmass_had2_tau", n_bins_wmass, 70, 90)
    wmass_lep_tau = rt.TH1D("wmass_lep_tau","wmass_lep_tau", n_bins_wmass, 40, 140)
    tmass_had1_tau = rt.TH1D("tmass_had1_tau", "tmass_had1_tau", n_bins_topmass, 100, 220)
    tmass_had2_tau = rt.TH1D("tmass_had2_tau", "tmass_had2_tau", n_bins_topmass, 140, 190)
    tmass_lep_tau = rt.TH1D("tmass_lep_tau", "tmass_lep_tau", n_bins_topmass, 100, 220)
    chi2_histo1_tau = rt.TH1D("chi2_histo1_tau", "chi2_histo1_tau", 1000, 0, 150)
    chi2_histo2_tau = rt.TH1D("chi2_histo2_tau", "chi2_histo2_tau", 50, 0, 20)
    chi2_alt_histo1_tau = rt.TH1D("chi2_alt_histo1_tau", "chi2_alt_histo1_tau", 1000, 0, 150)
    chi2_alt_histo2_tau = rt.TH1D("chi2_alt_histo2_tau", "chi2_alt_histo2_tau", 50, 0, 20)
    chi2_alt2_histo1_tau = rt.TH1D("chi2_alt2_histo1_tau", "chi2_alt2_histo1_tau", 1000, 0, 150)
    chi2_alt2_histo2_tau = rt.TH1D("chi2_alt2_histo2_tau", "chi2_alt2_histo2_tau", 50, 0, 20)
    chi2_whad_h_tau = rt.TH1D("chi2_whad_h_tau", "chi2_whad_tau", 100, 0, 150)
    chi2_thad_h_tau = rt.TH1D("chi2_thad_h_tau", "chi2_thad_tau", 100, 0, 150)
    chi2_wlep_h_tau = rt.TH1D("chi2_wlep_h_tau", "chi2_wlep_tau", 100, 0, 150)
    chi2_tlep_h_tau = rt.TH1D("chi2_tlep_h_tau", "chi2_tlep_tau", 100, 0, 150)
    chi2_tt_h_tau = rt.TH1D("chi2_tt_h_tau", "chi2_tt_tau", 100, 0, 150)
    #also init the other important histograms
    four_jets_mass_cuts_tau =  rt.TH1D("four_jets_mass_cuts_tau","four_jets_mass_cuts_tau", 100, 150, 270)
    four_jets_mass_full_tau =   rt.TH1D("four_jets_mass_full_tau", "four_jets_mass_full_tau",100, 0, 300)
    min_jets_mass_cuts_tau           =  rt.TH1D(   "min_jets_mass_cuts_tau", "min_jets_mass_cuts_tau",100, 10, 100)
    min_jets_mass_full_tau           =  rt.TH1D(   "min_jets_mass_full_tau", "min_jets_mass_full_tau",100, 0, 100)
    second_min_jets_mass_full_tau =  rt.TH1D(   "second_min_jets_mass_full_tau","second_min_jets_mass_full_tau", 100, 0, 110)
    second_min_jets_mass_cuts_tau = rt.TH1D(   "second_min_jets_mass_cuts_tau", "second_min_jets_mass_cuts_tau",100, 20, 110)
    lep1_e_full_tau =  rt.TH1D("lep1_e_full_tau","lep1_e_full_tau", 100, 0, 150) 
    lep1_e_cuts_tau = rt.TH1D("lep1_e_cuts_tau", "lep1_e_cuts_tau",100, 0, 100)
    missing_rec_e_full_tau = rt.TH1D( "missing_rec_e_full_tau","missing_rec_e_full_tau", 100, 0, 170)
    missing_rec_e_cuts_tau = rt.TH1D( "missing_rec_e_cuts_tau","missing_rec_e_cuts_tau", 100, 20, 170)
    chi2_nicolo1_tau = rt.TH1D( "chi2_nicolo1_tau","chi2_nicolo1_tau", 1000, 0, 150)
    chi2_nicolo2_tau = rt.TH1D( "chi2_nicolo2_tau","chi2_nicolo2_tau", 50, 0, 20)
    total_rec_mass_full_tau = rt.TH1D( "total_rec_mass_full_tau","total_rec_mass_full_tau", 100, 0, 350)
    total_rec_mass_cuts_tau = rt.TH1D("total_rec_mass_cuts_tau","total_rec_mass_cuts_tau",100, 130, 320)
    
    ########################################################
    #                                                               NO TAU                                                            #
    ########################################################
    # Init the histograms with no taus
    wmass_had1_notau = rt.TH1D("wmass_had1_notau", "wmass_had1_notau", n_bins_wmass, 40, 140) 
    wmass_had2_notau = rt.TH1D("wmass_had2_notau", "wmass_had2_notau", n_bins_wmass, 70, 90)
    wmass_lep_notau = rt.TH1D("wmass_lep_notau","wmass_lep_notau", n_bins_wmass, 40, 140)
    tmass_had1_notau = rt.TH1D("tmass_had1_notau", "tmass_had1_notau", n_bins_topmass, 100, 220)
    tmass_had2_notau = rt.TH1D("tmass_had2_notau", "tmass_had2_notau", n_bins_topmass, 140, 190)
    tmass_lep_notau = rt.TH1D("tmass_lep_notau", "tmass_lep_notau", n_bins_topmass, 100, 220)
    chi2_histo1_notau = rt.TH1D("chi2_histo1_notau", "chi2_histo1_notau", 1000, 0, 150)
    chi2_histo2_notau = rt.TH1D("chi2_histo2_notau", "chi2_histo2_notau", 50, 0, 20)
    chi2_alt_histo1_notau = rt.TH1D("chi2_alt_histo1_notau", "chi2_alt_histo1_notau", 1000, 0, 150)
    chi2_alt_histo2_notau = rt.TH1D("chi2_alt_histo2_notau", "chi2_alt_histo2_notau", 50, 0, 20)
    chi2_alt2_histo1_notau = rt.TH1D("chi2_alt2_histo1_notau", "chi2_alt2_histo1_notau", 1000, 0, 150)
    chi2_alt2_histo2_notau = rt.TH1D("chi2_alt2_histo2_notau", "chi2_alt2_histo2_notau", 50, 0, 20)
    chi2_whad_h_notau = rt.TH1D("chi2_whad_h_notau", "chi2_whad_notau", 100, 0, 150)
    chi2_thad_h_notau = rt.TH1D("chi2_thad_h_notau", "chi2_thad_notau", 100, 0, 150)
    chi2_wlep_h_notau = rt.TH1D("chi2_wlep_h_notau", "chi2_wlep_notau", 100, 0, 150)
    chi2_tlep_h_notau = rt.TH1D("chi2_tlep_h_notau", "chi2_tlep_notau", 100, 0, 150)
    chi2_tt_h_notau = rt.TH1D("chi2_tt_h_notau", "chi2_tt_notau", 100, 0, 150)
    #also init the other important histograms
    four_jets_mass_cuts_notau =  rt.TH1D("four_jets_mass_cuts_notau","four_jets_mass_cuts_notau", 100, 150, 270)
    four_jets_mass_full_notau =   rt.TH1D("four_jets_mass_full_notau", "four_jets_mass_full_notau",100, 0, 300)
    min_jets_mass_cuts_notau           =  rt.TH1D(   "min_jets_mass_cuts_notau", "min_jets_mass_cuts_notau",100, 10, 100)
    min_jets_mass_full_notau            =  rt.TH1D(   "min_jets_mass_full_notau", "min_jets_mass_full_notau",100, 0, 100)
    second_min_jets_mass_full_notau =  rt.TH1D(   "second_min_jets_mass_full_notau","second_min_jets_mass_full_notau", 100, 0, 110)
    second_min_jets_mass_cuts_notau= rt.TH1D(   "second_min_jets_mass_cuts_notau", "second_min_jets_mass_cuts_notau",100, 20, 110)
    lep1_e_full_notau =  rt.TH1D("lep1_e_full_notau","lep1_e_full_notau", 100, 0, 150) 
    lep1_e_cuts_notau = rt.TH1D("lep1_e_cuts_notau", "lep1_e_cuts_notau",100, 0, 100)
    missing_rec_e_full_notau = rt.TH1D( "missing_rec_e_full_notau","missing_rec_e_full_notau", 100, 0, 170)
    missing_rec_e_cuts_notau = rt.TH1D( "missing_rec_e_cuts_notau","missing_rec_e_cuts_notau", 100, 20, 170)
    chi2_nicolo1_notau = rt.TH1D( "chi2_nicolo1_notau","chi2_nicolo1_notau", 1000, 0, 150)
    chi2_nicolo2_notau = rt.TH1D( "chi2_nicolo2_notau","chi2_nicolo2_notau", 50, 0, 20)
    total_rec_mass_full_notau = rt.TH1D( "total_rec_mass_full_notau","total_rec_mass_full_notau", 100, 0, 350)
    total_rec_mass_cuts_notau = rt.TH1D("total_rec_mass_cuts_notau","total_rec_mass_cuts_notau", 100, 130, 320)
    
    ########################################################
    #                                                          COMBO                                                                 #
    ########################################################
    # Init the histograms with good combinations
    wmass_had1_gc = rt.TH1D("wmass_had1_gc", "wmass_had1_gc", n_bins_wmass, 40, 140) 
    wmass_had2_gc = rt.TH1D("wmass_had2_gc", "wmass_had2_gc", n_bins_wmass, 70, 90)
    wmass_lep_gc = rt.TH1D("wmass_lep_gc","wmass_lep_gc", n_bins_wmass, 40, 140)
    tmass_had1_gc = rt.TH1D("tmass_had1_gc", "tmass_had1_gc", n_bins_topmass, 100, 220)
    tmass_had2_gc = rt.TH1D("tmass_had2_gc", "tmass_had2_gc", n_bins_topmass, 140, 190)
    tmass_lep_gc = rt.TH1D("tmass_lep_gc", "tmass_lep_gc", n_bins_topmass, 100, 220)
    chi2_histo1_gc = rt.TH1D("chi2_histo1_gc", "chi2_histo1_gc", 1000, 0, 150)
    chi2_histo2_gc = rt.TH1D("chi2_histo2_gc", "chi2_histo2_gc", 50, 0, 20)
    chi2_alt_histo1_gc = rt.TH1D("chi2_alt_histo1_gc", "chi2_alt_histo1_gc", 1000, 0, 150)
    chi2_alt_histo2_gc = rt.TH1D("chi2_alt_histo2_gc", "chi2_alt_histo2_gc", 50, 0, 20)
    chi2_alt2_histo1_gc = rt.TH1D("chi2_alt2_histo1_gc", "chi2_alt2_histo1_gc", 1000, 0, 150)
    chi2_alt2_histo2_gc = rt.TH1D("chi2_alt2_histo2_gc", "chi2_alt2_histo2_gc", 50, 0, 20)
    chi2_whad_h_gc = rt.TH1D("chi2_whad_h_gc", "chi2_whad_gc", 100, 0, 150)
    chi2_thad_h_gc = rt.TH1D("chi2_thad_h_gc", "chi2_thad_gc", 100, 0, 150)
    chi2_wlep_h_gc = rt.TH1D("chi2_wlep_h_gc", "chi2_wlep_gc", 100, 0, 150)
    chi2_tlep_h_gc = rt.TH1D("chi2_tlep_h_gc", "chi2_tlep_gc", 100, 0, 150)
    chi2_tt_h_gc = rt.TH1D("chi2_tt_h_gc", "chi2_tt_gc", 100, 0, 150)
    #also init the other important histograms
    four_jets_mass_cuts_gc =  rt.TH1D("four_jets_mass_cuts_gc","four_jets_mass_cuts_gc", 100, 150, 270)
    four_jets_mass_full_gc =   rt.TH1D("four_jets_mass_full_gc", "four_jets_mass_full_gc",100, 0, 300)
    min_jets_mass_cuts_gc           =  rt.TH1D(   "min_jets_mass_cuts_gc", "min_jets_mass_cuts_gc",100, 10, 100)
    min_jets_mass_full_gc           =  rt.TH1D(   "min_jets_mass_full_gc", "min_jets_mass_full_gc",100, 0, 100)
    second_min_jets_mass_full_gc =  rt.TH1D(   "second_min_jets_mass_full_gc","second_min_jets_mass_full_gc", 100, 0, 110)
    second_min_jets_mass_cuts_gc = rt.TH1D(   "second_min_jets_mass_cuts_gc", "second_min_jets_mass_cuts_gc",100, 20, 110)
    lep1_e_full_gc =  rt.TH1D("lep1_e_full_gc","lep1_e_full_gc", 100, 0, 150) 
    lep1_e_cuts_gc = rt.TH1D("lep1_e_cuts_gc", "lep1_e_cuts_gc",100, 0, 100)
    missing_rec_e_full_gc = rt.TH1D( "missing_rec_e_full_gc","missing_rec_e_full_gc", 100, 0, 170)
    missing_rec_e_cuts_gc = rt.TH1D( "missing_rec_e_cuts_gc","missing_rec_e_cuts_gc", 100, 20, 170)
    chi2_nicolo1_gc = rt.TH1D( "chi2_nicolo1_gc","chi2_nicolo1_gc", 1000, 0, 150)
    chi2_nicolo2_gc = rt.TH1D( "chi2_nicolo2_gc","chi2_nicolo2_gc", 50, 0, 20)
    total_rec_mass_full_gc = rt.TH1D( "total_rec_mass_full_gc","total_rec_mass_full_gc", 100, 0, 350)
    total_rec_mass_cuts_gc = rt.TH1D("total_rec_mass_cuts_gc","total_rec_mass_cuts_gc",100, 130, 320)
    
    ########################################################
    #                                                          BAD COMBO                                                          #
    ########################################################
    # Init the histograms with bad combiantions
    wmass_had1_bc = rt.TH1D("wmass_had1_bc", "wmass_had1_bc", n_bins_wmass, 40, 140) 
    wmass_had2_bc = rt.TH1D("wmass_had2_bc", "wmass_had2_bc", n_bins_wmass, 70, 90)
    wmass_lep_bc = rt.TH1D("wmass_lep_bc","wmass_lep_bc", n_bins_wmass, 40, 140)
    tmass_had1_bc = rt.TH1D("tmass_had1_bc", "tmass_had1_bc", n_bins_topmass, 100, 220)
    tmass_had2_bc = rt.TH1D("tmass_had2_bc", "tmass_had2_bc", n_bins_topmass, 140, 190)
    tmass_lep_bc = rt.TH1D("tmass_lep_bc", "tmass_lep_bc", n_bins_topmass, 100, 220)
    chi2_histo1_bc = rt.TH1D("chi2_histo1_bc", "chi2_histo1_bc", 1000, 0, 150)
    chi2_histo2_bc = rt.TH1D("chi2_histo2_bc", "chi2_histo2_bc", 50, 0, 20)
    chi2_alt_histo1_bc = rt.TH1D("chi2_alt_histo1_bc", "chi2_alt_histo1_bc", 1000, 0, 150)
    chi2_alt_histo2_bc = rt.TH1D("chi2_alt_histo2_bc", "chi2_alt_histo2_bc", 50, 0, 20)
    chi2_alt2_histo1_bc = rt.TH1D("chi2_alt2_histo1_bc", "chi2_alt2_histo1_bc", 1000, 0, 150)
    chi2_alt2_histo2_bc = rt.TH1D("chi2_alt2_histo2_bc", "chi2_alt2_histo2_bc", 50, 0, 20)
    chi2_whad_h_bc = rt.TH1D("chi2_whad_h_bc", "chi2_whad_bc", 100, 0, 150)
    chi2_thad_h_bc = rt.TH1D("chi2_thad_h_bc", "chi2_thad_bc", 100, 0, 150)
    chi2_wlep_h_bc = rt.TH1D("chi2_wlep_h_bc", "chi2_wlep_bc", 100, 0, 150)
    chi2_tlep_h_bc = rt.TH1D("chi2_tlep_h_bc", "chi2_tlep_bc", 100, 0, 150)
    chi2_tt_h_bc = rt.TH1D("chi2_tt_h_bc", "chi2_tt_bc", 100, 0, 150)
    #also init the other important histograms
    four_jets_mass_cuts_bc =  rt.TH1D("four_jets_mass_cuts_bc","four_jets_mass_cuts_bc", 100, 150, 270)
    four_jets_mass_full_bc =   rt.TH1D("four_jets_mass_full_bc", "four_jets_mass_full_bc",100, 0, 300)
    min_jets_mass_cuts_bc           =  rt.TH1D(   "min_jets_mass_cuts_bc", "min_jets_mass_cuts_bc",100, 10, 100)
    min_jets_mass_full_bc            =  rt.TH1D(   "min_jets_mass_full_bc", "min_jets_mass_full_bc",100, 0, 100)
    second_min_jets_mass_full_bc =  rt.TH1D(   "second_min_jets_mass_full_bc","second_min_jets_mass_full_bc", 100, 0, 110)
    second_min_jets_mass_cuts_bc= rt.TH1D(   "second_min_jets_mass_cuts_bc", "second_min_jets_mass_cuts_bc",100, 20, 110)
    lep1_e_full_bc =  rt.TH1D("lep1_e_full_bc","lep1_e_full_bc", 100, 0, 150) 
    lep1_e_cuts_bc = rt.TH1D("lep1_e_cuts_bc", "lep1_e_cuts_bc",100, 0, 100)
    missing_rec_e_full_bc = rt.TH1D( "missing_rec_e_full_bc","missing_rec_e_full_bc", 100, 0, 170)
    missing_rec_e_cuts_bc = rt.TH1D( "missing_rec_e_cuts_bc","missing_rec_e_cuts_bc", 100, 20, 170)
    chi2_nicolo1_bc = rt.TH1D( "chi2_nicolo1_bc","chi2_nicolo1_bc", 1000, 0, 150)
    chi2_nicolo2_bc = rt.TH1D( "chi2_nicolo2_bc","chi2_nicolo2_bc", 50, 0, 20)
    total_rec_mass_full_bc = rt.TH1D( "total_rec_mass_full_bc","total_rec_mass_full_bc", 100, 0, 350)
    total_rec_mass_cuts_bc = rt.TH1D("total_rec_mass_cuts_bc","total_rec_mass_cuts_bc", 100, 130, 320)
    
    ########################################################
    #                                                          SPECIALS                                                              #
    ########################################################
    
    # Extra dR histograms:
    n_bins_angles = 40
    min_angles = 0
    max_angles = 0.5
    b1_dR = rt.TH1D("b1_dR","b1_dR",n_bins_angles,min_angles,max_angles)
    b2_dR = rt.TH1D("b2_dR","b2_dR",n_bins_angles,min_angles,max_angles)
    q1_dR = rt.TH1D("q1_dR","q1_dR",n_bins_angles,min_angles,max_angles)
    q2_dR = rt.TH1D("q2_dR","q2_dR",n_bins_angles,min_angles,max_angles)
    lep_dR = rt.TH1D("lep_dR","lep_dR",n_bins_angles,min_angles,max_angles)
    neu_dR = rt.TH1D("neu_dR","neu_dR",n_bins_angles,min_angles,max_angles)
    
    # Extra cut_flow_table
    cut_flow_histo = rt.TH1D("cut_flow_histo","cut_flow_histo",21,-1,20)
    
    # Extra SPECIAL histograms for intermediary steps for the cut flow table!
    # only do "full" scale so we can see how much background is eliminated
    four_jets_mass_special = rt.TH1D("four_jets_mass_special","four_jets_mass_special", 100, 0, 300)
    min_jets_mass_special = rt.TH1D("min_jets_mass_special","min_jets_mass_special",100, 0, 100)
    second_min_jets_mass_special = rt.TH1D("second_min_jets_mass_special","second_min_jets_mass_special",100, 0, 110)
    lep1_e_special = rt.TH1D("lep1_e_special","lep1_e_special",100, 0, 150) 
    missing_rec_e_special = rt.TH1D("missing_rec_e_special","missing_rec_e_special",100, 0, 170)
    
    
    
    # Save all the jets for the chi2 algorithm as well as the missing_rec and lep1
    j1 = rt.TLorentzVector()
    j2 = rt.TLorentzVector()
    j3 = rt.TLorentzVector()
    j4 = rt.TLorentzVector()
    lep1 = rt.TLorentzVector()
    missing_rec = rt.TLorentzVector()
    mc_lepton1 = rt.TLorentzVector()
    mc_neutrino1 = rt.TLorentzVector()
    # Save some 4vectors for the W and t particles to be used as temp in the 
    thad = rt.TLorentzVector()
    tlep = rt.TLorentzVector()
    whad = rt.TLorentzVector()
    wlep =  rt.TLorentzVector()
    # Save extra variables useful for the chi2 analysis:
    chi2 = 1000000
    chi2_alt = 1000000
    chi2_alt2 = 1000000
    #note: no need to have a value for chi2_nicolo, all of that is handled inside the HEPPY loop level already! 
    # Replace the real vars with temp only if chi2 is lower!
    thad_save = rt.TLorentzVector()
    tlep_save = rt.TLorentzVector()
    whad_save = rt.TLorentzVector()
    wlep_save =  rt.TLorentzVector()
    # Save associated chi2 components as well:
    chi2_whad_save = 10000000
    chi2_thad_save = 100000
    chi2_wlep_save = 1000000
    chi2_tlep_save = 1000000
    chi2_2tops_save = 1000000
    
    # dR limit to define the smallest angle between MC and reco, default 0.1
    dR = 0.1
    
    for iev,ev in enumerate(chain):
        # reset value
        chi2 = 1000000
        chi2_alt = 1000000
        chi2_alt2 = 1000000
        chi2_condition = True
        # is_full_tt denotes that the pythia generated file is a full ee > ttbar collision, no particular decay channel selected
        if is_full_tt:
            # Keep only the semileptonic decays for the tt pythia files:
            chi2_condition = (ev.decay_channel == 1)
        cut1 = ev.four_jets_mass > 150
        cut2 = ev.four_jets_mass < 270
        cut3 = ev.min_jets_mass > 10
        cut4 = ev.second_min_jets_mass > 20
        cut5 = ev.lep1_e < 100
        cut6 = ev.missing_rec_e > 20
        all_cuts = cut1 and cut2 and cut3 and cut4 and cut5 and cut6 and chi2_condition
        is_tau_event = abs(ev.mc_lepton1_pdgid) == 15
        
        # Find if event is a good combo:
        lep1.SetPxPyPzE(ev.lep1_px, ev.lep1_py, ev.lep1_pz, ev.lep1_e)
        missing_rec.SetPxPyPzE(ev.missing_rec_px, ev.missing_rec_py, ev.missing_rec_pz, ev.missing_rec_e)
        mc_lepton1.SetPxPyPzE(ev.mc_lepton1_px,ev.mc_lepton1_py, ev.mc_lepton1_pz,ev.mc_lepton1_e)
        mc_neutrino1.SetPxPyPzE(ev.mc_neutrino1_px,ev.mc_neutrino1_py,ev.mc_neutrino1_pz, ev.mc_neutrino1_e)
        lep_angle = lep1.Angle(mc_lepton1.Vect())
        neutrino_angle = missing_rec.Angle(mc_neutrino1.Vect())
        is_goodcombo = (ev.mc_quarkjet1_delta_alpha_wrt_nearest_jet < dR and ev.mc_quarkjet2_delta_alpha_wrt_nearest_jet < dR and ev.mc_bquark2_delta_alpha_wrt_nearest_jet < dR and ev.mc_bquark1_delta_alpha_wrt_nearest_jet < dR and neutrino_angle < dR and lep_angle < dR)
        
        # DO the loop for all events, selection happens when filling! This allows the creation of the cut_flow histogram and special histos
        if chi2_condition:
            # Init P4 of jets
            j1.SetPxPyPzE(ev.jet1_px,ev.jet1_py,ev.jet1_pz,ev.jet1_e)
            j2.SetPxPyPzE(ev.jet2_px,ev.jet2_py,ev.jet2_pz,ev.jet2_e)
            j3.SetPxPyPzE(ev.jet3_px,ev.jet3_py,ev.jet3_pz,ev.jet3_e)
            j4.SetPxPyPzE(ev.jet4_px,ev.jet4_py,ev.jet4_pz,ev.jet4_e)
            # Create a list of the 4 jets 
            jet_list = [j1, j2, j3, j4]
            jet_perm = list(permutations(jet_list))
            
            ################DETERMINE CHI2 USING JET INFO ###################
            for jets in jet_perm:
                # Assume index 0 and 1 represent the W hadronic:
                whad = jets[0] + jets[1]
                # Assume the index 2 represents the b quark for top hadronic:
                thad = whad + jets [2]
                # Assume the index 3 represents the b quark for top leptonic:
                wlep = lep1 + missing_rec
                tlep = wlep + jets [3]
                
                
                # Now we have all 4vectors to perform the chi2
                chi2_whad =((whad.M()-float(mw_had))/float(sw_had))**2
                chi2_thad = ((thad.M()-float(mt_had))/float(st_had))**2
                chi2_wlep = ((wlep.M()-float(mw_lep))/float(sw_lep))**2
                chi2_tlep = ((tlep.M()-float(mt_lep))/float(st_lep))**2
                chi2_2tops = (((tlep.M() + thad.M())-(float(mt_had)+float(mt_lep)))/(float(st_lep)+float(st_had)))**2
                
                # This is referred to as chi2_4 (4 terms) in my thesis 
                chi2_temp = chi2_whad + chi2_thad + chi2_wlep + chi2_tlep
                # chi2_3
                chi2_alt_temp = chi2_whad + chi2_thad + chi2_tlep
                # chi2_5
                chi2_alt2_temp = chi2_whad + chi2_thad + chi2_wlep + chi2_tlep + chi2_2tops
                
                # If the chi2 is smaller than the value of the current chi2: overwrite the 4 vectors & chi2 values
                if chi2_temp < chi2:
                    chi2 = chi2_temp
                    whad_save = whad
                    thad_save = thad
                    wlep_save = wlep
                    tlep_save = tlep
                    chi2_whad_save = chi2_whad
                    chi2_thad_save = chi2_thad
                    chi2_wlep_save = chi2_wlep
                    chi2_tlep_save = chi2_tlep
                    chi2_2tops_save = chi2_2tops
                    
                # If chi2_alt is smaller than the value 
                if chi2_alt_temp < chi2_alt:
                    chi2_alt = chi2_alt_temp
                
                if chi2_alt2_temp < chi2_alt2:
                    chi2_alt2 = chi2_alt2_temp
                
            ################END OF CHI2 ################################
            # Fill in the histograms
            
            # Eliminate the default chi2 values and need success == 1
            if ev.chi2_top_constrainer < 0 or ev.success != 1:
                chi2_nicolo = 1000000
            else:
                chi2_nicolo = ev.chi2_top_constrainer
            
            # First the CUT FLOW TABLE & specials along the way
            four_jets_mass_special.Fill(ev.four_jets_mass)
            cut_flow_histo.Fill(1)
            if cut1: #4j > 150
                cut_flow_histo.Fill(2)
                if cut2: #4j < 270
                    cut_flow_histo.Fill(3)
                    min_jets_mass_special.Fill(ev.min_jets_mass)
                    if cut3: #min_j_mass > 10
                        cut_flow_histo.Fill(4)
                        second_min_jets_mass_special.Fill(ev.second_min_jets_mass)
                        if cut4: # 2nd min j mass > 20
                            cut_flow_histo.Fill(5)
                            lep1_e_special.Fill(ev.lep1_e)
                            if cut5: #lepE < 100
                                cut_flow_histo.Fill(6)
                                missing_rec_e_special.Fill(ev.missing_rec_e)
                                if cut6: #missing_rec_e > 20
                                    cut_flow_histo.Fill(7)
                                    # At this stage the entire pre selection is done
                                    
                                    # Let's fill in the chi2 distributions, these are filled until pre selection only! 
                                    # ALL
                                    chi2_histo1.Fill(chi2)
                                    chi2_histo2.Fill(chi2)
                                    chi2_nicolo1.Fill(chi2_nicolo)
                                    chi2_nicolo2.Fill(chi2_nicolo)
                                    chi2_alt_histo1.Fill(chi2_alt)
                                    chi2_alt_histo2.Fill(chi2_alt)
                                    chi2_alt2_histo1.Fill(chi2_alt2)
                                    chi2_alt2_histo2.Fill(chi2_alt2)
                                        # TAU
                                    if is_tau_event:
                                        chi2_histo1_tau.Fill(chi2)
                                        chi2_histo2_tau.Fill(chi2)
                                        chi2_nicolo1_tau.Fill(chi2_nicolo)
                                        chi2_nicolo2_tau.Fill(chi2_nicolo)
                                        chi2_alt_histo1_tau.Fill(chi2_alt)
                                        chi2_alt_histo2_tau.Fill(chi2_alt)
                                        chi2_alt2_histo1_tau.Fill(chi2_alt2)
                                        chi2_alt2_histo2_tau.Fill(chi2_alt2)
                                    else:
                                        # NO TAU
                                        chi2_histo1_notau.Fill(chi2)
                                        chi2_histo2_notau.Fill(chi2)
                                        chi2_nicolo1_notau.Fill(chi2_nicolo)
                                        chi2_nicolo2_notau.Fill(chi2_nicolo)
                                        chi2_alt_histo1_notau.Fill(chi2_alt)
                                        chi2_alt_histo2_notau.Fill(chi2_alt)
                                        chi2_alt2_histo1_notau.Fill(chi2_alt2)
                                        chi2_alt2_histo2_notau.Fill(chi2_alt2)
                                    if is_goodcombo:
                                        # COMBO
                                        chi2_histo1_gc.Fill(chi2)
                                        chi2_histo2_gc.Fill(chi2)
                                        chi2_nicolo1_gc.Fill(chi2_nicolo)
                                        chi2_nicolo2_gc.Fill(chi2_nicolo)
                                        chi2_alt_histo1_gc.Fill(chi2_alt)
                                        chi2_alt_histo2_gc.Fill(chi2_alt)
                                        chi2_alt2_histo1_gc.Fill(chi2_alt2)
                                        chi2_alt2_histo2_gc.Fill(chi2_alt2)
                                    else:
                                        # BAD COMBO
                                        chi2_histo1_bc.Fill(chi2)
                                        chi2_histo2_bc.Fill(chi2)
                                        chi2_nicolo1_bc.Fill(chi2_nicolo)
                                        chi2_nicolo2_bc.Fill(chi2_nicolo)
                                        chi2_alt_histo1_bc.Fill(chi2_alt)
                                        chi2_alt_histo2_bc.Fill(chi2_alt)
                                        chi2_alt2_histo1_bc.Fill(chi2_alt2)
                                        chi2_alt2_histo2_bc.Fill(chi2_alt2)
                                    
                                    if chi2 < chi2_cut:
                                        cut_flow_histo.Fill(10)
                                    if chi2_alt < chi2_alt_cut:
                                        cut_flow_histo.Fill(11)
                                    if chi2_alt2 < chi2_alt2_cut:
                                        cut_flow_histo.Fill(12)
                                    if ev.chi2_top_constrainer < chi2_nicolo_cut:
                                        cut_flow_histo.Fill(13)
            # Within if chi2_condition: (True or decay_channel == 1 if full tt)
            
            
            # if within chi2 cuts: all the other histograms
            if chi2 < chi2_cut and all_cuts:
                b1_dR.Fill(ev.mc_bquark1_delta_alpha_wrt_nearest_jet)
                b2_dR.Fill(ev.mc_bquark2_delta_alpha_wrt_nearest_jet)
                q1_dR.Fill(ev.mc_quarkjet1_delta_alpha_wrt_nearest_jet)
                q2_dR.Fill(ev.mc_quarkjet2_delta_alpha_wrt_nearest_jet)
                lep_dR.Fill(lep_angle)
                neu_dR.Fill(neutrino_angle)
            ########################################################
            #                                                               ALL                                                                  #
            ########################################################
                tmass_had1.Fill(thad_save.M())
                tmass_had2.Fill(thad_save.M())
                tmass_lep.Fill(tlep_save.M())
                wmass_had1.Fill(whad_save.M())
                wmass_had2.Fill(whad_save.M())
                
                wmass_lep.Fill(wlep_save.M())
                chi2_whad_h.Fill(chi2_whad_save)
                chi2_thad_h.Fill(chi2_thad_save)
                
                chi2_wlep_h.Fill(chi2_wlep_save)
                chi2_tlep_h.Fill(chi2_tlep_save)
                chi2_tt_h.Fill(chi2_2tops_save)
                four_jets_mass_cuts.Fill(ev.four_jets_mass)
                four_jets_mass_full.Fill(ev.four_jets_mass)
                min_jets_mass_cuts.Fill(ev.min_jets_mass)
                
                min_jets_mass_full.Fill(ev.min_jets_mass)
                second_min_jets_mass_full.Fill(ev.second_min_jets_mass)
                second_min_jets_mass_cuts.Fill(ev.second_min_jets_mass)
                lep1_e_full.Fill(ev.lep1_e)
                lep1_e_cuts.Fill(ev.lep1_e)
                
                missing_rec_e_full.Fill(ev.missing_rec_e)
                missing_rec_e_cuts.Fill(ev.missing_rec_e)
                total_rec_mass_full.Fill(ev.total_rec_mass)
                
                total_rec_mass_cuts.Fill(ev.total_rec_mass)
            ########################################################
            #                                                               TAU                                                                  #
            ########################################################
                if is_tau_event:
                    tmass_had1_tau.Fill(thad_save.M())
                    tmass_had2_tau.Fill(thad_save.M())
                    tmass_lep_tau.Fill(tlep_save.M())
                    wmass_had1_tau.Fill(whad_save.M())
                    wmass_had2_tau.Fill(whad_save.M())
                    
                    wmass_lep_tau.Fill(wlep_save.M())
                    chi2_whad_h_tau.Fill(chi2_whad_save)
                    chi2_thad_h_tau.Fill(chi2_thad_save)
                    
                    chi2_wlep_h_tau.Fill(chi2_wlep_save)
                    chi2_tlep_h_tau.Fill(chi2_tlep_save)
                    chi2_tt_h_tau.Fill(chi2_2tops_save)
                    four_jets_mass_cuts_tau.Fill(ev.four_jets_mass)
                    four_jets_mass_full_tau.Fill(ev.four_jets_mass)
                    min_jets_mass_cuts_tau.Fill(ev.min_jets_mass)
                    
                    min_jets_mass_full_tau.Fill(ev.min_jets_mass)
                    second_min_jets_mass_full_tau.Fill(ev.second_min_jets_mass)
                    second_min_jets_mass_cuts_tau.Fill(ev.second_min_jets_mass)
                    lep1_e_full_tau.Fill(ev.lep1_e)
                    lep1_e_cuts_tau.Fill(ev.lep1_e)
                    
                    missing_rec_e_full_tau.Fill(ev.missing_rec_e)
                    missing_rec_e_cuts_tau.Fill(ev.missing_rec_e)
                    total_rec_mass_full_tau.Fill(ev.total_rec_mass)
                    
                    total_rec_mass_cuts_tau.Fill(ev.total_rec_mass)
            ########################################################
            #                                                               TAU                                                                  #
            ########################################################
                else:
                    tmass_had1_notau.Fill(thad_save.M())
                    tmass_had2_notau.Fill(thad_save.M())
                    tmass_lep_notau.Fill(tlep_save.M())
                    wmass_had1_notau.Fill(whad_save.M())
                    wmass_had2_notau.Fill(whad_save.M())
                    
                    wmass_lep_notau.Fill(wlep_save.M())
                    chi2_whad_h_notau.Fill(chi2_whad_save)
                    chi2_thad_h_notau.Fill(chi2_thad_save)
                    
                    chi2_wlep_h_notau.Fill(chi2_wlep_save)
                    chi2_tlep_h_notau.Fill(chi2_tlep_save)
                    chi2_tt_h_notau.Fill(chi2_2tops_save)
                    four_jets_mass_cuts_notau.Fill(ev.four_jets_mass)
                    four_jets_mass_full_notau.Fill(ev.four_jets_mass)
                    min_jets_mass_cuts_notau.Fill(ev.min_jets_mass)
                    
                    min_jets_mass_full_notau.Fill(ev.min_jets_mass)
                    second_min_jets_mass_full_notau.Fill(ev.second_min_jets_mass)
                    second_min_jets_mass_cuts_notau.Fill(ev.second_min_jets_mass)
                    lep1_e_full_notau.Fill(ev.lep1_e)
                    lep1_e_cuts_notau.Fill(ev.lep1_e)
                    
                    missing_rec_e_full_notau.Fill(ev.missing_rec_e)
                    missing_rec_e_cuts_notau.Fill(ev.missing_rec_e)
                    total_rec_mass_full_notau.Fill(ev.total_rec_mass)
                    
                    total_rec_mass_cuts_notau.Fill(ev.total_rec_mass)
            ########################################################
            #                                                        COMBO                                                                   #
            ########################################################
                if is_goodcombo:
                    tmass_had1_gc.Fill(thad_save.M())
                    tmass_had2_gc.Fill(thad_save.M())
                    tmass_lep_gc.Fill(tlep_save.M())
                    wmass_had1_gc.Fill(whad_save.M())
                    wmass_had2_gc.Fill(whad_save.M())
                    
                    wmass_lep_gc.Fill(wlep_save.M())
                    chi2_whad_h_gc.Fill(chi2_whad_save)
                    chi2_thad_h_gc.Fill(chi2_thad_save)
                    
                    chi2_wlep_h_gc.Fill(chi2_wlep_save)
                    chi2_tlep_h_gc.Fill(chi2_tlep_save)
                    chi2_tt_h_gc.Fill(chi2_2tops_save)
                    four_jets_mass_cuts_gc.Fill(ev.four_jets_mass)
                    four_jets_mass_full_gc.Fill(ev.four_jets_mass)
                    min_jets_mass_cuts_gc.Fill(ev.min_jets_mass)
                    
                    min_jets_mass_full_gc.Fill(ev.min_jets_mass)
                    second_min_jets_mass_full_gc.Fill(ev.second_min_jets_mass)
                    second_min_jets_mass_cuts_gc.Fill(ev.second_min_jets_mass)
                    lep1_e_full_gc.Fill(ev.lep1_e)
                    lep1_e_cuts_gc.Fill(ev.lep1_e)
                    
                    missing_rec_e_full_gc.Fill(ev.missing_rec_e)
                    missing_rec_e_cuts_gc.Fill(ev.missing_rec_e)
                    total_rec_mass_full_gc.Fill(ev.total_rec_mass)
                    
                    total_rec_mass_cuts_gc.Fill(ev.total_rec_mass)
                    
            ########################################################
            #                                             BAD COMBO                                                                       #
            ########################################################
                else:
                    tmass_had1_bc.Fill(thad_save.M())
                    tmass_had2_bc.Fill(thad_save.M())
                    tmass_lep_bc.Fill(tlep_save.M())
                    wmass_had1_bc.Fill(whad_save.M())
                    wmass_had2_bc.Fill(whad_save.M())
                    
                    wmass_lep_bc.Fill(wlep_save.M())
                    chi2_whad_h_bc.Fill(chi2_whad_save)
                    chi2_thad_h_bc.Fill(chi2_thad_save)
                    
                    chi2_wlep_h_bc.Fill(chi2_wlep_save)
                    chi2_tlep_h_bc.Fill(chi2_tlep_save)
                    chi2_tt_h_bc.Fill(chi2_2tops_save)
                    four_jets_mass_cuts_bc.Fill(ev.four_jets_mass)
                    four_jets_mass_full_bc.Fill(ev.four_jets_mass)
                    min_jets_mass_cuts_bc.Fill(ev.min_jets_mass)
                    
                    min_jets_mass_full_bc.Fill(ev.min_jets_mass)
                    second_min_jets_mass_full_bc.Fill(ev.second_min_jets_mass)
                    second_min_jets_mass_cuts_bc.Fill(ev.second_min_jets_mass)
                    lep1_e_full_bc.Fill(ev.lep1_e)
                    lep1_e_cuts_bc.Fill(ev.lep1_e)
                    
                    missing_rec_e_full_bc.Fill(ev.missing_rec_e)
                    missing_rec_e_cuts_bc.Fill(ev.missing_rec_e)
                    total_rec_mass_full_bc.Fill(ev.total_rec_mass)
                    
                    total_rec_mass_cuts_bc.Fill(ev.total_rec_mass)
                    # end of normal chi2 plots
                
            
    # end event loop
    root_outfile.Write()
    root_outfile.Close()
    return 0







####################FUNCTION CALLS ###########################
pi_ = 3.14159
textfilename = 'fit_stats.txt'
# mw_had,sw_had,mt_had,st_had,mw_lep,sw_lep,mt_lep,st_lep
param_list_Nicolo = [81.88, 16.69, 164.59, 17.13, 105.43, 17.37, 177.37, 20.25]
param_list_self = []

#print ch.GetEntries()
#simple_loop(ch)
#print testangle()

#print sample_dir, ch.GetEntries()

#mcmatch_histo(ch, path_to_output_file)
#mcmatch_histo_wtop(ch, path_to_output_file, path_to_output_dir+textfilename)

#is_full_tt = ('tt' in sample_dir)
#chi2_algorithm(ch, path_to_output_file, param_list_Nicolo, is_full_tt)




