#!/usr/bin/perl

use strict; # 
use warnings; #
use Getopt::Std; # Get's arguments from the command line

my %opts; # Defining the opts hash
getopts('f:m:', \%opts); # getting options from the command line. f is the fasta file, m is the max length

open FA, "$opts{f}" or die; # opening the fasta file

my $processed = 0; # Defining how many sequences have been processed
my $removed_for_length = 0; # Defining how many sequences have been removed due to length incompatibilities
my $ambigs = 0; # Defining how many sequences are removed for having 'N's
my $kept = 0; # Defining how many sequences are passing the filters
while (my $header = <FA>) { # Start the loop on the fast file
	chomp $header; # get rid of the linebreak at the end of the line
	my $seq = <FA>; chomp $seq; # get the sequence, which is just after the header in the fasta
	warn "$processed total\t$removed_for_length removed due to length\t$ambigs removed due to ambiguities\n" if $processed % 10000 == 0; # print some stats
	if (length $seq > $opts{m}) { # Check if the length of the sequence is greater than the maximum allowed
		$processed++; # If so, tally one for the processed variable
		$removed_for_length++; # If so, tally one for the removed for length violation variable
		next; # go to next iteration of the loop. There's no point in doing the commands below this
	}
	$seq =~ s/N$//; # If the sequence has an N at the back then replace it with nothing, ie cut it off
	$seq =~ s/^N//; # If the sequence has an N at the front cut if off
	if ($seq =~ /N/) { # If there is an N in the interior of the sequence
		$processed++; # tally one for processed
		$ambigs++; # tally one for the ambig variable
		next; # Go to next iteration
	}
	# If the loop reaches this point, then it means the sequence has passed its checks
	$processed++; 
	print "$header\n$seq\n"; # print the header and sequence
}
