#!/usr/bin/python

import sys
import optparse
import os
import re

parser = optparse.OptionParser()
parser.add_option('-m', '--mapping_file', dest = "map", action = "store")
parser.add_option('-p', '--prefix', dest = "prefix", action = "store", default = "mpipe")
parser.add_option('--read1', dest = "read1", action = "store", default = "R1.fq")
parser.add_option('--read2', dest = "read2", action = "store", default = "R2.fq")
parser.add_option('--read3', dest = "read3", action = "store", default = "R3.fq")
parser.add_option('--read4', dest = "read4", action = "store", default = "R4.fq")
parser.add_option('-a', '--algorithm', dest = "pipeline", action = "store", default = "qiime")
parser.add_option('--max_length', dest = "max_length", action = "store", type = "int", default = 275)

options, args = parser.parse_args()

## Define Files
read1 = options.read1
read2 = options.read2
read3 = options.read3
read4 = options.read4
mapFile = options.map
prefix = options.prefix
pipeline = options.pipeline
max_length = options.max_length

## Demultiplex
groupFile = prefix + "_groups.txt"
dm_arg = 'demultiplex.py -m ' + mapFile + ' -f ' + read1 + ' -r ' + read4 + ' --I1 ' + read2 + ' --I2 ' + read3 + ' -p ' + prefix + ' -a ' + pipeline
print '[STATUS] Executing argument "' + dm_arg + '"'
print "Writing results to " + groupFile
os.system(dm_arg)

if pipeline.lower() == "dada2":
	sys.exit("\nDone")

## Grouping Read1
#r1_name = re.sub('\.f.*', '', read1)
r1GroupedFile = prefix + '_R1_grouped.fq'
#r1_g_arg = 'fq_group_extract.pl -g ' + groupFile + ' -q ' + read1 + ' > ' + r1GroupedFile
#print '[STATUS] Executing argument "' + r1_g_arg + '"'
#print 'Writing results to ' + r1GroupedFile
#os.system(r1_g_arg)

### Grouping Read4
#r4_name = re.sub('\.f.*', '', read4)
r4GroupedFile = prefix + '_R2_grouped.fq'
#r4_g_arg = 'fq_group_extract.pl -g ' + groupFile + ' -q ' + read4 + ' > ' + r4GroupedFile
#print '[STATUS] Executing argument "' + r4_g_arg + '"'
#print 'Writing results to ' + r4GroupedFile
#os.system(r4_g_arg)

## Run Pandaseq
ps_out_fq = prefix + '_contigs.fq'
ps_arg = 'pandaseq -f ' + r1GroupedFile + ' -r ' + r4GroupedFile + ' -F -w ' + ps_out_fq + ' -B' 
print '[STATUS] Executing argument "' + ps_arg + '"'
print 'Writing results to ' + ps_out_fq
os.system(ps_arg)

## Order the groups
groupName = re.sub('\..*', '', groupFile)
group_order_out = groupName + '_ordered.txt'
group_order_arg = 'group_order.pl -g ' + groupFile + ' -q ' + ps_out_fq + ' > ' + group_order_out
print '[STATUS] Executing argument "' + group_order_arg + '"'
print 'Writing results to ' + group_order_out
os.system(group_order_arg)

## Convert contigs file to FASTA
fa_convert_out = re.sub('\.fq*', '.fa', ps_out_fq)
fa_convert_arg = 'fa_assemble_from_group.pl ' + group_order_out + ' ' + ps_out_fq + ' > ' + fa_convert_out
print '[STATUS] Executing argument "' + fa_convert_arg + '"'
print 'Writing results to ' + fa_convert_out
os.system(fa_convert_arg)

## Remove bad sequences
final_seqs = prefix + 'seqs.fa'
clean_up_arg = '16S_cleanup.pl -f ' + fa_convert_out + ' -m ' + str(max_length) + ' > ' + final_seqs
print '[STATUS] Executing argument "' + clean_up_arg + '"'
print 'Writing results to ' + final_seqs
os.system(clean_up_arg)

print "\nDone"

	





