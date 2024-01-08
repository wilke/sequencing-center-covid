#! /usr/bin/env perl
use strict;
use Getopt::Long;
use Data::Dumper;

my $usage = 'parse_pileup.pl [options] <mpielup >output
	
	Eliminates uninformative columns in an mpileup defined as those that 
	Match the reference sequence
	
	
	my current pileups are based on:
	time samtools mpileup -q 20 -f NC_045512.trimmed.fa -d 8000 
	MCoV-65205.sorted.bam --output-QNAME --adjust-MQ 50 -B  >test.2.pileup
	## samtools 1.14
	
	-f fraction [d = 0.05]
		fraction of nucleotides required for consideration of the position
		as a SNP/INDEL  
	-h help
';

my $frac = 0.05;
#my $frac = 0.15;

my ($help);
my $opts = GetOptions('h'     => \$help,
                      'f=s'   => \$frac);                      

if ($help){die "$usage\n"}

my $hash = {};
my %begins;
my %ends;

print "Position\tStatus\tRef_Base\tDepth\tConsensus\tConsensus_Depth\tDot\tA\tT\tG\tC\tAmbigous\tInsertion\tDeletion\tStar\tRead_starts\tRead_ends\n";



while (<>)
{
	chomp;
	my ($ref, $pos, $ref_base, $depth, $lcpile, $phred, $ids) = split /\t/;
	
	$begins{$pos} = 0;
	$ends{$pos} = 0;

	#initiate data structure:
	@{$hash->{$pos}->{INDEL_READ}} = ();
	@{$hash->{$pos}->{INDEL_CHANGE}} = ();
	@{$hash->{$pos}->{DOT_READ}} = ();
	@{$hash->{$pos}->{STAR_READ}} = ();
	@{$hash->{$pos}->{NT_READ}}  = ();
	@{$hash->{$pos}->{NT_CHANGE}}  = ();

	my $pile = uc $lcpile;
	$pile =~ s/\,/\./g;
		
	my @pileup =  split ("", $pile); 
	my @reads = split (",", $ids); 
	my $count = 0;

	while (@pileup)
	{
		my $element = shift @pileup; 
		
		# if it is conserved:
		if ($element =~ /\./)
		{
			#push @{$hash->{$pos}->{DOT_READ}}, "$reads[$count], $count";
			push @{$hash->{$pos}->{DOT_READ}}, "$reads[$count]";	
			$count ++;
		}
		
		#if it is a * signifying a place holder of a deletion:
		elsif ($element =~ /\*/)
		{
			#push @{$hash->{$pos}->{STAR_READ}}, "$reads[$count], $count";
			push @{$hash->{$pos}->{STAR_READ}}, "$reads[$count]";
			$count ++;	
		}
		
		#if it is a nucleotide and not within an indel, push and increment.
		elsif ($element =~ /[A-Z]/i)
		{
			#push @{$hash->{$pos}->{NT_READ}}, "$reads[$count], $count";
			#push @{$hash->{$pos}->{NT_CHANGE}}, "$element, $count";
			push @{$hash->{$pos}->{NT_READ}}, "$reads[$count]";
			push @{$hash->{$pos}->{NT_CHANGE}}, "$element";
			$count ++;
		}
		
		#if it is an indel
		elsif ($element =~ /[\+|\-]/i)
		{
			# count will be incremented by 1, so  need to do count -1 to get the 
			#
			my $loc = ($count -1); #correct indel loc
			my $string = join ("", @pileup);
			$string =~ s/^(\d+)//;
			my $len = $1;			
			my $bases = substr($string, 0, $len);		
			my $indel = $element.$len.$bases;  

			#push @{$hash->{$pos}->{INDEL_READ}}, "$reads[($loc )], $loc";
			#push @{$hash->{$pos}->{INDEL_CHANGE}}, "$indel, $loc";
			push @{$hash->{$pos}->{INDEL_READ}}, "$reads[($loc)]";
			push @{$hash->{$pos}->{INDEL_CHANGE}}, "$indel";
	
			my @indel = split ("", $indel);
			shift @indel;
			while (@indel)
			{
				shift @pileup;
				shift @indel;	
			}
		}	
		
		# keep track of ends 
		elsif ($element =~ /\$/i)
		{
			$ends{$pos}++;
		}

		#keep track of starts 
		elsif ($element =~ /\^/i)
		{
			$begins{$pos}++;
			shift @pileup; #get rid of phred value with start
		}
		
		#die on a reference skip.  we shouldn't see this with sars-cov-2.
		elsif ($element =~ /[\<|\>]/i)
		{
			die "Found a reference-skip charcter in the pileup string: $element at position: $pos, character: $count.  The code does not currently support reference skips.\n"  
		}
		
	}

	#----------------------------------------------------------------------------
	# Determine if this is a conserved (same as reference) or consistent position
	# If consistent or conserved, Report 
	# If not, keep it for further processing of mixed variants.
	
	
	my $cutoff = ((1 - $frac) * $depth);	
	my $min = ($frac * $depth); 
	
	# process easy columns first.
	my $n_dot = scalar @{$hash->{$pos}->{DOT_READ}};
	my $n_indel = scalar @{$hash->{$pos}->{INDEL_READ}};
	my $n_star = scalar @{$hash->{$pos}->{STAR_READ}};
	my $n_snp = scalar @{$hash->{$pos}->{NT_READ}};
	
	#if it is a consistent deletion position
	if ($n_star >= $cutoff)
	{
		print "$pos\tSTAR\t$ref_base\t$depth\t\*\t$n_star\n"
	}
	
	#if it is a conserved nucleotide position
	elsif (($n_dot >= $cutoff) && ($n_indel < $min))
	{
		print "$pos\tCONSERVED\t$ref_base\t$depth\t\.\t$n_dot\n",	
	}

	#if it is a consistent indel
	elsif ($n_indel > $cutoff)
	{
		my %difs;
		foreach (@{$hash->{$pos}->{INDEL_CHANGE}})
		{
			$difs{$_}++;
		}

		my $largest;
		my $n_largest = 0;
		foreach (keys %difs)
		{
			if ($difs{$_} > $n_largest)
			{
				$largest = $_;
				$n_largest = $difs{$_}; 
			}
		}
		print "$pos\tCONSISTENT_INDEL\t$ref_base\t$depth\t$largest\t$n_largest\n";	
	}
	
	#if it is a consistent nt change

	elsif ($n_snp> $cutoff)
	{
		my %difs;
		foreach (@{$hash->{$pos}->{NT_CHANGE}})
		{
			$difs{$_}++;
		}

		my $largest;
		my $n_largest = 0;
		foreach (keys %difs)
		{
			if ($difs{$_} > $n_largest)
			{
				$largest = $_;
				$n_largest = $difs{$_}; 
			}
		}
		print "$pos\tCONSISTENT_SNP\t$ref_base\t$depth\t$largest\t$n_largest\n";	
	}
	else
	{
		#print refbase and depth, skip match columns
		print "$pos\tUNCONSERVED\t$ref_base\t$depth\t#\t#\t";
		
		
		#print counts of A,T,G,C,(ambg), in, del
		my ($dot, $a, $t, $g, $c, $amb, $star, $in, $del) = (0) x 9;
		
		$dot =  scalar(@{$hash->{$pos}->{DOT_READ}});
		$star = scalar(@{$hash->{$pos}->{STAR_READ}});
		
		my $nt_ref = \@{$hash->{$pos}->{NT_CHANGE}};		
		foreach (@$nt_ref)
		{
			if ($_ =~ /A/i){$a++;}
			elsif ($_ =~ /T/i){$t++;}
			elsif ($_ =~ /G/i){$g++;}
			elsif ($_ =~ /C/i){$c++;}
			else {$amb++;}
		}
		#counts of indels.
		my $indel_ref = \@{$hash->{$pos}->{INDEL_CHANGE}};		
		foreach (@$indel_ref)
		{
			if ($_ =~ /^\+/i){$in++;}
			elsif ($_ =~ /^\-/i){$del++;}
		}

		print "$dot\t$a\t$t\t$g\t$c\t$amb\t$in\t$del\t$star\t$begins{$pos}\t$ends{$pos}\n"; 		
	
	}
	
	
	
	
}


	
	
	
	



























