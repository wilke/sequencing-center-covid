#! /usr/bin/env sh

run_dir=$1
src=`basename ${run_dir}`

# Use FREYJA_VERSION if set, otherwise default to 'latest'
FREYJA_VERSION=${FREYJA_VERSION:-latest}
container=/local/incoming/covid/config/freyja_${FREYJA_VERSION}.sif
script=/local/incoming/covid/scripts/parse_pileup-v12.pl

echo "Using Freyja version: ${FREYJA_VERSION}"

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

