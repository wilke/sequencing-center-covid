
SRC=$1
GROUP=`basename $SRC`
locations=/local/incoming/covid/aggregate/testing/
base=/local/incoming/covid/
FREYJA=/local/incoming/covid/config/freyja_1.3.2.sif
log=`date +%Y-%m-%d`.error.log

g=$GROUP

echo $GROUP $SRC
sleep 10

for label in ${SRC}/* 

		do 
			d=`basename ${label}` 
			echo Aggregate for $g $d
			rm ${SRC}/${d}/*.aggregate.*
			rm ${SRC}/${d}/.*aggregate*
			singularity  run --bind ${base} $FREYJA freyja aggregate ${label}/ --output ${label}/$d.aggregate.tsv 2>&1 
			python3 ${base}/scripts/sortAggregate.py ${label}/$d.aggregate.tsv  > $label/$d.aggregate.line.tsv  
			fgrep -v "[]" $label/$d.aggregate.line.tsv > $label/$d.aggregate.line.filtered.tsv
			sort -n  < $label/$d.aggregate.line.filtered.tsv > $label/$d.aggregate.line.sorted.tsv
			if [ ! -f $label/$d.aggregate.line.sorted.tsv ] 
				then
					echo missing $label/$d.aggregate.line.sorted.tsv
					# exit
				fi  
			echo Plot $d
 			singularity  run --bind /local/incoming/covid/ $FREYJA freyja plot $label/$d.aggregate.line.sorted.tsv  --output $label/$d.aggregate.pdf 
			echo Lineages $d
			singularity  run --bind /local/incoming/covid/ $FREYJA freyja plot $label/$d.aggregate.line.sorted.tsv  --lineages --output $label/$d.aggregate.lineages.pdf
		done
