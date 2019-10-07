#!/usr/bin/env bash

SCRIPTS_DIR=heppy/ttbar_analysis/ANALYSIS/PYTHIA/scripts

Nnodes=1
Ncores=2
Njobs=6

cards=(tt dilep had ww zz hz)
cards_len=${#cards[@]}
sqrts=(340 342 344 346 350)
sqrts_len=${#sqrts[@]}

#GENERATOR=ee_
GENERATOR=ee_ttbar_splitmtop_1730
extension=.txt

#ntuple_subdir=splitmtop/
ntuple_subdir=cross_sections/

# Use -v with qsub to export variables to the script! 
# qsub <script.sh> -v param_name=param_value,param_name2=param_value2,...


#for ((j=100; j<Njobs; j++)); do
#    echo job: ${j}
#    #for ((ic = 0; ic<cards_len; ic++  )); do
##        qsub run_ee_ttbar_1card.sh -v GENERATOR=${GENERATOR}${cards[${ic}]}_${j}${extension},subdir=${cards[${ic}]}/ -lnodes=${Nnodes}:ppn=${Ncores} -N ${cards[${ic}]}_${j}
#    echo qsub run_ee_ttbar_1card.sh -v GENERATOR=${GENERATOR}_${j}${extension},subdir=${ntuple_subdir} -lnodes=${Nnodes}:ppn=${Ncores} -N job_${j}
#        sleep 0.25
#    #done
#done

for ((i = 3; i<Njobs; i++)); do
    for ((j = 0; j<sqrts_len; j++)); do
        s=${sqrts[j]}
        c=${cards[i]}
        filename=${c}_${s}.txt
        echo sending card ${c}, sqrts ${s}
        #for ((ic = 0; ic<cards_len; ic++  )); do
        #python card_creator.py -o ${filename} -m ${mtop} -W ${topwidth} -N ${Nevents} -E ${s}
        qsub run_ee_ttbar_1card.sh -v GENERATOR=${filename},subdir=${nutple_subdir} -lnodes=${Nnodes}:ppn=${Ncores} -N ${filename}
            #echo python card_creator.py -o ee_${cards[${ic}]}_${i}.txt -m ${mtop} -W ${topwidth} -N ${Nevents} -E ${sqrts} -c ${cards[${ic}]}
        #done
    done
done




