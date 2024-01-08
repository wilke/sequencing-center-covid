#!/usr/bin/env bash
primer=$1
id=$2
reads=${id}.reads

base=/local/incoming/covid/

if [ $primer == qiagen ] 
then
	echo Assembly with qiagen
	perl ${base}/scripts/parallel-assemblies-v2.pl -n 10 -p qiagen < ${reads}
elif [ $primer == swift ] 
then
	echo Assembly with swift
	perl ${base}/scripts/parallel-assemblies-v2.pl -n 10 -p swift < ${reads}
elif [ $primer == midnight ] 
then
	echo Assembly with midnight
        perl ${base}/scripts/parallel-assemblies-v2.pl -n 10 -p midnight < ${reads}
else
	echo Unkown primer: ${primer}, supported values are qiagen, swift and midnight
fi

exit

# perl ${base}/scripts/parallel-assemblies-v2.pl -n 4 -p qiagen < ${reads}
# perl ${base}/scripts/parallel-assemblies-v2.pl -n 10 -p swift < ${reads}

ls Assemblies | perl -e 'while (<>){chomp; my $mcov = $_; system "cp Assemblies/$mcov/$mcov.fasta Consensus/$mcov.fasta";}'
ls Consensus| perl -e 'use gjoseqlib; while (<>){chomp; my $mcov = $_; $mcov =~ s/\.fasta//g; open (IN, "<Consensus/$_"); my @seqs = &gjoseqlib::read_fasta(\*IN); close IN; &gjoseqlib::print_alignment_as_fasta([$mcov, undef, $seqs[0][2]]);}' > ${id}.dna
