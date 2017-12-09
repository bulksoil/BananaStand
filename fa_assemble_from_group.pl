#!/usr/bin/perl
#################################
# Written by Joe Edwards
# Sundaresan Lab
# Department of Plant Biology
# University of California - Davis
# 2013
##################################

# This script takes a group file and a contigs FASTQ file
# and makes a fasta file with the appropriate headers for
# analysis in qiime

use strict;
use warnings;

my ($group, $fq) = @ARGV;														# Grab the group file and and fastq file from the command line, order is important

open GROUP, "$group" or die "Cannot open group file: $group\n";
open FQ, "$fq" or die "Cannot open fastq file: $fq\n";

my %bcs = ();																		# Initialize hash for group names
my %seqs = ();																		# Initialize hash for barcode sequences
while (my $line = <GROUP>) {													# Open loop to read the group file
	chomp $line;																	# Remove line break 
	my @fields = split(/\t/, $line);											# Split the line into an array
	$bcs{$fields[0]} = $fields[1];											# This first 
	$seqs{$fields[1]} = $fields[2];
}

my $count = 1;
while (my $header = <FQ>) {
	chomp $header;
	chop $header;
	chop $header;
	my $seq = <FQ>; chomp $seq;
	my $skip = <FQ>; $skip = <FQ>;
	next if !exists $bcs{$header};
	my $samp = $bcs{$header};
	my $samp1 = $samp . "_" . $count;
	$header =~ s/@//;
	print ">$samp1\t$header\torig_bc=GATACA\tnew_bc=GATACA\tbc_diffs=0\n$seq\n";
	$count++;
	warn "Found $count so far\n" if ($count % 10000 == 0);
}	
