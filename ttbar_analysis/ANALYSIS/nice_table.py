from copy import copy
import ROOT as rt
from tabulate import tabulate
import numpy as np
from cut_flow import efficiency_uncertainty



def produce_table(table,output_file,header_list=None):
    if header_list is not None:
        latex_table = tabulate(table, tablefmt="latex_raw",headers=header_list)
    else:
        latex_table = tabulate(table, tablefmt="latex")
    
    file= open(output_file,"wt")
    file.write(latex_table)
    file.close()
    
    return 0

def grab_histos_cutflow(histo_files_list,nfiles_list,histo_name,scales_list):
    
    histo_list = []
    for i in range(len(histo_files_list)):
#        print histo_files_list[i]
        rootfile = rt.TFile(histo_files_list[i],"READ")
        h = rootfile.Get(histo_name)
        h = h.Clone()
        h.Sumw2()
        print histo_files_list[i],scales_list[i]
        scale_factor = float(scales_list[i])/(nfiles_list[i]*2500) 
        h.Scale(scale_factor)
        h.Fill(-1,nfiles_list[i]*2500) # -1: Generated events
        h.Fill(0,scales_list[i]) # 0: scaled events
        histo_list.append(copy(h))
    
    return histo_list


def make_cutflow_table(histo_list):
    table = []
    cut_list = ["Generated","Scaled","1 lep \& 4 ptcles","$\mathrm{m}_{\mathrm{4j}}$ > 150","$\mathrm{m}_{\mathrm{4j}}$  < 270","$\mathrm{m}_{\mathrm{2j}}^{\mathrm{min}}$ > 10","$\mathrm{m}_{\mathrm{2j}}^{\mathrm{2nd \: min}}$ > 20", " $\mathrm{E}_{\mathrm{lepton}}$ < 100","$\\not \!\! {E}^{\mathrm{reco}}$ > 20","$\chi^{2}_{4} < 1.35$","$\chi^{2}_{3} < 0.45$","$\chi^{2}_{5} < 1.5$","$\chi^{2}_{Kin}$" ]
    table.append(cut_list)
    list_middle_column = ["",""]
    list_middle_column.extend(["$\pm$"]*11)
    for ih,h in enumerate(histo_list):
        list_values = []
        list_errors = []
        for j in range(-1,8):
            list_values.append(int(h.GetBinContent(j+2)))
            list_errors.append(int(h.GetBinError(j+2)))
        for j in range(10,14):
            list_values.append(int(h.GetBinContent(j+2)))
            list_errors.append(int(h.GetBinError(j+2)))
        list_errors[0]=""
        list_errors[1]=""
        table.append(list_values)
        table.append(list_middle_column)
        table.append(list_errors)
    # Transpose the matrix now:
    table = np.transpose(table)
    return table
    
def make_cutflow_efficiencies(histo_list):
        table = []
        cut_list = ["Generated","Scaled","1 lep \& 4 ptcles","$\mathrm{m}_{\mathrm{4j}}$ > 150","$\mathrm{m}_{\mathrm{4j}}$  < 270","$\mathrm{m}_{\mathrm{2j}}^{\mathrm{min}}$ > 10","$\mathrm{m}_{\mathrm{2j}}^{\mathrm{2nd \: min}}$ > 20", " $\mathrm{E}_{\mathrm{lepton}}$ < 100","$\\not \!\! {E}^{\mathrm{reco}}$ > 20","$\chi^{2}_{4} < 1.35$","$\chi^{2}_{3} < 0.45$","$\chi^{2}_{5} < 1.5$","$\chi^{2}_{Kin}$" ]
        table.append(cut_list)
        for ih,h in enumerate(histo_list):
            list_values = []
            for j in range(-1,8):
                list_values.append(int(h.GetBinContent(j+2)))
            for j in range(10,14):
                list_values.append(int(h.GetBinContent(j+2)))
            
            scaled_events = list_values[1]
            string_list = [list_values[0], list_values[1]]
            for k in range(len(list_values)-2):
                #print list_values[k+2], scaled_events
                eff,sig_dn,sig_up = efficiency_uncertainty(list_values[k+2],scaled_events)
                string_eff = "$%5.4f_{-%5.4f}^{+%5.4f}$"%(eff,sig_dn,sig_up)
                string_list.append(string_eff)
            table.append(string_list)
        table = np.transpose(table)
        return table


def mtop_sqrts_table(semilep_matrix_files, semilep_matrix_nfiles, semilep_matrix_scales, background_list_files, background_list_nfiles, background_list_scales, histo_name,output_table, headers_table):
    
    yield_signal_table_strings = []
    yield_signal_table = []
    yield_signal_error_table = []
    yield_back_list = []
    eff_table = []
    statcross_table = []
    purity_table= []
    
    index_chi2 = 13 # 13 for chi2_3
    
    left_column = ["340","342","344","346","350"]
    
    
    
    for ib,b in enumerate(background_list_files): # ib is the same as iterating over the sqrts values indices
        # Init
        yield_string_list = [left_column[ib]]
        yield_list = [left_column[ib]]
        yield_error_list = [left_column[ib]]
        eff_list = [left_column[ib]]
        statcross_list = [left_column[ib]]
        purity_list = [left_column[ib]]
        back_yield = 0
        
        # Grab backgrounds
        back_histo_list = grab_histos_cutflow(b,background_list_nfiles[ib], histo_name,background_list_scales[ib])
        for h in back_histo_list:
            back_yield += h.GetBinContent(index_chi2)
        yield_back_list.append(back_yield)
        
        signal_histo_list = grab_histos_cutflow(semilep_matrix_files[ib],semilep_matrix_nfiles[ib],histo_name,semilep_matrix_scales[ib])
        for h in signal_histo_list:
            yield_list.append(h.GetBinContent(index_chi2))
            yield_error_list.append(h.GetBinError(index_chi2))
        yield_signal_table.append(yield_list)
        yield_signal_error_table.append(yield_error_list)
        
        
        for i in range(len(yield_list)-1):
            i = i+1
            # Purity
#            print "Purity: ",yield_list[i],yield_list[i]+back_yield,(yield_list[i]/(yield_list[i]+back_yield))
            purity,sig_dn,sig_up = efficiency_uncertainty(yield_list[i],yield_list[i]+back_yield)
#            print purity,sig_dn,sig_up
            purity_string = "$%5.4f_{-%5.4f}^{+%5.4f}$"%(purity,sig_dn,sig_up)
            purity_list.append(purity_string)
            # Efficiency
#            print yield_list[i],semilep_matrix_scales[ib][i-1]
            if semilep_matrix_scales[ib][i-1] == 0:
                eff,sig_dn,sig_up = (0,0,0)
            else:
                eff,sig_dn,sig_up = efficiency_uncertainty(yield_list[i],semilep_matrix_scales[ib][i-1])
            eff_string = "$%5.4f_{-%5.4f}^{+%5.4f}$"%(eff,sig_dn,sig_up)
            eff_list.append(eff_string)
            # Statistical uncertainty 
            if semilep_matrix_scales[ib][i-1] == 0:
                cross = 0
                dcross = 0
            else:
                cross = ((back_yield+float(yield_list[i]))-float(back_yield))/((float(yield_list[i])/semilep_matrix_scales[ib][i-1])*0.2*0.44) # L_int = 0.2ab-1, BR semilep = 0.44, bgend+sigend = Ntot, Nbg = bgend 
                dcross = 1/ ((float(yield_list[i])/semilep_matrix_scales[ib][i-1])*0.2*0.44)
            sigcross = np.sqrt(  ((dcross**2)  * ( back_yield+float(yield_list[i]))   ) +   ( (dcross**2) *float(back_yield))    )
            if semilep_matrix_scales[ib][i-1] == 0:
                statcross_percent = 0
            else:
                statcross_percent = (float(sigcross)/cross)*100.
            statcross_string = "%4.2f"%(statcross_percent)
            statcross_list.append(statcross_string)
            
            # Strings for the yield signal table:
            string_yield = "${} \pm {}$".format(int(yield_list[i]),int(yield_error_list[i])) 
            yield_string_list.append(string_yield)
        
#        print purity_list
        purity_table.append(purity_list)
        yield_signal_table_strings.append(yield_string_list)
        eff_table.append(eff_list)
        statcross_table.append(statcross_list)
        
    
    
    
    # Make the tables
    produce_table(yield_signal_table_strings,output_table[:-4]+"_yield.txt",header_list=headers_table)
    
    produce_table(eff_table,output_table[:-4]+"_eff.txt",header_list=headers_table)
    
    produce_table(purity_table,output_table[:-4]+"_purity.txt",header_list=headers_table)
    
    produce_table(statcross_table,output_table[:-4]+"_statcross.txt",header_list=headers_table)
    
        
        
        
        
            
    

    
    return 0









def full_cutflow_table_to_file(histo_files_list,nfiles_list,histo_name,scales_list,output_file,header_list=None):
    
    histo_list = grab_histos_cutflow(histo_files_list,nfiles_list,histo_name,scales_list)
    table = make_cutflow_table(histo_list)
    produce_table(table,output_file,header_list=header_list)
    
    return 0


def full_cutflow_table_to_file_eff(histo_files_list,nfiles_list,histo_name,scales_list,output_file,header_list=None):
    
    histo_list = grab_histos_cutflow(histo_files_list,nfiles_list,histo_name,scales_list)
    table = make_cutflow_efficiencies(histo_list)
    produce_table(table,output_file,header_list=header_list)
    
    return 0





