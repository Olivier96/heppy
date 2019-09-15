#!/usr/bin/env bash

Nnodes=2
Ncores=8


#sampler=ee_
sampler=ee_ttbar_splitmtop_1730
sampler_ext=_sampler.py
sample_dir=splitmtop/
analysis_subdir=splitmtop/

outputfile_ext=_analysis.py

Njobs=400

cards=(tt dilep had ww zz hz)
cards_len=${#cards[@]}

for (( j=100; j<Njobs; j++)); do
    echo analysis: ${j}
    #for ((ic = 0; ic<cards_len; ic++  )); do
        #python analysis_creator.py -s ${sampler}${cards[${ic}]}_${j}${sampler_ext} -N ${Nnodes} -n ${Ncores} -o ${sampler}${cards[${ic}]}_${j}${outputfile_ext} --sample-dir=${cards[${ic}]}/ --output-subdir=${cards[${ic}]}/
    python analysis_creator.py -s ${sampler}_${j}${sampler_ext} -N ${Nnodes} -n ${Ncores} -o ${sampler}_${j}${outputfile_ext} --sample-dir=${sample_dir} --output-subdir=${analysis_subdir}
    #done
done

