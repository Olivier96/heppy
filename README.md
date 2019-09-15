# fcc_ttbar

This code is based on the heppy repository made by Colin Bernet: https://github.com/cbernet/heppy

The ttbar project was started by Nicolò Foppiani: https://github.com/nfoppiani/heppy

The general structure of the project is as follows:
Modules are created in the analzers/ directory,
then called in various sequences in the sequences/ directory.
Finally the sequences are used in the analysis found in the ttbar_analysis/ directory.

Inside ttbar_analysis:

1) Produce a pythia file inside ANALYSIS/PYTHIA using the scripts card_creator.py and create_ncards.py. The cards use a text file template found in ntuple_generator_copies and produces copies there with the settings from the python scripts.
2) The ntuples can ce submitted using the script submit_ncards.sh and are output into the ntuples/ directory.
3) Move the logfiles into the directory scripts/logfiles.
4) Create a python sampler by running the create_nsamplers.py and sampler_creator.py scripts inside python_samplers/.
5) Go back to the ttbar_analysis dir
6) Use scripts/ to produce an analysis python file by running the analysis_creator.py, or use create_nanalysis.py to produce multiple. 
7) These are put into the CONFIGS/ directory where they can be submitted to the IIHE cluster using submit_nanalysis.sh.
8) The output from the analysis can be found in the ANALYSIS/OUT/ directory.

You now have data ready to analyse and produce plots.

A bunch of useful python scripts for ROOT can be found in the ttbar_analysis/ANALYSIS/ directory.

-chain_loop: produce ROOT histograms of the data passing through the chi2 analysis
-collect_trees: move files into convenient locations, also contains all calls necessary for steps 1-8 above inside comments to give an overview
-cut_flow: produce a cut flow table after the chain_loop is executed, this part does the logic
-generate_scales: gathers the amount of events in order to scale the data, can also be used to get cross-section values for different top quark masses
-get_chain: Obtain a ROOT TChain object from root files
-layered_histos: Produce nice looking stacked histograms figures using functions provided
-nice_graphs: Produce nice looking graphs, also contains a few specific functions for cross-section plots at the end
-nice_histo: Produce a single histogram figure
-nice_table: Produce tables for latex documents, also contains the functions to produce other relevant tables: yield, purity, cut_flow, statistical uncertainty on cross section, efficiency

-scan_selection: This is a large file that was used to produce the full analysis presented in the thesis see at the top. This file makes use of all the helper files mentioned above. It is self documented but a bit messy. I would recommend looking at it only as a guide in order to see how to call the useful helper functions. 

deprecated:
-CHAIN
-CHAIN2
-chain_simple
-chain_selection
-histo_properties




