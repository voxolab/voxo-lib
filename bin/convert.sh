#!/bin/bash

for show in `ls -d T*`; do

    echo $show;
    sort -n -k3 $show/decode/results/resul.1.ctm > $show/$show.utf8.ctm
    iconv -f utf8 -t latin1 $show/$show.utf8.ctm > $show/$show.iso.ctm

    sort -k3,3 -n $show/seg/$show.iv.seg > $show/$show.sorted.iv.seg

    ~/usr/src/python/voxo-lib/voxolab/ctm_to_uppercase.py $show/$show.iso.ctm $show/$show.iso.upper.ctm /home/vjousse/usr/bin/majAuto

    iconv -f latin1 -t utf8 $show/$show.iso.upper.ctm > $show/$show.utf8.upper.ctm

    ~/usr/src/python/voxo-lib/voxolab/seg_ctm_to_xml.py $show/$show.utf8.upper.ctm $show/$show.sorted.iv.seg > $show/$show.xml

    ~/usr/src/python/voxo-lib/voxolab/xml_alpha_to_numbers.py $show/$show.xml $show/$show.withnumbers.xml ~/usr/src/python/voxo-lib/bin/convertirAlphaEnNombre.pl ~/usr/src/python/voxo-lib/bin/convertirNombreEnAlpha.pl

    ~/usr/src/python/voxo-lib/voxolab/xml_to_srt.py $show/$show.withnumbers.xml $show/$show.srt

    ~/usr/src/python/voxo-lib/voxolab/xml_to_webvtt.py $show/$show.withnumbers.xml $show/$show.vtt

    ~/usr/src/python/voxo-lib/voxolab/xml_to_txt.py $show/$show.withnumbers.xml $show/$show.txt

    cp $show/$show.txt results
    cp $show/$show.srt results

done
