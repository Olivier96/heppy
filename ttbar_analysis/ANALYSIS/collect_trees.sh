#!/usr/bin/env bash

# go to out directory
OUT_dir=~/testFCC/Nicolo/heppy/ttbar_analysis/ANALYSIS/OUT/
cd ${OUT_dir}

mtop=(171.8 172.6 173.0 173.4 174.2)
mtop_len=${#mtop[@]}
mtop_central_idx=2
sqrts=(340 342 344 346 350)
sqrts_len=${#sqrts[@]}
sqrts_central_idx=2
cards=(tt dilep had ww zz hz)
cards_len=${#cards[@]}


#tree_dir=ee_ttbar_splitmtop_1730_3_
#tree_dir=
tree_root=tt_semilepton_ILD_Chunk0/heppy.analyzers.tree.TreeTTSemilep.TreeTTSemilep_1/tree.root

Nfiles=1
#collect_dir=chi2_params/

# Create directory of it does not exist:
#if [ ! -d "${collect_dir}" ]; then
#    mkdir ${collect_dir}
#fi
#for ((ic = 0; ic<cards_len; ic++  )); do
#    mkdir -p ${cards[${ic}]}
#done

#for (( j=0; j<Nfiles; j++)); do
#    #for ((ic = 0; ic<cards_len; ic++  )); do
#    cp ${tree_dir}${j}/${tree_root} ${collect_dir}tree_${j}.root
#        #cp ${cards[${ic}]}_${j}/${tree_root} ${cards[${ic}]}/tree_${j}.root
#    #done
#done

ii=0
for ((i = 0; i<Nfiles; i++)); do
    echo trees number ${i}
    for ((is = 0; is <sqrts_len; is++)); do
        for ((im = 0; im<mtop_len; im++)); do
            m=${mtop[im]}
            s=${sqrts[is]}
            if [[ im -eq mtop_central_idx ]]; then
                for ((ic = 0; ic<cards_len; ic++  )); do
                    c=${cards[${ic}]}
                    collect_dir=m${m/./}_s${s}/${c}/
                    ls ${collect_dir} -1v | wc -l
                    echo ${collect_dir}
                    #mkdir -p ${collect_dir}
                    #echo cp ${c}_m${m/./}_s${s}_${i}/${tree_root} ${collect_dir}tree_${i}.root
                    #cp ${c}_m${m/./}_s${s}_${i}/${tree_root} ${collect_dir}tree_${i}.root
                    ii=$((${ii} + 1))
                    #python card_creator.py -o ${c}_${m}_${s}_${i}.txt -m ${m} -W ${topwidth} -N ${Nevents} -E ${s} -c ${c}
                    #qsub run_ee_ttbar_1card.sh -v GENERATOR=${c}_${m}_${s}_${i}.txt,subdir=m${m}_s${s}/  -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m}_${s}_${i}
                    #python sampler_creator.py -o ${c}_${m}_${s}_${i}_sampler.py -n ${c}_${m}_${s}_${i}${extension} --output-directory=m${m}_s${s}/ --ntuple-dir=m${m}_s${s}/
                    #python analysis_creator.py -s ${c}_${m}_${s}_${i}_sampler.py -N ${Nnodes} -n ${Ncores} -o ${c}_${m}_${s}_${i}${outputfile_ext} --sample-dir=m${m}_s${s}/ --output-subdir=m${m}_s${s}/
                    #echo heppy_batch2.py -o ${PATH_TO_OUT}${c}_m${m/./}_s${s}_${i}/  m${m}_s${s}/${c}_${m}_${s}_${i}${analysisfile_ext} -b "qsub ${PATH_TO_OUT}${c}_m${m/./}_s${s}_${i}/tt_semilepton_ILD_Chunk0/batchScript.sh -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m/./}_${s}_${i}"
                    #echo heppy_batch2.py -o ${PATH_TO_OUT}${c}_m${m/./}_s${s}_${i}/  m${m}_s${s}/${c}_${m}_${s}_${i}${analysisfile_ext} -b "qsub batchScript.sh -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m/./}_${s}_${i}" 
                done
            else
                c=tt
                collect_dir=m${m/./}_s${s}/${c}/
                ls ${collect_dir} -1v | wc -l
                echo ${collect_dir}
                #mkdir -p ${collect_dir}
                #cp ${c}_m${m/./}_s${s}_${i}/${tree_root} ${collect_dir}tree_${i}.root
                #python card_creator.py -o ${c}_${m}_${s}_${i}.txt -m ${m} -W ${topwidth} -N ${Nevents} -E ${s} -c ${c}
                #qsub run_ee_ttbar_1card.sh -v GENERATOR=${c}_${m}_${s}_${i}.txt,subdir=m${m}_s${s}/  -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m}_${s}_${i}
                #python sampler_creator.py -o ${c}_${m}_${s}_${i}_sampler.py -n ${c}_${m}_${s}_${i}${extension} --output-directory=m${m}_s${s}/ --ntuple-dir=m${m}_s${s}/
                #python analysis_creator.py -s ${c}_${m}_${s}_${i}_sampler.py -N ${Nnodes} -n ${Ncores} -o ${c}_${m}_${s}_${i}${outputfile_ext} --sample-dir=m${m}_s${s}/ --output-subdir=m${m}_s${s}/
                #echo heppy_batch2.py -o ${PATH_TO_OUT}${c}_m${m/./}_s${s}_${i}/  m${m}_s${s}/${c}_${m}_${s}_${i}${analysisfile_ext} -b "qsub ${PATH_TO_OUT}${c}_m${m/./}_s${s}_${i}/tt_semilepton_ILD_Chunk0/batchScript.sh -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m/./}_${s}_${i}" 
                #echo heppy_batch2.py -o ${PATH_TO_OUT}${c}_m${m/./}_s${s}_${i}/  m${m}_s${s}/${c}_${m}_${s}_${i}${analysisfile_ext} -b "qsub batchScript.sh -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m/./}_${s}_${i}"
                ii=$((${ii} + 1))
            fi
        done
    done
done
echo ${ii}






