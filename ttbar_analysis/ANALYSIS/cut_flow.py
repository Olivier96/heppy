import os, sys
import ROOT as rt
import math
#import math

# Runs a script to extract the cut flow values from the chain_selection script

####### DATA SELECTION######################################
distribution = "lep1_e"
# Which distribution you choose will not affect the result, it just needs to be present in the TTree

############### CREATE CUTFLOW FUNCTIONS #####################

# Deprecated 
def get_yield(distribution, path_to_rootfile):
    histo_name = "histo_"+distribution
    rootfile = rt.TFile(path_to_rootfile,"READ")
    # Now get the distributions from the rootfile and store it in a list
    yield_list = []
    histo = rootfile.Get(histo_name+"_nocut")
    # Now add yields using .GetEntries()
    # GetEntries counts overflow and underflow bins as well
    yield_list.append(histo.GetEntries())
    for i in range(8):
        histo = rootfile.Get(histo_name+"_cut"+str(i+1))
        yield_list.append(histo.GetEntries())
    return yield_list

# Deprecated 
def cut_flow(distribution, path_to_rootfile, cuts, filename):
    file = open(filename,"wt")
    yield_Nicolo = [6290, 6277, 6269, 6268, 6267, 6265, 6265, 6258, 5336]
    yield_sample = get_yield(distribution, path_to_rootfile)
    cuts.insert(0,"no cuts")
    header_string = '{:30};{.7};{:.7};{:.7};{:.7};{:.7};{:.7};{:.7};{:.7};{:.7}\n'.format("cuts", "yield_sample", "yield_Nicolo", "eff_sample", "sig_down", "sig_up", "eff_Nicolo", "sig_down", "sig_up",'diff_ratio')
    file.write(header_string)
    for i in range(9):
        if i == 0:
            eff_sample = (float(1),float(0), float(0))
            eff_Nicolo = (float(1),float(0), float(0))
        else:
            eff_sample = efficiency_uncertainty(yield_sample[i],yield_sample[i-1])
            eff_Nicolo = efficiency_uncertainty(yield_Nicolo[i],yield_Nicolo[i-1])
        flow_string = '{cut:<30};{yieldS:<13};{yieldN:<12};{effS:<16};{dnS:<18};{upS:<18};{effN:<16};{dnN:<18};{upN:<18};{diff_ratio:<18}\n'.format(cut=cuts[i],yieldS=yield_sample[i],yieldN=yield_Nicolo[i],effS=eff_sample[0], dnS = eff_sample[1], upS = eff_sample[2], effN = eff_Nicolo[0], dnN = eff_Nicolo[1], upN = eff_Nicolo[2],diff_ratio=(eff_sample[0]-eff_Nicolo[0])/(max(eff_Nicolo[1],eff_Nicolo[2],1)) )
        file.write(flow_string)
    file.close()
    return 0

def efficiency_uncertainty(n,m):
    n = float(n)
    m = float(m)
    eff = n/m
    D = m*m*(1+2.0*n)*(1+2.0*n) - 4.0*m*(1.0+m)*n*n
    pp = (m*(1+2.0*n)+math.sqrt(D)) / (2.0*m*(1.0+m))
    pm = (m*(1+2.0*n)-math.sqrt(D)) / (2.0*m*(1.0+m))
    sig_down = eff - pm
    sig_up = pp - eff
    return (eff, sig_down, sig_up)
   
# Efficiency taken from Freya Blekman, translated from ROOT (in C++)
# for (int i=1;i<=bins;i++){
#    m=htmp_num->GetBinContent(i);
#    n=htmp_den->GetBinContent(i);
#    if(n>0.0) {
#      double D=n*n*(1+2.0*m)*(1+2.0*m) - 4.0*n*(1.0+n)*m*m;
#      pp=( n*(1.0+2.0*m) + sqrt(D) )/(2.0*n*(1.0+n));
#      pm=( n*(1.0+2.0*m) - sqrt(D) )/(2.0*n*(1.0+n));
#      y[i-1]=m/n;
#      eyl[i-1]=(m/n)-pm;
#      eyh[i-1]=pp-(m/n);
#    } else {
#      y[i-1]=0.0;
#      eyl[i-1]=0.0;
#      eyh[i-1]=0.0;
#    }


##########################################################

################## CALL THE FUNCTION FOR SAMPLES #################


#PLOTS_dir = 'PLOTS/'
#rootfile = 'selection_histograms.root'
#cut_file = 'cut_flow.txt'
#
#sample1 = 'had/'
#path1 = PLOTS_dir+sample1+rootfile
#filename = PLOTS_dir+sample1+cut_file
#
#cuts_distributions = ["four_jets_mass > 150", "four_jets_mass < 270", "min_jets_mass > 10", "second_min_jets_mass > 20", "lep1_e < 100", "missing_rec_e > 20", "chi2_top_constrainer <= 40 ", "success == 1"]
#
#cut_flow(distribution, path1, cuts_distributions, filename)

