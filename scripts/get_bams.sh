
jim=/vol/sars2/jdavis/Sarah/
base=/local/incoming/covid/
run_dir=$1
src=`basename ${run_dir}`

echo rsync -zurvp --rsh="ssh -i /local/incoming/covid/config/covid_rsa" --include="*.bam" --exclude="*.*"  wilke@locust:${jim}/${src}/ ${run_dir}/

rsync -zurvp --rsh="ssh -i /local/incoming/covid/config/covid_rsa" --include="*.bam" --exclude="*.*"  wilke@locust:${jim}/${src}/ ${run_dir}/

find ${run_dir}/Assemblies -name *.sorted.bam -exec mv {} ${run_dir}/bam/ \;
find ${run_dir}/Assemblies -name *.sorted.bam -exec mv {} ${run_dir}/bam/ \;
current=`pwd`
cd ${run_dir}
make -j 8 strain

for i in depth/* ; do sh ${base}/scripts/depth2cov.sh $i ; done | tee coverage.all.txt
for i in output/* ; do python3 ${base}/scripts/out2spreadsheet.py $i ; done > summary.tsv

sort summary.tsv > summary.sorted.tsv
sort coverage.all.txt > coverage.sorted.txt
join -t $'\t' -a 1 -a 2 -e 'n/a' -j 1 summary.sorted.tsv <(cat coverage.sorted.txt | cut -f1,2) > summary.all.tsv
cd $current

