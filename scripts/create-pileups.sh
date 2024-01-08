#! /usr/bin/env sh

run_dir=$1
src=`basename ${run_dir}`

container=/local/incoming/covid/config/freyja_latest.sif
script=/local/incoming/covid/scripts/parse_pileup-v12.pl

cd $run_dir
mkdir -p tmp
mkdir -p pileups

echo "Moving pileups"
find ./Assemblies/ -name "*.pileup*" -exec cp {} tmp/ \;
echo "Uncompressing files"
gunzip -v tmp/*.gz

for i in tmp/*.pileup
 do
	f=`basename $i`
	echo Processing $f
	echo "singularity run -B $script $container perl $script < $i  > pileups/${f}.tab" 
	singularity run -B $script $container perl $script < $i  > pileups/${f}.tab
 done

