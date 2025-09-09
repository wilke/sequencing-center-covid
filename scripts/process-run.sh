#! /usr/bin/env sh 

run_dir=$1
src=`basename ${run_dir}`

covid_run_dir=/local/incoming/covid/runs/${src}/
export_dir=/vol/sars2/jdavis/Sarah/
ssh_id_file=/local/incoming/covid/config/covid_rsa
rsa_file=covid_`whoami`_rsa

jim=/vol/sars2/jdavis/Sarah/
base=/local/incoming/covid/

echo Processing covid-run folder ${src} `date`

# Use FREYJA_VERSION if set, otherwise default to 'latest'
FREYJA_VERSION=${FREYJA_VERSION:-latest}
echo "Using Freyja version: ${FREYJA_VERSION}"

echo Moving bam files
find ${covid_run_dir}/Assemblies -name *.sorted.bam -exec mv {} ${covid_run_dir}/staging/ \;
# find ${covid_run_dir}/Assemblies -name *.sorted.bam -exec mv {} ${covid_run_dir}/bam/ \;
current=`pwd`
cd ${covid_run_dir}

nr_assemblies=`ls ${covid_run_dir}/staging/ | wc -l`
echo Found ${nr_assemblies} samples from assemblies

echo Setting date for bam files
mapping_file=`ls *.sample-mapping.tsv`
python3 ${base}/scripts/staging2bam.py -m ${mapping_file} -s ./staging/ -d ./bam/

nr_samples=`ls ${covid_run_dir}/bam/ | wc -l`
echo Processing ${nr_samples}/${nr_assemblies} samples

echo "Computing variants and out files with Freyja ${FREYJA_VERSION}" `date`
make update FREYJA_VERSION=${FREYJA_VERSION}
make -B -i -j 20 strain FREYJA_VERSION=${FREYJA_VERSION}
make -i -j 10 strain FREYJA_VERSION=${FREYJA_VERSION} 
echo Done - Computing variants and out files `date`

echo Create coverage and summary
for i in depth/* ; do sh ${base}/scripts/depth2cov.sh $i ; done > coverage.all.txt
for i in output/* ; do python3 ${base}/scripts/out2spreadsheet.py $i ; done > summary.tsv

echo Creating summary
sort summary.tsv > summary.sorted.tsv
sort coverage.all.txt > coverage.sorted.txt
cat coverage.sorted.txt | cut -f1,2 > coverage.c1.c2

join -t $'\t' -a 1 -a 2 -e 'n/a' -j 1 summary.sorted.tsv coverage.c1.c2 > summary.all.tsv

python3 ${base}/scripts/update-sample-mapping.py -c coverage.all.txt -m ${mapping_file} -s output 2>./summary.error.log 1> ${mapping_file}.updated.tsv

echo Creating Pileups
sh /local/incoming/covid/scripts/create-pileups.sh $run_dir

# echo Moving data for plotting
# python3 ${base}/scripts/samples2aggregates.py --mapping-file ${mapping_file} --sites2labels ${base}/mapping.tsv --source-dir ./ --destination-dir ${base}/aggregate/current/

cd $current
echo Done - Processing covid-run folder ${src} `date`
