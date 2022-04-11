#! /usr/bin/env perl 
use strict;
use Proc::ParallelLoop;
use Getopt::Long;

my $usage = 'Parallel-assemblies.pl -n (number of processes)  <id\tread1path\tread2path
        
        required: -n number threads
        		  -p primers [ARTIC midnight qiagen swift varskip varskip-long]
        		     if ARTIC, must declare version.
        		  -v ARTIC primer version [ 3, 4, and 4.1]
        optional  -a assembly dir [d = "Assemblies"];


';

my ($help, $np, $ver, $adir, $primer);
my $adir = "Assemblies";

my $opts = GetOptions('h'   => \$help, 
                      'n=i' => \$np,
                      'v=i' => \$ver,
                      'p=s' => \$primer,  
                      'a=s' => \$adir);

if ($help){die "$usage\n";}
unless ($np){die "need number of processors\n$usage\n";}
unless ($primer){die "must declare a primer set"}
if (($primer =~ /ARTIC/i) && (! $ver)){die "need artic primer version\n$usage\n";}


my @array; 
while (<>)
{
    chomp; 
    push @array, $_;
}

if ($ver =~ /ARTIC/i)
{
	pareach(\@array,  sub { my $stuff = shift @_; my ($mcov, $r1, $r2) = split ("\t", $stuff); 
	system "sars2-onecodex -j 24 -D 3 -d 8000 --primer-version $ver --primers $primer -n $mcov -1 $r1 -2 $r2 $mcov $adir/$mcov"; }, { Max_Workers => $np });
}

else 
{
	pareach(\@array,  sub { my $stuff = shift @_; my ($mcov, $r1, $r2) = split ("\t", $stuff); 
	system "sars2-onecodex -j 24 -D 3 -d 8000  --primers $primer -n $mcov -1 $r1 -2 $r2 $mcov $adir/$mcov"; }, { Max_Workers => $np });
}



