import os,sys
# Run root in batch mode
sys.argv.append( '-b-' )
import ROOT as rt
import math
import time

# Retrieve a histogram from .root file (e.g. selection_histograms.root) and display it nicely, and save it to png or pdf

############### SAVE HISTO FUNCTIONS ###########################

def get_params_fit(fitter, distribution_name):
        chi2 = fitter.GetChisquare()
        ndof = fitter.GetNDF()
        mean = fitter.GetParameter(1)
        mean_error = fitter.GetParError(1)
        width = fitter.GetParameter(2)
        width_error = fitter.GetParError(2)
        return [distribution_name ,mean,mean_error, width,width_error, chi2, ndof]
        

def save_params_to_txt(param_list, filename):
        file = open(filename, "wt")
        file.write("{:20};\t{:.5};\t{:.5};\t{:.5};\t{:.5};\t{:.10}\n".format("dist","mean","meanE","width","widthE","chi2/ndof"))
        #file.write("dist;\tmean;\twidth;\tchi2/ndof\n")
        for list in param_list:
            file.write("{:20};\t{:.5};\t{:.5};\t{:.5};\t{:.5};\t{:.5}\n".format(list[0],list[1],list[2],list[3],list[4],list[5]/list[6]))
        file.close()
        return 0


def save_histo_to_image(sample_dir, rootname, histo_name,xlabel,ylabel,extension, log = "", fit ="" , xmin = None, xmax = None, subrange = False, scale = 0):
    
    # Retrieve file and histogram from the file
    rootfile = rt.TFile(sample_dir+rootname,"READ")
    canvas = rt.TCanvas("canvas","canvas", 600, 600)
    pad = rt.TPad("pad","pad",0.05,0.05,0.95,0.95)
    #pad = pad.Clone()
    canvas.cd()
    pad.Draw()
    histo = rootfile.Get(histo_name)
    histo.Sumw2()
    if scale == -1:
        histo.Scale(float(1)/ histo.GetEffectiveEntries())
    elif scale:
        histo.Scale(scale)
    #histo.Draw("E")
    # Make histogram look nice
    # Hide the stat box
    rt.gStyle.SetOptStat(0)
    # Remove title
    histo.SetTitle("")
    # Set Y-axis to log scale
    #if "y" in log.lower():
    #    rt.gPad.SetLogy()
    # Set X-axis to log scale
    if "x" in log.lower():
        rt.gPad.SetLogx()
    
    # Label axes nicely
    histo.SetXTitle(xlabel)
    histo.SetYTitle(ylabel)
    
    histo.GetYaxis().SetNdivisions(505)
    histo.GetYaxis().SetTitleOffset(1.1)
    #histo.GetYaxis().SetMaxDigits(2)
    rt.TGaxis.SetMaxDigits(3)
    
    # Change Colours and Line properties
    histo.SetLineWidth(2)
    histo.SetLineColor(rt.kBlue)
    histo.SetLineStyle(1)
    histo.SetFillColor(rt.kBlue)
    histo.SetFillStyle(3002)
    
    #Change axis title sizes before updating
    histo.SetTitleSize(0.045,"xy") #default size = 0.035
    histo.SetTitleFont(42,"xy")
    canvas.Update()
    
    # Fit if the option is selected:
    if fit != "":
        if xmax is not None:
            fit_func = rt.TF1("fit_func",fit, xmin, xmax)
            histo.Fit(fit_func,"ER")
        elif subrange:
            fit_func = rt.TF1("fit_func",fit, histo.GetMean()-histo.GetRMS(), histo.GetMean()+histo.GetRMS())
            histo.Fit(fit_func,"ER")
        else:
            fit_func = rt.TF1("fit_func",fit)
            histo.Fit(fit_func,"E")
    
    # Finally save the histogram as png or pdf
    canvas.cd()
    canvas.Update()
    histo.Draw("HIST")
    if fit != "":
        fit_func.Draw("same")
    canvas.SaveAs(sample_dir+histo_name+'.'+extension)
    #time.sleep(0.1)
    rt.gPad.SetLogy()
    histo.Draw("HIST")
    if fit != "":
        fit_func.Draw("same")
    canvas.cd()
    canvas.Update()
    #histo.Draw("HIST")
    canvas.SaveAs(sample_dir+histo_name+'_logy'+'.'+extension)
    canvas.Close()
    rootfile.Close()
    if fit != "":
        return get_params_fit(fit_func, histo_name)
    return 0


############### CALL HISTO FUNCTIONS ###########################

PLOTS_dir = 'PLOTS/'
#sample = 'splitmtop_1730_2/'
sample= 'chi2_params/'
#rootname = 'selection_histograms.root'
rootname = 'looper_histograms.root'
fitname= 'fit_chi2_parameters.txt'
sample_dir = PLOTS_dir+sample
fitter = "gaus"
extension = 'pdf'

# Function calls for determining chi2 parameters:
# TODO: add fitting of the curves! 
chi2_parameters = []

#chi2_parameters.append( save_histo_to_image(sample_dir, rootname, "wmass_had1", "m_{W}^{had}     (GeV)", "events", extension, fit = fitter, xmin =80, xmax = 120))
#chi2_parameters.append( save_histo_to_image(sample_dir, rootname, "tmass_had1", "m_{t}^{had}     (GeV)", "events", extension, fit = fitter))
#chi2_parameters.append( save_histo_to_image(sample_dir, rootname, "wmass_lep", "m_{W}^{lep}     (GeV)", "events", extension, fit = fitter, xmin = 70, xmax = 100))
#chi2_parameters.append( save_histo_to_image(sample_dir, rootname, "tmass_lep", "m_{t}^{lep}     (GeV)", "events", extension, fit = fitter, xmin = 120, xmax  =180))


#save_params_to_txt(chi2_parameters, sample_dir+fitname)

#distribution = "jet1_e"
#histo_name1 = 'histo_'+distribution+'_cut8'
#histo_name2 = 'histo_jet2_e_cut8' 
#histo_name3 = 'histo_jet3_e_cut8' 
#histo_name4 = 'histo_jet4_e_cut8' 
#histo_name5 = 'histo_lep1_e_cut5'
#histo_name6 = 'histo_four_jets_mass_cuts_cut2'
#histo_name7 = 'histo_missing_rec_e_cut8'
#
#
#save_histo_to_image(sample_dir, rootname, "histo_mc_bquark1_delta_alpha_wrt_nearest_jet_zoom_nocut", "angle b1,jet", "events", extension)
#save_histo_to_image(sample_dir, rootname, "histo_mc_bquark2_delta_alpha_wrt_nearest_jet_zoom_nocut", "angle b2,jet", "events", extension)
#
#save_histo_to_image(sample_dir, rootname, "histo_mc_bquark1_delta_e_wrt_nearest_jet_cut1", "E_{b1}^{MC} - E_{j}     (GeV)", "events", extension)
#save_histo_to_image(sample_dir, rootname, "histo_mc_bquark2_delta_e_wrt_nearest_jet_cut1", "E_{b2}^{MC} - E_{j}     (GeV)", "events", extension)
#
#save_histo_to_image(sample_dir, rootname, "histo_mc_quarkjet1_delta_alpha_wrt_nearest_jet_zoom_nocut", "angle q1,jet", "events", extension)
#save_histo_to_image(sample_dir, rootname, "histo_mc_quarkjet2_delta_alpha_wrt_nearest_jet_zoom_nocut", "angle q2,jet", "events", extension)
#save_histo_to_image(sample_dir, rootname, "histo_mc_quarkjet1_delta_e_wrt_nearest_jet_cut1", "E_{q1}^{MC} - E_{j}     (GeV)", "events", extension)
#save_histo_to_image(sample_dir, rootname, "histo_mc_quarkjet2_delta_e_wrt_nearest_jet_cut1", "E_{q2}^{MC} - E_{j}     (GeV)", "events", extension)
#
#save_histo_to_image(sample_dir, rootname, "histo_lepton_ediff_nocut", "E_{lep}^{MC} - E_{lep}^{Rec}     (GeV)", "events", extension)
#save_histo_to_image(sample_dir, rootname, "histo_neutrino_ediff_nocut", "E_{#nu}^{MC} - E_{#nu}^{Rec}     (GeV)", "events", extension)



#save_histo_to_image(sample_dir, rootname, histo_name1,"E_{jet1}   (GeV)","events",extension,"y")
#save_histo_to_image(sample_dir, rootname, histo_name2,"E_{jet2}   (GeV)","events",extension,"y")
#save_histo_to_image(sample_dir, rootname, histo_name3,"E_{jet3}   (GeV)","events",extension,"y")
#save_histo_to_image(sample_dir, rootname, histo_name4,"E_{jet4}   (GeV)","events",extension,"y")
#save_histo_to_image(sample_dir, rootname, histo_name5,"E_{lepton}   (GeV)","events",extension,"y")
#save_histo_to_image(sample_dir, rootname, histo_name6,"E_{4j}   (GeV)","events",extension,"y")
#save_histo_to_image(sample_dir, rootname, histo_name6,"#slash{E}   (GeV)","events",extension,"y")
# File does get saved but seems to be damaged! 









