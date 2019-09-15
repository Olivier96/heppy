#from ROOT import gROOT, TCanvas, TF1, TGraph, TFile, TH1F,TMath
import ROOT as rt
from copy import copy
from math import sqrt
from numpy import arange
from generate_scales import cross_graph_coords


#gROOT.Reset()

# load histograms from file
#file = TFile("in.root","read")
#histo1 = file.Get("histo1")
#histo2 = file.Get("histo2")

# backup: random histograms with random data in there, chosen to have very different distributions
#histo1 = TH1F("histo1","",100,0,10)
#histo2 = histo1.Clone("histo2")
#func1 = TF1("func1","TMath::DiLog(x)",0,10)
#func2 = TF1("func2","x*x",0,10)
#histo1.FillRandom("func1",10000)
#histo2.FillRandom("func2",10000)


def produce_ROC_graph(histo_signal,histo_background,efficiency_bg,larger_than = True):
    nbins = histo_signal.GetNbinsX()
    tgraphcomb = rt.TGraph()
    tgraph_statcross = rt.TGraph()
    print "Histogram: {}".format(histo_signal.GetName())

    if histo_signal.GetEntries()==0 :
        return None
    if histo_background.GetEntries()==0 :
        return None
    # for loop that does integration:
    ibinwork=0
    ibinwork2 = 0
    efficiency_reached = False
    display_statcross  = False
    bgstart=histo_background.Integral(0,nbins+1)
    sigstart=histo_signal.Integral(0,nbins+1)
    print bgstart,sigstart
    for ibin in range(1,nbins+1):
        # heavily reliant on TH1D::Integral(Int_t binx1, Int_t binx2, Option_t *option). Simple modification that also includes errors would mean using TH1D::IntegralAndError()
        if larger_than:
            # Need to check if this is correct!
            # Voor var > x
            bgend=histo_background.Integral(ibin,nbins+1)
            sigend=histo_signal.Integral(ibin,nbins+1)
        else:
            # Voor var < x:
            bgend=histo_background.Integral(0,ibin-1)
            sigend=histo_signal.Integral(0,ibin-1)
        # debugging printout:
        #print ibin,ibinwork,"high edge:",histo_signal.GetBinLowEdge(ibinwork+1),bgend,sigend,bgend/bgstart,sigend/sigstart
        if abs(bgstart*sigstart) > 0 :
            # nu voor chi2 < x
            if ((not efficiency_reached) and (bgend/bgstart)>efficiency_bg):
                print "Reach desired background efficiency {}% at bin-highedge: {}, bin {}".format(efficiency_bg*100,histo_signal.GetBinLowEdge(ibinwork+1),ibinwork)
                efficiency_reached = True
                display_statcross = True
            tgraphcomb.SetPoint(ibinwork,bgend/bgstart,sigend/sigstart)
            if sigend/sigstart >0:
                cross = ((bgend+float(sigend))-float(bgend))/((float(sigend)/sigstart)*0.2*0.44) # L_int = 0.2ab-1, BR semilep = 0.44, bgend+sigend = Ntot, Nbg = bgend 
                dcross = 1/((float(sigend)/sigstart)*0.2*0.44)
                sigcross = sqrt(  ((dcross**2)*(bgend+float(sigend))) +    ((dcross**2)*float(bgend))    )
                statcross_percent = (float(sigcross)/cross)*100.
                if display_statcross:
                    print "At the cut the stat relative crosssection: {:.3} %".format(statcross_percent)
                    display_statcross = False
                tgraph_statcross.SetPoint(ibinwork2,histo_signal.GetBinLowEdge(ibinwork2+1),statcross_percent)
                #print "Cross section {} +- {} ab, stat only".format(cross,sigcross)
                #print "Fractional uncertainty {:.3} %".format((sigcross/cross)*100)
                ibinwork2 += 1
            ibinwork+=1
    print "Signal efficiency at {}% background: {}".format(efficiency_bg*100,tgraphcomb.Eval(efficiency_bg))
    print ""
    return [copy(tgraphcomb),copy(tgraph_statcross)]
    #raw_input("press something to continue")
    # additional graph is in the same canvas you draw with only the "l" option, e.g., tgraph2.Draw("l")


def stack_graphs(output_file,graph_list, legend_list,legend_spot, xlabel,ylabel,linecolour_list,xlim,ylim, graph_options = "la",log = "", markers = False, draw_legend = True):
    rt.TGaxis.SetMaxDigits(3)
    rt.gStyle.SetOptStat(0)
    
    # create canvas and pad
    canvas = rt.TCanvas("canvas","canvas",700,525)
    pad = rt.TPad("pad","pad",0,0.05,1,1)
    pad.Draw()
    pad.SetTopMargin(0.08)
    pad.SetBottomMargin(0.10)
#    pad.SetGrid()
    pad.cd()
    pad.SetTicks(1)
    pad.Update()
    
    # Create a legend
    if draw_legend:
        rt.gStyle.SetLegendFont(42)
        if legend_spot == "topleft":
            legend = rt.TLegend(0.15, 0.71, 0.36, 0.88)
        elif legend_spot == "topright":
            legend = rt.TLegend(0.6, 0.71, 0.87, 0.88)
        elif legend_spot == "bottomright":
            legend = rt.TLegend(0.74,0.14,0.87,0.3)
        elif legend_spot == "bottomright_big":
            legend = rt.TLegend(0.68, 0.14, 0.87, 0.4)
        else:
            #default is top left
            legend = rt.TLegend(0.1, 0.71, 0.23, 0.88)
        #legend.SetHeader(legend_title+stack_option,"C")
        legend.SetTextSize(0.035)
        #legend.SetBorderSize(0)
    
    # create multigraphs
    mg = rt.TMultiGraph()
    
    # Fill the multigraph:
    for i in range(len(graph_list)):
        #print mg,graph_list[i]
        graph_list[i].SetLineWidth(2)
        graph_list[i].SetLineColor(linecolour_list[i % len(linecolour_list)])
        if markers:
            graph_list[i].SetMarkerColor(linecolour_list[i % len(linecolour_list)])
            if graph_options == "cross2":
                if i == 0:
                    graph_list[i].SetMarkerStyle(1)
                    graph_list[i].SetMarkerSize(3*graph_list[i].GetMarkerSize())
                else:
                    graph_list[i].SetMarkerStyle(20+i)
            else:
                graph_list[i].SetMarkerStyle(20+i)
        mg.Add(copy(graph_list[i]))
        if draw_legend:
            legend.AddEntry(graph_list[i],legend_list[i],'p')
    
    #print mg
    if graph_options == "cross2":
        mg.Draw("ap")
    else:
        mg.Draw(graph_options)
    if draw_legend:
        legend.Draw()
    canvas.Update()
    canvas.cd()
    
    ndiv = 210
    # x-axis
    mg.GetXaxis().SetTitle(xlabel)
    mg.GetXaxis().SetLimits(xlim[0],xlim[1])
    mg.GetXaxis().SetNdivisions(ndiv)
    mg.GetXaxis().SetTitleSize(0.051)
    mg.GetXaxis().SetLabelSize(0.042)
    mg.GetXaxis().SetTitleFont(42)
    mg.GetXaxis().SetTitleOffset(0.84)
    # y-axis
    mg.GetYaxis().SetTitle(ylabel)
    mg.GetYaxis().SetNdivisions(ndiv)
    mg.GetYaxis().SetTitleOffset(0.93)
    mg.GetYaxis().SetTitleFont(42)
    mg.GetYaxis().SetLabelSize(0.042)
    mg.GetYaxis().SetTitleSize(0.0525)
    mg.SetMinimum(ylim[0])
    mg.SetMaximum(ylim[1])
    canvas.Update()
    
    
    pad.cd()
    if "y" in log.lower():
        pad.SetLogy()
    
    canvas.cd()
    canvas.Update()
    
    ################## TLATEX #########################
#    canvas.cd()
#    latex = rt.TLatex()
#    #print latex_text
#    latex.SetTextAlign(13) # top aligned
#    latex.SetTextSize(0.034)
#    if latex_corner == "topleft":
#        latex.DrawLatexNDC(.14,0.86,latex_text)
#    elif latex_corner == "center" or latex_corner == "centre":
#        latex.DrawLatexNDC(0.35,0.86,latex_text)
#    elif latex_corner == "topright":
#        latex.DrawLatexNDC(0.65,0.86,latex_text)
#    else:
#        print "layered_histos: legend_corner variable not recognised: TRY topleft, centre, topright"
    
    canvas.SaveAs(output_file[:-4]+".pdf")
    canvas.SaveAs(output_file[:-4]+".root")
    
    return 0


def prepare_ROC_graphs(root_filename,signal_list,background_list,efficiency_bg,output_file, legend_list,legend_spot, xlabel,ylabel,linecolour_list,xlim,ylim, graph_options = "la",larger_than = True):
    
    rootfile = rt.TFile(root_filename,"READ")
    graph_list = []
    graph_cross_list = []
    for i in range(len(signal_list)):
        histo_signal = rootfile.Get(signal_list[i])
        histo_signal = histo_signal.Clone()
        histo_background = rootfile.Get(background_list[i])
        histo_background = histo_background.Clone()
        graph_temp = produce_ROC_graph(copy(histo_signal),copy(histo_background),efficiency_bg,larger_than)
        if graph_temp is not None:
            graph_list.append(graph_temp[0])
            graph_cross_list.append(graph_temp[1])
    
    stack_graphs(output_file,graph_list, legend_list,legend_spot, xlabel,ylabel,linecolour_list,xlim,ylim, graph_options=graph_options)
    
    xlabel_cross = "#chi^{2}_{cut}"
    ylabel_cross = "#Delta#sigma/#sigma     (%)"
    xlim_cross = (0,150)
    ylim_cross = (0,12)
    output_file_cross = output_file[:-4]+"_cross.pdf"
    xlim_cross_zoom = (0,8)
    output_file_cross_zoom = output_file[:-4]+"_cross_zoom.pdf"
    
    stack_graphs(output_file_cross,graph_cross_list, legend_list,legend_spot, xlabel_cross,ylabel_cross,linecolour_list,xlim_cross,ylim_cross, graph_options=graph_options)
    stack_graphs(output_file_cross_zoom,graph_cross_list, legend_list,legend_spot, xlabel_cross,ylabel_cross,linecolour_list,xlim_cross_zoom,ylim_cross, graph_options=graph_options)

    return 0




def make_graphs_pythia(output_pythia):
    
    sqrts = [340,342,344,346,350]
    
    # Following cross sections taken from pyhtia log files, all in milibarn
    cross_ttbar   = [1.405e-11,1.903e-11,2.916e-11,5.949e-11,1.722e-10]
    errors_ttbar  = [1.487e-14,2.18e-14,4.96e-14,1.112e-13,2.146e-13]
    cross_ww      = [1.205e-8,1.196e-8,1.193e-8,1.185e-8,1.171e-8]
    errors_ww     = [1.439e-11,1.423e-11,1.424e-11,1.411e-11,1.398e-11]
    cross_zz        = [9.328e-10,9.258e-10,9.172e-10,9.128e-10,8.987e-10]
    errors_zz       = [1.021e-12,1.012e-12,1.003e-12,9.949e-13,9.798e-13]
    cross_hz        = [1.48e-10,1.467e-10,1.453e-10,1.435e-10,1.406e-10]
    errors_hz       = [2.136e-13,2.116e-13,2.098e-13,2.084e-13,2.037e-13]
    
    # convert to femtobarn
    conversion = 1e12
    for i in range(5):  
        cross_ttbar[i] *= conversion 
        errors_ttbar[i] *= conversion 
        cross_ww[i] *= conversion    
        errors_ww[i] *= conversion   
        cross_zz[i] *= conversion      
        errors_zz[i] *= conversion     
        cross_hz[i] *= conversion      
        errors_hz[i] *= conversion     
    
    xlim_sqrts = [338,352] 
    ylim_cross =  [2,2e4]
    markers = True
    
    TT = rt.TGraphErrors()
    WW = rt.TGraphErrors()
    ZZ = rt.TGraphErrors()
    HZ = rt.TGraphErrors()
    
    for i in range(5):
        TT.SetPoint(i,sqrts[i],cross_ttbar[i])
        TT.SetPointError(i,0,errors_ttbar[i])
        WW.SetPoint(i,sqrts[i],cross_ww[i])
        WW.SetPointError(i,0,errors_ww[i])
        ZZ.SetPoint(i,sqrts[i],cross_zz[i])
        ZZ.SetPointError(i,0,errors_zz[i])
        HZ.SetPoint(i,sqrts[i],cross_hz[i])
        HZ.SetPointError(i,0,errors_hz[i])
    
    graphs = [WW,ZZ,HZ,TT]
    legend_pythia = ["WW","ZZ","HZ","t#bar{t}"]
    legend_pythia_spot = "bottomright"
    xlabel = "#sqrt{s}     (GeV)"
    ylabel = "#sigma_{LO}     (fb)"
    
    pythia_colour = [rt.kBlue,rt.kGreen+1, rt.kRed, rt.kMagenta]
    
    stack_graphs(output_pythia,graphs,legend_pythia,legend_pythia_spot,xlabel,ylabel, pythia_colour,xlim_sqrts,ylim_cross,graph_options = "lap",log="y",markers = markers)
    
    return 0



def make_cross_plot():
    
    sqrts = [340,342,344,346,350]
    
    
     #mtop = 1730 column  for the next numbers
    N_sig = [104,505,1183,3653,4404] # yields
    purity = [0.076, 0.3148, 0.5356, 0.7686, 0.7904]
    eff = [0.1011, 0.1033, 0.1007, 0.1016, 0.0953]
    L_int = 0.2 # ab-1
    BR = 0.438
    
    # in ab:
    cross = [None]*5
    sig_cross = [None]*5
    cross_graph = rt.TGraphErrors()
    
    #conversion to femtobarn:
    conversion = 1e-3
    for i in range(len(N_sig)):
        N_tot = N_sig[i]/purity[i]
        N_bg = N_tot - N_sig[i]
        cross[i] = ((float(N_tot) - N_bg)/(eff[i] * L_int*BR))*conversion
        dcross = 1/(eff[i] * L_int*BR)
        sig_cross[i] = (sqrt( ((dcross**2) *(N_tot)) +( ((-dcross)**2)*(N_bg))  ))*conversion
#        print cross[i],sig_cross[i]
        cross_graph.SetPoint(i,sqrts[i],cross[i])
        cross_graph.SetPointError(i,0,sig_cross[i])
    
    legend = ["t#bar{t}"]
    xlabel = "#sqrt{s}     (GeV)"
    ylabel = "#sigma     (fb)"
    xlim_sqrts = [339,352] 
    ylim = [.1,820]
    markers = True
    colour = [rt.kRed]
    graphs = [cross_graph]
    output_cross = "PLOTS/cross.pdf"
    
#    stack_graphs(output_cross,graphs,legend,"topright",xlabel,ylabel,colour,xlim_sqrts,ylim,graph_options = "lap",log="",markers = markers, draw_legend = False)
    
    
    coords_173 = cross_graph_coords(173)
    graph_173 = rt.TGraph()
    for i in range(len(coords_173[0])):
        graph_173.SetPoint(i,coords_173[0][i],coords_173[1][i] * 1000)
#    print cross_graph.Print()
#    print cross_pred_graph.Print()
    
    output_cross2 = "PLOTS/cross2.pdf"
    legend_pred = ["arXiv:1611.03399","Measurement"]
    colour = [rt.kBlue,rt.kRed]
    graphs = [graph_173,cross_graph]
    
    stack_graphs(output_cross2,graphs,legend_pred,"topright",xlabel,ylabel,colour,xlim_sqrts,ylim,graph_options = "cross2",log="",markers = markers, draw_legend = True)
    
    return 0

make_cross_plot()

def make_cross_method_plot():
    coords_1715 = cross_graph_coords(171.5)
    graph_1715 = rt.TGraph()
    coords_173 = cross_graph_coords(173)
    graph_173 = rt.TGraph()
    coords_1742 = cross_graph_coords(174.2)
    graph_1742 = rt.TGraph()
    for i in range(len(coords_1742[0])):
        if i < len(coords_1715[0]):
            graph_1715.SetPoint(i,coords_1715[0][i],coords_1715[1][i] * 1000)
        if i < len(coords_173[0]):
            graph_173.SetPoint(i,coords_173[0][i],coords_173[1][i] * 1000)
        graph_1742.SetPoint(i,coords_1742[0][i],coords_1742[1][i] * 1000)
    
    graph_list = [graph_1715, graph_173, graph_1742]
    
    xlabel = "#sqrt{s}     (GeV)"
    ylabel = "#sigma     (fb)"
    xlim_sqrts = [339,352] 
    ylim = [0,820]
    
    stack_graphs("PLOTS/cross_method.pdf",graph_list, ["m_{t} = 171.5 GeV","m_{t} = 173.0 GeV","m_{t} = 174.2 GeV"], "topleft",xlabel,ylabel,[rt.kBlue,rt.kRed,rt.kGreen], xlim_sqrts,ylim, draw_legend = True)
    
    return 0

#make_cross_method_plot()


