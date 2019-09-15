#!/usr/bin/env bash

Nnodes=2
Ncores=8

#jobname=1730

#analysis_subdir=splitmtop/
#analysisfile=ee_ttbar_splitmtop_1730
#analysisfile=ee_
analysisfile_ext=_analysis.py

mtop=(171.8 172.6 173.0 173.4 174.2)
mtop_len=${#mtop[@]}
mtop_central_idx=2
sqrts=(340 342 344 346 350)
sqrts_len=${#sqrts[@]}
sqrts_central_idx=2
cards=(tt dilep had ww zz hz)
cards_len=${#cards[@]}

# ALL JOBS SENT! 
Nstart=44
Nend=$(( ${Nstart} + 1 ))

PATH_TO_OUT=/storage_mnt/storage/user/mmancini/testFCC/Nicolo/heppy/ttbar_analysis/ANALYSIS/OUT/
#output_folder=

#for (( j=40; j<Njobs; j++)); do
#    echo job: ${j}
#    for ((ic = 0; ic<cards_len; ic++  )); do
#        heppy_batch2.py -o ${PATH_TO_OUT}${cards[${ic}]}_${j} ${cards[${ic}]}/${analysisfile}${cards[${ic}]}_${j}${analysisfile_ext} -b "qsub batchScript.sh -lnodes=${Nnodes}:ppn=${Ncores} -N ${cards[${ic}]}_${j}"
#    done
#done

#for (( j=100; j<Njobs; j++)); do
#    echo job: ${j}
#    echo heppy_batch2.py -o ${PATH_TO_OUT}${analysisfile}_3_${j} ${analysis_subdir}${analysisfile}_${j}${analysisfile_ext} -b "qsub batchScript.sh -lnodes=${Nnodes}:ppn=${Ncores} -N job_${j}"
#done

ii=0
for ((i = Nstart; i<Nend; i++)); do
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
                    #python analysis_creator.py -s ${c}_${m}_${s}_${i}_sampler.py -N ${Nnodes} -n ${Ncores} -o ${c}_${m}_${s}_${i}${outputfile_ext} --sample-dir=m${m}_s${s}/ --output-subdir=m${m}_s${s}/
                    #echo heppy_batch2.py -o ${PATH_TO_OUT}${c}_m${m/./}_s${s}_${i}/  m${m}_s${s}/${c}_${m}_${s}_${i}${analysisfile_ext} -b "qsub ${PATH_TO_OUT}${c}_m${m/./}_s${s}_${i}/tt_semilepton_ILD_Chunk0/batchScript.sh -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m/./}_${s}_${i}"
                    echo heppy_batch2.py -o ${PATH_TO_OUT}${c}_m${m/./}_s${s}_${i}/  m${m}_s${s}/${c}_${m}_${s}_${i}${analysisfile_ext} -b "qsub batchScript.sh -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m/./}_${s}_${i}"
                done
            else
                c=tt
                #python card_creator.py -o ${c}_${m}_${s}_${i}.txt -m ${m} -W ${topwidth} -N ${Nevents} -E ${s} -c ${c}
                #qsub run_ee_ttbar_1card.sh -v GENERATOR=${c}_${m}_${s}_${i}.txt,subdir=m${m}_s${s}/  -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m}_${s}_${i}
                #python sampler_creator.py -o ${c}_${m}_${s}_${i}_sampler.py -n ${c}_${m}_${s}_${i}${extension} --output-directory=m${m}_s${s}/ --ntuple-dir=m${m}_s${s}/
                #python analysis_creator.py -s ${c}_${m}_${s}_${i}_sampler.py -N ${Nnodes} -n ${Ncores} -o ${c}_${m}_${s}_${i}${outputfile_ext} --sample-dir=m${m}_s${s}/ --output-subdir=m${m}_s${s}/
                #echo heppy_batch2.py -o ${PATH_TO_OUT}${c}_m${m/./}_s${s}_${i}/  m${m}_s${s}/${c}_${m}_${s}_${i}${analysisfile_ext} -b "qsub ${PATH_TO_OUT}${c}_m${m/./}_s${s}_${i}/tt_semilepton_ILD_Chunk0/batchScript.sh -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m/./}_${s}_${i}" 
                echo heppy_batch2.py -o ${PATH_TO_OUT}${c}_m${m/./}_s${s}_${i}/  m${m}_s${s}/${c}_${m}_${s}_${i}${analysisfile_ext} -b "qsub batchScript.sh -lnodes=${Nnodes}:ppn=${Ncores} -N ${c}_${m/./}_${s}_${i}"
                ii=$((${ii} + 1))
            fi
        done
    done
done
echo ${ii}








