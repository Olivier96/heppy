import os,sys
# Run root in batch mode
sys.argv.append( '-b-' )
import ROOT as rt
from ROOT import gROOT
import math
from copy import copy


# Retrieve multiple histograms from .root file (e.g. selection_histograms.root) and display it nicely, and save it to png or pdf


#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
############################# RATIO ###################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################




############### SAVE HISTO FUNCTIONS ###########################


def save_thstack_to_image(rootname_list, nfiles_list,scales_list,histo_name_list,legend_list,legend_spot, output_file,xlabel,ylabel,fillcolours,fillstyles, log = "", stack_option = "", rebin = 0, ratiomode = None, ref_ratio_index = -1, ylabel_ratio = "", latex_text = "", latex_corner = "topleft", legend_title = ""):

    rt.TGaxis.SetMaxDigits(3)
    if rebin == 0:
        save_thstack_to_image_noratio(rootname_list, nfiles_list,scales_list,histo_name_list,legend_list,legend_spot, output_file,xlabel,ylabel,fillcolours,fillstyles,log = "",latex_text = latex_text, latex_corner = latex_corner, legend_title=legend_title, stack_option=stack_option)
        save_thstack_to_image_noratio(rootname_list, nfiles_list,scales_list,histo_name_list,legend_list,legend_spot, output_file[:-4]+"_logy.png",xlabel,ylabel,fillcolours,fillstyles, log = "y",latex_text = latex_text, latex_corner = latex_corner, legend_title=legend_title, stack_option=stack_option)
    else:
        save_thstack_to_image_noratio(rootname_list, nfiles_list,scales_list,histo_name_list,legend_list,legend_spot, output_file,xlabel,ylabel,fillcolours,fillstyles,log = "",latex_text = latex_text, latex_corner = latex_corner, legend_title=legend_title, stack_option=stack_option,rebin=rebin)
        save_thstack_to_image_noratio(rootname_list, nfiles_list,scales_list,histo_name_list,legend_list,legend_spot, output_file[:-4]+"_logy.png",xlabel,ylabel,fillcolours,fillstyles, log = "y",latex_text = latex_text, latex_corner = latex_corner, legend_title=legend_title, stack_option=stack_option,rebin=rebin)
    # possible ratio modes:
        #divide: A/B
        #diff: A-B
        #fraction: (A-B)/B
        # For B the reference histogram chosen by ref_ratio_index
        
    N_histos = len(rootname_list)
    # If the histo_name_list is given as a string of 1 histo_name create a list containing that name N_histos times
    if type(histo_name_list) == str:
        histo_name_list = [histo_name_list]*N_histos
    
    ################## PADS & CANVAS ###################
    # Create a canvas, pad, legend and stack:
    gROOT.SetBatch(1)
    canvas = rt.TCanvas("canvas","canvas", 700, 525)
    
    ################## PADS ##########################
    mainpad = rt.TPad("mainpad","mainpad",0,0.30,1,1)
    ratiopad = rt.TPad("ratiopad","ratiopad",0,0,1,0.30)
    #canvas.cd()
    mainpad.Draw()
    ratiopad.Draw()
    mainpad.SetTopMargin(0.08)
    mainpad.SetBottomMargin(0.0)
    ratiopad.SetTopMargin(0)
    ratiopad.SetBottomMargin(0.3)
    mainpad.cd()
    mainpad.SetTicks(1)
    mainpad.Update()
    
    
    ################## STACK & LEGEND ###################
    stack = rt.THStack("stack","")
    rt.gStyle.SetLegendFont(42)
    if legend_spot == "topleft":
        legend = rt.TLegend(0.1, 0.71, 0.35, 0.88)
    elif legend_spot == "topright":
        legend = rt.TLegend(0.68, 0.71, 0.87, 0.88)
    else:
        #default is top left
        legend = rt.TLegend(0.1, 0.71, 0.35, 0.88)
    #legend.SetHeader(legend_title+stack_option,"C")
    legend.SetTextSize(0.035)
    legend.SetBorderSize(0)
    
    ################## FILL USING HISTO FROM FILES ###################
    histo_list = []
    scale_factor_list = []
    for i in range(N_histos):
        rootfile = rt.TFile(rootname_list[i],"READ")
        histo = rootfile.Get(histo_name_list[i])
        #histo.Draw()
        gROOT.cd()
        histo_clone = histo.Clone()
        # Scale the histogram
        scale_factor = float(scales_list[i])/(nfiles_list[i]*2500)
        scale_factor_list.append(scale_factor)
        histo_clone.Sumw2()
        histo_clone.Scale(scale_factor)
        if rebin != 0:
            if type(rebin) == int:
                histo_clone.Rebin(rebin)
            elif type(rebin) == list:
                histo_clone.Rebin(len(rebin)-1, hnew, rebin)
                histo_clone = hnew
        histo_clone.SetLineWidth(2)
        histo_clone.SetLineColor(fillcolours[i % len(fillcolours)])
        histo_clone.SetLineStyle(1)
        histo_clone.SetFillColor(fillcolours[i % len(fillcolours)])
        histo_clone.SetFillStyle(fillstyles[i % len(fillstyles)])
        if i == 0:
            x_axis = histo_clone.GetXaxis()
            x_min = x_axis.GetXmin()
            x_max = x_axis.GetXmax()
            n_bins = x_axis.GetNbins()
            width = math.fabs(x_max - x_min) / (n_bins)
        # Handle the Legend histogram: save the used histograms into a list, MUST COPY THEM!!!!!
        histo_list.append(copy(histo_clone))
        # Finally add to the stack
        stack.Add(histo_clone)
        
    # Fill legend:
    histo_list.reverse()
    for i,histo in enumerate(histo_list):
        legend.AddEntry(histo, legend_list[N_histos-i-1],'f')
    
    if stack_option == "":
        stack.Draw("HIST")
    else:
        stack.Draw(stack_option+" HIST")
        
    ################## STYLE CUSTOMISATION ###################
    # Hide the stat box
    rt.gStyle.SetOptStat(0)
    # Remove title
    stack.SetTitle("")
    
    # Label axes nicely
    stack.GetXaxis().SetTitle("")
    stack.GetYaxis().SetTitle(ylabel)
    
    
    #Change axis title sizes before updating
    stack.GetXaxis().SetTitleSize(0) #default size = 0.035
    stack.GetXaxis().SetLabelSize(0)
    stack.GetXaxis().SetTitleFont(42)
    stack.GetXaxis().SetTitleOffset(1)
    stack.GetYaxis().SetTitleSize(0.055) #default size = 0.035
    stack.GetYaxis().SetTitleFont(42)
    stack.GetYaxis().SetTitleOffset(0.8)
    stack.GetYaxis().SetLabelSize(0.055)
    canvas.Update()

    # make room for the legend
    y_factor = 1.25
    if "y" in log.lower():
        y_factor = 20
    yMax = stack.GetMaximum()*y_factor
    stack.SetMaximum(yMax)
    if "y" not in log.lower(): 
        stack.SetMinimum(0.01)
    if "y" in log.lower():
        stack.SetMinimum(0.2)
    
    # Set Y-axis to log scale
    if "y" in log.lower():
        rt.gPad.SetLogy()
    # Set X-axis to log scale
    if "x" in log.lower():
        rt.gPad.SetLogx()
        
    legend.Draw()
    canvas.Update()
    
    ################## RATIOPLOT ###################
    ratiopad.cd()
    # Grab histo and clone for reference
#    ref_file = rt.TFile(rootname_list[ref_ratio_index],"READ")
#    ref_histo1 = ref_file.Get(histo_name_list[ref_ratio_index])
#    ref_histo = ref_histo1.Clone()
    # Create another stack plot for the ratio where you add the entries after modifying according to the mode
    stack_ratio = rt.THStack("stack_ratio","")
    
#    if rebin != 0:
#            if type(rebin) == int:
#                ref_histo.Rebin(rebin)
#            elif type(rebin) == list:
#                ref_histo.Rebin(len(rebin)-1, hnew, rebin)
#                ref_histo = hnew
    
    
    for i in range(N_histos):
        if i != ref_ratio_index:
            #print i
            
            # Grab reference histo
            ref_file = rt.TFile(rootname_list[ref_ratio_index],"READ")
            ref_histo1 = ref_file.Get(histo_name_list[ref_ratio_index])
            ref_histo = ref_histo1.Clone()
            ref_histo.Sumw2()
            ref_histo.Scale(scale_factor_list[ref_ratio_index])
            
            # grab compare histo and contents
            comp_file = rt.TFile(rootname_list[i],"READ")
            comp_histo1 = comp_file.Get(histo_name_list[i])
            gROOT.cd()
            comp_histo = comp_histo1.Clone()
            comp_histo.Sumw2()
            comp_histo.Scale(scale_factor_list[i])
            if rebin != 0:
                if type(rebin) == int:
                    comp_histo.Rebin(rebin)
                    ref_histo.Rebin(rebin)
                elif type(rebin) == list:
                    comp_histo.Rebin(len(rebin)-1, hnew, rebin)
                    comp_histo = hnew
            
            # Now scale the histograms
            
            if ratiomode == "divide":
                comp_histo.Divide(ref_histo)
                line_height = 1
                range_yaxis = (0.01, 1.5)
            elif ratiomode == "diff":
                comp_histo.Add(ref_histo, -1.)
                line_height = 0
            elif ratiomode == "fraction":
                comp_histo.Add(ref_histo, -1.)
                comp_histo.Divide(ref_histo)
                line_height = 0
                range_yaxis = (-1.2, 1.2)
            else: 
                print "PLEASE SELECT A RATIOMODE: try: divide, diff, fraction"
            
            comp_histo.SetMarkerStyle(24+i)
            comp_histo.SetMarkerSize(0.4)
            comp_histo.SetMarkerColor(fillcolours[i % len(fillcolours)])
            comp_histo.SetLineColor(fillcolours[i % len(fillcolours)])
            
            
            
            if ratiomode is not None:
                #print "Adding to stack"
                stack_ratio.Add(comp_histo.Clone())
            
    # Now make nice stack options:
    ratiopad.cd()
    stack_ratio.Draw("ep nostack")
    
    # Remove title
    stack_ratio.SetTitle("")
    
    # Label axes nicely
    stack_ratio.GetXaxis().SetTitle(xlabel)
    stack_ratio.GetYaxis().SetTitle(ylabel_ratio)
    
    stack_ratio.GetXaxis().SetLabelSize(0.13)
    stack_ratio.GetXaxis().SetTitleSize(0.13)
    stack_ratio.GetXaxis().SetTitleFont(42)
    stack_ratio.GetXaxis().SetTitleOffset(0.9)
    stack_ratio.GetYaxis().SetLabelSize(0.1)
    stack_ratio.GetYaxis().SetTitleSize(0.13)
    stack_ratio.GetYaxis().SetTitleOffset(0.33)
    stack_ratio.GetYaxis().SetTitleFont(42)
    stack_ratio.GetYaxis().SetNdivisions(8)
    
    if ratiomode == "divide" or ratiomode == "fraction":
        #print "Setting the Y axis range"
        stack_ratio.SetMinimum(range_yaxis[0])
        stack_ratio.SetMaximum(range_yaxis[1])
    
    ratiopad.Update()
    
    # Draw a reference line to help visualise:
    line = rt.TLine(x_min, line_height, x_max, line_height)
    line.SetLineColor(rt.kBlack)
    line.SetLineWidth(2)
    line.Draw("same")
    
    
    ################## SAVE FILES ###################
    canvas.Update()
    
    
    ################## TLATEX #########################
    canvas.cd()
    latex = rt.TLatex()
    #print latex_text
    latex.SetTextAlign(13) # top aligned
    latex.SetTextSize(0.034)
    if latex_corner == "topleft":
        latex.DrawLatexNDC(.14,0.88,latex_text)
    elif latex_corner == "center" or latex_corner == "centre":
        latex.DrawLatexNDC(0.35,0.85,latex_text)
    elif latex_corner == "topright":
        latex.DrawLatexNDC(0.65,0.85,latex_text)
    else:
        print "layered_histos: latex_corner variable not recognised: TRY topleft, centre, topright"
    
    canvas.Update()
    ################## SAVE FILES ###################
    #canvas.SaveAs(output_file[:-4]+"_ratio.png")
    canvas.SaveAs(output_file[:-4]+"_ratio.pdf")
    canvas.SaveAs(output_file[:-4]+"_ratio.root")
    return 0
    
    
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
###########################NO RATIO ###################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
    
    

def save_thstack_to_image_noratio(rootname_list, nfiles_list,scales_list,histo_name_list,legend_list,legend_spot, output_file,xlabel,ylabel,fillcolours,fillstyles, log = "", stack_option = "", rebin = 0, latex_text = "", latex_corner = "topleft", legend_title = ""):


    rt.TGaxis.SetMaxDigits(3)
    N_histos = len(rootname_list)
    # If the histo_name_list is given as a string of 1 histo_name create a list containing that name N_histos times
    if type(histo_name_list) == str:
        histo_name_list = [histo_name_list]*N_histos
    
    ################## PADS & CANVAS ###################
    # Create a canvas, pad, legend and stack:
    gROOT.SetBatch(1)
    canvas = rt.TCanvas("canvas","canvas", 700, 525)
    mainpad = rt.TPad("mainpad","mainpad",0,0.05,1,1)
    #canvas.cd()
    mainpad.Draw()
    mainpad.SetTopMargin(0.08)
    mainpad.SetBottomMargin(0.10)
    mainpad.cd()
    mainpad.SetTicks(1)
    mainpad.Update()
    
    ################## STACK & LEGEND ###################
    stack = rt.THStack("stack","")
    rt.gStyle.SetLegendFont(42)
    if legend_spot == "topleft":
        legend = rt.TLegend(0.1, 0.71, 0.23, 0.88)
    elif legend_spot == "topright":
        legend = rt.TLegend(0.68, 0.71, 0.87, 0.88)
    else:
        #default is top left
        legend = rt.TLegend(0.1, 0.71, 0.23, 0.88)
    #legend.SetHeader(legend_title+stack_option,"C")
    legend.SetTextSize(0.035)
    legend.SetBorderSize(0)
    
    ################## FILL USING HISTO FROM FILES ###################
    histo_list = []
    for i in range(N_histos):
        print rootname_list[i], histo_name_list[i]
        rootfile = rt.TFile(rootname_list[i],"READ")
        histo = rootfile.Get(histo_name_list[i])
        gROOT.cd()
        histo_clone = histo.Clone()
        # Scale the histogram
        print rootname_list[i],nfiles_list[i]*2500,scales_list[i]
        scale_factor = float(scales_list[i])/(nfiles_list[i]*2500)
        histo_clone.Sumw2()
        histo_clone.Scale(scale_factor)
        if rebin != 0:
            if type(rebin) == int:
                histo_clone.Rebin(rebin)
            elif type(rebin) == list:
                histo_clone.Rebin(len(rebin)-1, hnew, rebin)
                histo_clone = hnew
        histo_clone.SetLineWidth(2)
        histo_clone.SetLineColor(fillcolours[i % len(fillcolours)])
        histo_clone.SetLineStyle(1)
        histo_clone.SetFillColor(fillcolours[i % len(fillcolours)])
        histo_clone.SetFillStyle(fillstyles[i % len(fillstyles)])
        if i == 0:
            x_axis = histo_clone.GetXaxis()
            x_min = x_axis.GetXmin()
            x_max = x_axis.GetXmax()
            n_bins = x_axis.GetNbins()
            width = math.fabs(x_max - x_min) / (n_bins)
        # Handle the Legend histogram: save the used histograms into a list, MUST COPY THEM!!!!!
        histo_list.append(copy(histo_clone))
        # Finally add to the stack
        stack.Add(histo_clone)
        
    # Fill legend:
    histo_list.reverse()
    for i,histo in enumerate(histo_list):
        legend.AddEntry(histo, legend_list[N_histos-i-1],'f')
    
    if stack_option == "":
        stack.Draw("HIST")
    else:
        stack.Draw(stack_option+" HIST")

    ################## STYLE CUSTOMISATION ###################
    # Hide the stat box
    rt.gStyle.SetOptStat(0)
    # Remove title
    stack.SetTitle("")
    
    # Label axes nicely
    stack.GetXaxis().SetTitle(xlabel)
    stack.GetYaxis().SetTitle(ylabel)
    
    
    #Change axis title sizes before updating
    stack.GetXaxis().SetTitleSize(0.04) #default size = 0.035
    stack.GetXaxis().SetLabelSize(0.045)
    stack.GetXaxis().SetTitleFont(42)
    stack.GetXaxis().SetTitleOffset(1.05)
    stack.GetYaxis().SetTitleSize(0.055) #default size = 0.035
    stack.GetYaxis().SetTitleFont(42)
    stack.GetYaxis().SetTitleOffset(0.87)
    stack.GetYaxis().SetLabelSize(0.043)
    canvas.Update()
    
    # make room for the legend
    y_factor = 1.25
    if "dR" in output_file:
        y_factor = 0.68
    if "energy" in output_file or "mtop" in output_file:
        y_factor = 0.35
    if "y" in log.lower():
        y_factor = 20
    yMax = stack.GetMaximum()*y_factor
    stack.SetMaximum(yMax)
    if "y" not in log.lower(): 
        stack.SetMinimum(0.01)
    if "y" in log.lower():
        stack.SetMinimum(0.2)
    
    # Set Y-axis to log scale
    if "y" in log.lower():
        rt.gPad.SetLogy()
    # Set X-axis to log scale
    if "x" in log.lower():
        rt.gPad.SetLogx()
        
    legend.Draw()
    canvas.Update()
    
    ################## SAVE FILES ###################
    canvas.Update()
    
    ################## TLATEX #########################
    canvas.cd()
    latex = rt.TLatex()
    #print latex_text
    latex.SetTextAlign(13) # top aligned
    latex.SetTextSize(0.034)
    if latex_corner == "topleft":
        latex.DrawLatexNDC(.14,0.86,latex_text)
    elif latex_corner == "center" or latex_corner == "centre":
        latex.DrawLatexNDC(0.35,0.86,latex_text)
    elif latex_corner == "topright":
        latex.DrawLatexNDC(0.65,0.86,latex_text)
    else:
        print "layered_histos: legend_corner variable not recognised: TRY topleft, centre, topright"
    
    canvas.Update()
    ################## SAVE FILES ###################
    canvas.SaveAs(output_file[:-4]+".pdf")
    canvas.SaveAs(output_file[:-4]+".root")
    return 0    


#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
##################### ROC CURVES #######################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################

def prepare_ROC_histos(rootname_list, nfiles_list,scales_list,histo_name_list,index_signal,output_file):
    
    rootfile_out = rt.TFile(output_file, "RECREATE")
    rootfile_out.cd()
    
    for j in range(len(histo_name_list)):
        #print histo_name_list[j]
        ################## FILL USING HISTO FROM FILES ###################
        histo_list = []
        scale_factor_list = []
        for i in range(len(rootname_list)):
            rootfile = rt.TFile(rootname_list[i],"READ")
            #rootfile.Print()
            histo = rootfile.Get(histo_name_list[j])
            histo_clone = histo.Clone()
            # Scale the histogram
            scale_factor = float(scales_list[i])/(nfiles_list[i]*2500)
            scale_factor_list.append(scale_factor)
            histo_clone.Sumw2()
            histo_clone.Scale(scale_factor)
            # Handle the Legend histogram: save the used histograms into a list, MUST COPY THEM!!!!!
            histo_list.append(copy(histo_clone))
        
        # First write to the file the signal:
        rootfile_out.cd()
        histo_list[index_signal].Write(histo_name_list[j]+"_signal")
        # Remove the entry from the list
        del histo_list[index_signal]
        
        #Now use list of histos to add together all BG to histo 0 
        for i in range(len(histo_list)-1):
            histo_list[0].Add(histo_list[i+1],1)
        histo_list[0].Write(histo_name_list[j]+"_background")
        
        
    rootfile_out.Write()
    rootfile_out.Close()
    return 0


    
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
########################### END ######################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
    
    


def get_bin_contents(histo, N):
    list = [None] * (N+2)
    bincenters = list
    for j in range(N):
        list[j+1] = histo.GetBinContent(j+1)
        bincenters[j+1] = histo.GetBinCenter(j+1)
    list[0] = histo.GetBinContent(0)
    bincenters[0] = histo.GetBinCenter(0)
    list[-1] = histo.GetBinContent(N+1)
    bincenters[-1] = histo.GetBinCenter(N+1)
    return (bincenters, list)

########################################################

rootname = 'selection_histograms.root'
sample_dirs = ['splitmtop_1718/','splitmtop_1730/','splitmtop_1742/']
sample_dirs.reverse()
PLOTS_dir = './PLOTS/'
rootname_list = [PLOTS_dir+s+rootname for s in sample_dirs]
ratiomode = "divide"
ref_ratio_index = 1

output_dir = PLOTS_dir+'combined/'

histo_name_iterate = ["histo_tophadRec_cut8","histo_mc_tquark1_m_cut8","histo_whadRec_cut8","histo_mc_w1_m_cut8","histo_jet1_e_cut8","histo_lep1_e_cut8","histo_four_jets_mass_cuts_cut8","histo_total_rec_mass_cut8"]#,"histo__cut8","histo__cut8"]
xlabel_list = ["m_{t}^{rec}", "m_{t}^{MC}", "m_{W}^{rec}", "m_{W}^{MC}", "E_{jet1}", "E_{l}", "E_{4j}", "m_{reconstructed}"]
ylabel_list = ["events"]*len(xlabel_list)
log_list = ["","","","","y","y","y","y"]
stack_option_list = ["nostack"]*len(xlabel_list)
legend_spot = ["topright","topleft","topright","topleft","topright","topright","topright","topright"]

legend_list = ["m_{t} = 171.8 GeV", "m_{t} = 173.0 GeV", "m_{t} = 174.2 GeV"]
legend_list.reverse()


name_list = ["mass_top_reco(3j)", "top_mass_mc", "mass_w_reco(2j)", "w_mass_mc", "jet1_e", "lep1_e", "hadronic_mass_reco(4j)", "total_mass_reco"]
extension = ".png"
output_file_list = [output_dir+s+extension for s in name_list]

j = 4
#save_thstack_to_image(rootname_list, histo_name_iterate[j], legend_list, legend_spot[j], output_file_list[j], xlabel_list[j], ylabel_list[j], log_list[j], stack_option_list[j], ratiomode = ratiomode, ref_ratio_index = ref_ratio_index)#, rebin = 4)

#for j in range(len(xlabel_list)):
    #print rootname_list, histo_name_iterate[j], legend_list, output_file_list[j], xlabel_list[j], ylabel_list[j], log_list[j], stack_option_list[j]
    #save_thstack_to_image(rootname_list, histo_name_iterate[j], legend_list, legend_spot[j], output_file_list[j], xlabel_list[j], ylabel_list[j], log_list[j], stack_option_list[j], ratiomode = ratiomode, ref_ratio_index = ref_ratio_index)



