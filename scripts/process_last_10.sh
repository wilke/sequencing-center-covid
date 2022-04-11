locations=/local/incoming/covid/aggregate/testing/
base=/local/incoming/covid/
FREYJA=/local/incoming/covid/config/freyja_1.3.2.sif
log=`date +%Y-%m-%d`.error.log
for l in ${locations}/* 
	do 
	groups=${l}
	for g in ${groups}/* 
		do 
			d=`basename $g` 
			echo Last 10 Aggregate for $g $d
			lines=`wc -l $g/$d.aggregate.line.sorted.tsv | cut -f1 -d " "`
			echo Found $lines lines
			if [ ${lines} -ge 15 ]
			then
				head -n 2  $g/$d.aggregate.line.sorted.tsv >  $g/$d.aggregate.last.10.tsv
				tail -n 10  $g/$d.aggregate.line.sorted.tsv >>  $g/$d.aggregate.last.10.tsv
				echo Plot $d
 				singularity  run --bind /local/incoming/covid/ $FREYJA freyja plot $g/$d.aggregate.last.10.tsv  --output $g/$d.aggregate.10.pdf 
				echo Lineages $d
				singularity  run --bind /local/incoming/covid/ $FREYJA freyja plot $g/$d.aggregate.last.10.tsv  --lineages --output $g/$d.aggregate.10.lineages.pdf
			else
				echo Not enough entries $lines for $d
				# sleep 10		
			fi

		done
	done
