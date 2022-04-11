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
			echo Aggregate for $g $d
			rm $g/*.aggregate.*
			rm $g/.*aggregate*
			singularity  run --bind ${base} $FREYJA freyja aggregate ${g}/ --output ${g}/$d.aggregate.tsv 2>&1 
			python3 ${base}/scripts/sortAggregate.py ${g}/$d.aggregate.tsv  > $g/$d.aggregate.line.tsv  
			fgrep -v "[]" $g/$d.aggregate.line.tsv > $g/$d.aggregate.line.filtered.tsv
			sort -n  < $g/$d.aggregate.line.filtered.tsv > $g/$d.aggregate.line.sorted.tsv
			if [ ! -f $g/$d.aggregate.line.sorted.tsv ] 
				then
					echo missing $g/$d.aggregate.line.sorted.tsv
					# exit
				fi  
			echo Plot $d
 			singularity  run --bind /local/incoming/covid/ $FREYJA freyja plot $g/$d.aggregate.line.sorted.tsv  --output $g/$d.aggregate.pdf 
			echo Lineages $d
			singularity  run --bind /local/incoming/covid/ $FREYJA freyja plot $g/$d.aggregate.line.sorted.tsv  --lineages --output $g/$d.aggregate.lineages.pdf
		done
	done
