locations=/local/incoming/covid/aggregate/locations/
base=/local/incoming/covid/
FREYJA=/local/incoming/covid/config/freyja_1.3.1.sif
log=`date +%Y-%m-%d`.error.log

g=$1
d=`basename $g` 
echo Aggregate for $g $d
echo singularity  run --bind ${base} $FREYJA freyja aggregate ${g}/ --output ${g}/$d.aggregate.tsv  
rm ${g}/*.aggregate.*
rm ${g}/.*aggregate*
singularity  run --bind ${base} $FREYJA freyja aggregate ${g}/ --output ${g}/$d.aggregate.tsv
python3 ${base}/scripts/sortAggregate.py ${g}/$d.aggregate.tsv  > $g/$d.aggregate.line.tsv  
fgrep -v "[]" $g/$d.aggregate.line.tsv > $g/$d.aggregate.line.filtered.tsv
sort -k 1.5,1.6n -k 1.1,1.2n -k 1.3,1.4n < $g/$d.aggregate.line.filtered.tsv > $g/$d.aggregate.line.sorted.tsv

if [ ! -f $g/$d.aggregate.line.sorted.tsv ] 
 then
 echo missing $g/$d.aggregate.line.sorted.tsv
					# exit
fi  

echo Plot $d

echo singularity run --bind /local/incoming/covid/ $FREYJA freyja plot $g/$d.aggregate.line.sorted.tsv  --output $g/$d.aggregate.pdf
singularity run --bind /local/incoming/covid/ $FREYJA freyja plot $g/$d.aggregate.line.sorted.tsv  --output $g/$d.aggregate.pdf 
echo Lineages $d
echo singularity  run --bind /local/incoming/covid/ $FREYJA freyja plot $g/$d.aggregate.line.sorted.tsv  --lineages --windowsize 300 --output $g/$d.aggregate.lineages.pdf 
singularity  run --bind /local/incoming/covid/ $FREYJA freyja plot $g/$d.aggregate.line.sorted.tsv  --lineages --windowsize 300 --output $g/$d.aggregate.lineages.pdf
