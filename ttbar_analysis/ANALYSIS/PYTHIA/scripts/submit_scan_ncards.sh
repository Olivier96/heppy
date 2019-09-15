#!/usr/bin/env bash

SCRIPTS_DIR=~/testFCC/Nicolo/heppy/ttbar_analysis/ANALYSIS/PYTHIA/scripts

Nnodes=1
Ncores=1
Njobs=45


mtop=(171.8 172.6 173.0 173.4 174.2)
mtop_len=${#mtop[@]}
mtop_central_idx=2
sqrts=(340 342 344 346 350)
sqrts_len=${#sqrts[@]}
sqrts_central_idx=2
cards=(tt dilep had ww zz hz)
cards_len=${#cards[@]}

# Use -v with qsub to export variables to the script! 
# qsub <script.sh> -v param_name=param_value,param_name2=param_value2,...

ii=0
for ((i = 0; i<Njobs; i++)); do
    echo card number ${i}
    for ((is = 0; is <sqrts_len; is++)); do
        for ((im = 0; im<mtop_len; im++)); do
            m=${mtop[im]}
            s=${sqrts[is]}
            if [[ im -eq mtop_central_idx ]]; then
                for ((ic = 0; ic<cards_len; ic++  )); do
                    c=${cards[${ic}]}
                    ii=$((${ii} + 1))
                    #python card_creator.py -o ${c}_${m}_${s}_${i}.txt -m ${m} -W ${topwidth} -N ${Nevents} -E ${s} -c ${c}
                    qsub run_ee_ttbar_1card.sh -v GENERATOR=${c}_${m}_${s}_${i}.txt,subdir=m${m}_s${s}/  -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m}_${s}_${i}
                    sleep 0.3
                done
            else
                c=tt
                #python card_creator.py -o ${c}_${m}_${s}_${i}.txt -m ${m} -W ${topwidth} -N ${Nevents} -E ${s} -c ${c}
                qsub run_ee_ttbar_1card.sh -v GENERATOR=${c}_${m}_${s}_${i}.txt,subdir=m${m}_s${s}/  -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m}_${s}_${i}
                sleep 0.3
                ii=$((${ii} + 1))
            fi
        done
    done
done
echo ${ii}







