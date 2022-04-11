run_dir=$1
current_dir=`pwd`
base=/local/incoming/covid

cd ${run_dir}

id=`basename $run_dir`
prefix=`date +%y%m%d-%H%M`

ls samples | perl -e 'use Cwd; my $hash = {}; while (<>){chomp; $name = $_; $name =~ s/(_R1|_R2).+//g; push @{$hash->{$name}}, getcwd . "/reads/$_";} foreach (keys %$hash){print "$_\t$hash->{$_}->[0]\t$hash->{$_}->[1]\n";}' > ${id}.reads

mkdir -p tmp
mkdir -p Assemblies
mkdir -p Consensus
# ln -s samples reads

echo Starting assembly: `date`
singularity run --pwd ${base}/runs/${id} -B ${base}/runs/${id}/tmp:/tmp -B ${base}:${base} ${base}/config/bvbrc-build-107.sif "sh ${base}/scripts/local-assembly.sh qiagen ${id}" > ${prefix}.assembly.log 2> ${prefix}.assembly.error
echo Assembly done: `date`

#ls Assemblies | perl -e 'while (<>){chomp; my $mcov = $_; system "cp Assemblies/$mcov/$mcov.fasta Consensus/$mcov.fasta";}'

#ls Consensus| perl -e 'use gjoseqlib; while (<>){chomp; my $mcov = $_; $mcov =~ s/\.fasta//g; open (IN, "<Consensus/$_"); my @seqs = &gjoseqlib::read_fasta(\*IN); close IN; &gjoseqlib::print_alignment_as_fasta([$mcov, undef, $seqs[0][2]]);}' > ${id}.dna 


# singularity shell -B /vol/sars2/jdavis/Sarah/220216_Swift-8-9/tmp:/tmp,/vol/ml/ /vol/patric3/production/containers/bvbrc-build-104.sif

# pangolin 220223_Direct_15_16.dna  -o 220223_Direct_15_16.pango

# cut -f5 -d, 220223_Direct_15_16.pango/lineage_report.csv |sort |uniq -c
cd ${current_dir}
