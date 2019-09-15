#!/usr/bin/env bash

Nevents=100000
mtop=173
topwidth=1.41
sqrts=(340 342 344 346 350)
sqrts_len=${#sqrts[@]}
cards=(tt dilep had ww zz hz)
cards_len=${#cards[@]}

ncards=6

#filename=ee_ttbar_splitmtop_1730_

for ((i = 3; i<ncards; i++)); do
    for ((j = 0; j<sqrts_len; j++)); do
        s=${sqrts[j]}
        c=${cards[i]}
        filename=${c}_${s}.txt
        echo making card ${c}, sqrts ${s}
        #for ((ic = 0; ic<cards_len; ic++  )); do
        python card_creator.py -o ${filename} -m ${mtop} -W ${topwidth} -N ${Nevents} -E ${s} -c ${c}
            #echo python card_creator.py -o ee_${cards[${ic}]}_${i}.txt -m ${mtop} -W ${topwidth} -N ${Nevents} -E ${sqrts} -c ${cards[${ic}]}
        #done
    done
done
