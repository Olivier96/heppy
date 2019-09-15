#!/usr/bin/env bash

ntuple_subdir=splitmtop/
output_dir=splitmtop/
#GENERATOR=ee_
GENERATOR=ee_ttbar_splitmtop_1730
extension=.root

Nsamples=400

cards=(tt dilep had ww zz hz)
cards_len=${#cards[@]}

for ((j=100; j<Nsamples; j++)); do
    echo sampler: ${j}
    #for ((ic = 0; ic<cards_len; ic++  )); do
        #python sampler_creator.py -o ${GENERATOR}${cards[${ic}]}_${j}_sampler.py -n ${GENERATOR}${cards[${ic}]}_${j}${extension} --output-directory=${cards[${ic}]}/ --ntuple-dir=${cards[${ic}]}/
        python sampler_creator.py -o ${GENERATOR}_${j}_sampler.py -n ${GENERATOR}_${j}${extension} --output-directory=${output_dir} --ntuple-dir=${ntuple_subdir}
    #done
done

