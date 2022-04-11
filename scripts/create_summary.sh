$1

jim=/vol/sars2/jdavis/Sarah/
base=/local/incoming/covid/
src=`basename $1`


current=`pwd`
cd $1

for i in depth/* ; do sh ${base}/scripts/depth2cov.sh $i ; done | tee coverage.all.txt
for i in output/* ; do python3 ${base}/scripts/out2spreadsheet.py $i ; done > summary.tsv

sort summary.tsv > summary.sorted.tsv
sort coverage.all.txt > coverage.sorted.txt
join -t $'\t' -a 1 -a 2 -e 'n/a' -j 1 summary.sorted.tsv <(cat coverage.sorted.txt | cut -f1,2) > summary.all.tsv
cd $current

