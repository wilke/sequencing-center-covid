#!/usr/bin/env bash

threshold=3

if [ -f $1 ] 
	then
		f=$1
		total=`wc -l $f | cut -d ' ' -f1`
		count=0
		sample=`basename $f .depth`
		for number in `cut -f4 $f` ; do if [ ${number} -ge $threshold ] ; then count=$(($count + 1)) ; fi ; done
		cov=`bc <<< "scale=2; $count * 100 / $total"` 
		echo ${sample}$'\t'$cov$'\t'Sample=$sample File=$f Threshold=${threshold} Count=${count} Total=${total} Coverage=$cov
	else
		echo No file $1
	fi
