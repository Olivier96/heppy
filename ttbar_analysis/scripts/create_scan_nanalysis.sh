#!/usr/bin/env bash

Nnodes=2
Ncores=8

mtop=(171.8 172.6 173.0 173.4 174.2)
mtop_len=${#mtop[@]}
mtop_central_idx=2
sqrts=(340 342 344 346 350)
sqrts_len=${#sqrts[@]}
sqrts_central_idx=2
cards=(tt dilep had ww zz hz)
cards_len=${#cards[@]}


#sampler=ee_
#sampler=ee_ttbar_splitmtop_1730
#sampler_ext=_sampler.py
#sample_dir=splitmtop/
#analysis_subdir=splitmtop/

outputfile_ext=_analysis.py

Njobs=45

cards=(tt dilep had ww zz hz)
cards_len=${#cards[@]}

#for (( j=100; j<Njobs; j++)); do
#    echo analysis: ${j}
#    #for ((ic = 0; ic<cards_len; ic++  )); do
#        #python analysis_creator.py -s ${sampler}${cards[${ic}]}_${j}${sampler_ext} -N ${Nnodes} -n ${Ncores} -o ${sampler}${cards[${ic}]}_${j}${outputfile_ext} --sample-dir=${cards[${ic}]}/ --output-subdir=${cards[${ic}]}/
#    python analysis_creator.py -s ${sampler}_${j}${sampler_ext} -N ${Nnodes} -n ${Ncores} -o ${sampler}_${j}${outputfile_ext} --sample-dir=${sample_dir} --output-subdir=${analysis_subdir}
#    #done
#done

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
                    #qsub run_ee_ttbar_1card.sh -v GENERATOR=${c}_${m}_${s}_${i}.txt,subdir=m${m}_s${s}/  -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m}_${s}_${i}
                    #python sampler_creator.py -o ${c}_${m}_${s}_${i}_sampler.py -n ${c}_${m}_${s}_${i}${extension} --output-directory=m${m}_s${s}/ --ntuple-dir=m${m}_s${s}/
                    python analysis_creator.py -s ${c}_${m/./}_${s}_${i}_sampler.py -N ${Nnodes} -n ${Ncores} -o ${c}_${m}_${s}_${i}${outputfile_ext} --sample-dir=m${m/./}_s${s}/ --output-subdir=m${m}_s${s}/
                done
            else
                c=tt
                #python card_creator.py -o ${c}_${m}_${s}_${i}.txt -m ${m} -W ${topwidth} -N ${Nevents} -E ${s} -c ${c}
                #qsub run_ee_ttbar_1card.sh -v GENERATOR=${c}_${m}_${s}_${i}.txt,subdir=m${m}_s${s}/  -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m}_${s}_${i}
                #python sampler_creator.py -o ${c}_${m}_${s}_${i}_sampler.py -n ${c}_${m}_${s}_${i}${extension} --output-directory=m${m}_s${s}/ --ntuple-dir=m${m}_s${s}/
                python analysis_creator.py -s ${c}_${m/./}_${s}_${i}_sampler.py -N ${Nnodes} -n ${Ncores} -o ${c}_${m}_${s}_${i}${outputfile_ext} --sample-dir=m${m/./}_s${s}/ --output-subdir=m${m}_s${s}/
                ii=$((${ii} + 1))
            fi
        done
    done
done
echo ${ii}






