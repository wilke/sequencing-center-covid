#!/usr/bin/env bash


for i in $1/*.out
	do 
		sample=`basename $i .out`
		datestring=`echo $sample | cut -f1 -d "-"`
		loc=`echo $sample | cut -f1 -d "_" | cut -f2 -d "-"`
		day=`echo $datestring | cut -c1,2`
		month=`echo $datestring | cut -c3,4`
		year=`echo $datestring | cut -c5,6`
		summarized=`grep summarized $i | cut -f2`
		lineages=`grep lineages $i | cut -f2` 

		echo $sample$'\t'${day}/${month}/${year}$'\t'${loc}$'\t'$i{summarized}$'\t'${lineages} 
	done

