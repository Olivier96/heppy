#!/usr/bin/env bash

Nevents=2500
mtop=(171.8 172.6 173.0 173.4 174.2)
mtop_len=${#mtop[@]}
mtop_central_idx=2
topwidth=1.41
sqrts=(340 342 344 346 350)
sqrts_len=${#sqrts[@]}
sqrts_central_idx=2
cards=(tt dilep had ww zz hz)
cards_len=${#cards[@]}

ncards=45
ii=0
#filename=ee_ttbar_splitmtop_1730_

for ((i = 0; i<ncards; i++)); do
    echo card number ${i}
    for ((is = 0; is <sqrts_len; is++)); do
        for ((im = 0; im<mtop_len; im++)); do
            m=${mtop[im]}
            s=${sqrts[is]}
            if [[ im -eq mtop_central_idx ]]; then
                for ((ic = 0; ic<cards_len; ic++  )); do
                    c=${cards[${ic}]}
                    ii=$((${ii} + 1))
                    python card_creator.py -o ${c}_${m}_${s}_${i}.txt -m ${m} -W ${topwidth} -N ${Nevents} -E ${s} -c ${c}
                done
            else
                c=tt
                python card_creator.py -o ${c}_${m}_${s}_${i}.txt -m ${m} -W ${topwidth} -N ${Nevents} -E ${s} -c ${c}
                ii=$((${ii} + 1))
            fi
        done
    done
done

echo ${ii}
