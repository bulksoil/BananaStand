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
parser.add_option('--max_length', dest = "max_length", action = "store", type = "int", default = 320)
parser.add_option('--min_length', dest = "min_length", action = "store", type = "int", default = 100)
parser.add_option('--ps_overlap', dest = "ps_overlap", action = "store", type = "int", default = 5)

options, args = parser.parse_args()

## Define Files
read1 = options.read1
read2 = options.read2
read3 = options.read3
read4 = options.read4
mapFile = options.map
prefix = options.prefix
max_length = options.max_length
min_length = options.min_length
ps_overlap = options.ps_overlap

## Demultiplex
groupFile = prefix + "_groups.txt"
dm_arg = 'demultiplex.py -m ' + mapFile + ' -f ' + read1 + ' -r ' + read4 + ' --I1 ' + read2 + ' --I2 ' + read3 + ' -p ' + prefix
print '[STATUS] Executing argument "' + dm_arg + '"'
print "Writing results to " + groupFile
os.system(dm_arg)

## Grouping Read1
#r1_name = re.sub('\.f.*', '', read1)
r1GroupedFile = prefix + '_R1_grouped.fq'
#r1_g_arg = 'fq_group_extract.pl -g ' + groupFile + ' -q ' + read1 + ' > ' + r1GroupedFile
#print '[STATUS] Executing argument "' + r1_g_arg + '"'
#print 'Writing results to ' + r1GroupedFile
#os.system(r1_g_arg)

## Grouping Read4
#r4_name = re.sub('\.f.*', '', read4)
r4GroupedFile = prefix + '_R2_grouped.fq'
#r4_g_arg = 'fq_group_extract.pl -g ' + groupFile + ' -q ' + read4 + ' > ' + r4GroupedFile
#print '[STATUS] Executing argument "' + r4_g_arg + '"'
#print 'Writing results to ' + r4GroupedFile
#os.system(r4_g_arg)

## run Cutadapt
cutadapt_out_R1_fq = prefix + '_R1_cutadapt.fq'
cutadapt_out_R2_fq = prefix + '_R2_cutadapt.fq'
cutadapt_arg = ' cutadapt -a GCATCGATGAAGAACGCAGC -A TTACTTCCTCTAAATGACCAAG ' + r1GroupedFile + ' ' + r4GroupedFile + ' --overlap 10 -m 10 -q 10 -o ' + cutadapt_out_R1_fq + ' -p ' + cutadapt_out_R2_fq
print '[STATUS] Executing argument "' + cutadapt_arg + '"'
print 'Writing results to ' + cutadapt_out_R1_fq + " and " + cutadapt_out_R2_fq
os.system(cutadapt_arg)

## Run Pandaseq
ps_out_fq = prefix + '_contigs.fq'
ps_arg = 'pandaseq -f ' + cutadapt_out_R1_fq + ' -r ' + cutadapt_out_R2_fq + ' -F -o ' + str(ps_overlap) + ' -g pandaseq.log -w ' + ps_out_fq + ' -B' 
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

## Make ITSx folder
ITSx_folder_arg = 'mkdir ITSx_output'
print '[STATUS] Executing argument "' + ITSx_folder_arg + '"'
os.system(ITSx_folder_arg)

## Run ITSx
ITSx_out_fa = prefix + '.ITS1.fasta'
ITSx_arg = 'ITSx -i ' + fa_convert_out + ' -t E,F,G,T --preserve T --complement F --minlen 100 -o ./ITSx_output/' + prefix + ' -cpu 6'
print '[STATUS] Executing argument "' + ITSx_arg + '"'
print 'Writing results to ' + ITSx_out_fa
os.system(ITSx_arg)



## Remove bad sequences
clean_seqs = prefix + '.cleaned.seqs.fa'
clean_up_arg = 'perl /Users/Shared/SequenceProcessing/ITS_cleanup.pl -f ./ITSx_output/' + prefix + '.ITS1.fasta -m ' + str(max_length) + ' -n ' + str(min_length) + ' > ' + clean_seqs
print '[STATUS] Executing argument "' + clean_up_arg + '"'
print 'Writing results to ' + clean_seqs
os.system(clean_up_arg)

##check for chimeras
ident_chimeras_arg = 'identify_chimeric_seqs.py -i ' + clean_seqs + ' -m usearch61 -o ./usearch_checked_chimeras/ -r /Users/Shared/ReferenceData/UNITE_ver7/sh_refs_qiime_ver7_97_31.01.2016.Osativa.fasta'
print '[STATUS] Executing argument "' + ident_chimeras_arg + '"'
print 'Writing results to usearch_checked_chimeras'
os.system(ident_chimeras_arg)

##remove chimeras
filtered_seqs = prefix + '.final.seqs.fa'
filter_arg = 'filter_fasta.py -f ' + clean_seqs + ' -o ' + filtered_seqs + ' -s usearch_checked_chimeras/chimeras.txt -n'
print '[STATUS] Executing argument "' + filter_arg + '"'
print 'Writing results to ' + filtered_seqs
os.system(filter_arg)

	





