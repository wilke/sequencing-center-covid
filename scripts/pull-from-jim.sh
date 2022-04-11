#! /usr/bin/env sh 

run_dir=$1
src=`basename ${run_dir}`

covid_run_dir=/local/incoming/covid/runs/${src}/
export_dir=/vol/sars2/jdavis/Sarah/
ssh_id_file=/local/incoming/covid/config/covid_rsa
rsa_file=covid_`whoami`_rsa

jim=/vol/sars2/jdavis/Sarah/
base=/local/incoming/covid/
echo Pulling $run_dir
echo rsync -zurv --rsh="ssh -i ~/.ssh/${rsa_file}" --include="*.bam" --exclude="*.*"  wilke@locust:${jim}/${src}/ ${covid_run_dir}/

rsync -zurv --chmod=g\+w --rsh="ssh -i ~/.ssh/${rsa_file}" --include="*.bam" --exclude="*.*"  wilke@locust:${jim}/${src}/ ${covid_run_dir}/


echo Moving bam files
find ${covid_run_dir}/Assemblies -name *.sorted.bam -exec mv {} ${covid_run_dir}/staging/ \;
# find ${covid_run_dir}/Assemblies -name *.sorted.bam -exec mv {} ${covid_run_dir}/bam/ \;
current=`pwd`
cd ${covid_run_dir}

echo Setting date for bam files
python3 ${base}/scripts/bam2samples.py -m ${base}/samples.tsv -s ./staging/ -d ./bam/
echo Computing variants and out files
make -j 8 strain

echo Create coverage and summary
for i in depth/* ; do sh ${base}/scripts/depth2cov.sh $i ; done | tee coverage.all.txt
for i in output/* ; do python3 ${base}/scripts/out2spreadsheet.py $i ; done > summary.tsv

sort summary.tsv > summary.sorted.tsv
sort coverage.all.txt > coverage.sorted.txt
cat coverage.sorted.txt | cut -f1,2 > coverage.c1.c2

join -t $'\t' -a 1 -a 2 -e 'n/a' -j 1 summary.sorted.tsv coverage.c1.c2 > summary.all.tsv
cd $current
echo Done `date`
