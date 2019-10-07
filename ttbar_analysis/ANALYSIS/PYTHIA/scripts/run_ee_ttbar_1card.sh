#!/usr/bin/env bash


# Code to add GENERATOR parameter as a parser command! use: ./run_ee_ttbar1card.sh -i <generator.txt>
#while [[ "$#" -gt 0 ]]; do case $1 in
#  -i|--input) GENERATOR="$2"; shift;;
#  *) echo "Unknown parameter passed: $1"; exit 1;;
#esac; shift; done

echo ${GENERATOR}
echo ${subdir}

NTUPLE_DIR=heppy/ttbar_analysis/ANALYSIS/PYTHIA/ntuples
NTUPLE_GEN_DIR=heppy/ttbar_analysis/ANALYSIS/PYTHIA/ntuples_generator_copies
#GENERATOR=ee_tt_0.txt
#subdir=ee/
ROOTNAME=${GENERATOR}

mkdir -p ${NTUPLE_DIR}/${subdir}

echo "sourcing FCCSW 0.8 (gen)"
source /cvmfs/fcc.cern.ch/sw/0.8.1/init_fcc_stack.sh

echo "Copy the generator file from the Ntuple generator directory to the Ntuple directory"
cp ${NTUPLE_GEN_DIR}/${GENERATOR} ${NTUPLE_DIR}/${subdir}${ROOTNAME}

echo "Go to Ntuple directory"
cd ${NTUPLE_DIR}/${subdir}

echo "Running the pythia ${GENERATOR} gen_card"
fcc-pythia8-generate ${GENERATOR}

echo "Remove gen_card from the Ntuples directory"
rm ${GENERATOR}

echo "All done, ROOT file succesfully produced!"

