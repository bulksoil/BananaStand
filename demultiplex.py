#!/usr/bin/python

import sys
import optparse
import gzip
import os

def opt_get():
	parser = optparse.OptionParser()
	parser.add_option('-f', '--FORWARD', dest = "r1", action = "store")
	parser.add_option('-r', '--REVERSE', dest = "r2", action = "store")
	parser.add_option('-p', '--PREFIX', dest = "prefix", action = "store")
	parser.add_option('-m', '--MAP', dest = "map", action = "store")
	parser.add_option('--I1', dest = "index1", action = "store")
	parser.add_option('--I2', dest = "index2", action = "store")
	parser.add_option('-a', '--algorithm', dest = "pipeline", action = "store", default = "qiime")
	(options, args) = parser.parse_args()
	return(options)

## Get arguments from command line
options = opt_get()
map_file = options.map
prefix = options.prefix
index1_f = options.index1
index2_f = options.index2
read1_f = options.r1
read2_f = options.r2
pipeline = options.pipeline.lower()

## Check if pipeline is valid
if not pipeline in ["qiime", "dada2"]:
	sys.exit('[ERROR] Do not recognize pipeline ' + pipeline + "\n Valid options are dada2 and qiime.")

## Read in barcodes for samples from the mapping file
print "Scanning barcodes..."
sample_barcodes = {}
inp = open(map_file, 'r')
while True:
	line = inp.readline()
	if not line:
		break
	sampleID, barcode = line.rstrip("\n").split("\t")[:2]
	if barcode in sample_barcodes:
		sys.exit("[ERROR] Non unique barcodes in map file.")
	else:
		sample_barcodes[barcode] = sampleID

inp.close()
print "Found " + str(len(sample_barcodes)) + " barcodes."

## Read fq files
print "Demultiplexing..."
i1 = gzip.open(index1_f, 'rb')
i2 = gzip.open(index2_f, 'rb' )
r1 = gzip.open(read1_f, 'rb')
r2 = gzip.open(read2_f, 'rb')


found = 0
sample_counts = {}

def fq_read(file_inp):
	data = {}
	data['header'] = file_inp.readline().rstrip("\n")
	data['seq'] = file_inp.readline().rstrip("\n")
	data['space'] = file_inp.readline().rstrip("\n")
	data['qual'] = file_inp.readline().rstrip("\n")
	return(data)

def header_match(h1, h2, h3, h4):
	h1 = h1.split(" ")[0]
	h2 = h2.split(" ")[0]
	h3 = h3.split(" ")[0]
	h4 = h4.split(" ")[0]
	if all(x == h1 for x in (h2, h3, h4)):
		return(1)
	else:
		return(0)

def complement(s): 
    basecomplement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'N': 'N'} 
    letters = list(s) 
    letters = [basecomplement[base] for base in letters] 
    return(''.join(letters))

def revcom(s):
    return(complement(s[::-1]))

if options.pipeline == "qiime":

	
	## Prepare outfiles
	r1_g_name = prefix + "_R1_grouped.fq"
	r2_g_name = prefix + "_R2_grouped.fq"
	group_name = prefix + '_groups.txt'
	sc_name = prefix + '_sample_counts.txt'
	
	groups = open(group_name, 'wb')
	sc = open(sc_name, 'w')
	r1o = open(r1_g_name, 'wb')
	r2o = open(r2_g_name, 'wb')

	while True:
		i1_dat = fq_read(i1)
		i2_dat = fq_read(i2)
		r1_dat = fq_read(r1)
		r2_dat = fq_read(r2)

		if not i1_dat['header']:
			break

		if(header_match(i1_dat['header'], i2_dat['header'], r1_dat['header'], r2_dat['header']) == 0):
			sys.exit('[ERROR] Headers do not match.')

		#bc = i2_dat['seq'] + revcom(i1_dat['seq'])
		bc = i2_dat['seq'] + revcom(i1_dat['seq'])

		if bc in sample_barcodes:
			found += 1
			sample = sample_barcodes[bc]
			if found % 100 == 0:
				sys.stdout.write('%s\r' % found)
    			sys.stdout.flush()
		
			if sample in sample_counts:
				sample_counts[sample] += 1
			else:
				sample_counts[sample] = 1
		
			groups.write(i1_dat['header'].split(" ")[0] + "\t" + sample + "\n")
			r1o.write(r1_dat['header'] + "\n" + r1_dat['seq'] + "\n" + "+" + "\n" + r1_dat['qual'] + "\n")
			r2o.write(r2_dat['header'] + "\n" + r2_dat['seq'] + "\n" + "+" + "\n" + r2_dat['qual'] + "\n")

	i1.close()
	i2.close()
	r1.close()
	r2.close()
	r1o.close()
	r2o.close()
	groups.close()

else:

	group_name = prefix + '_groups.txt'
	sc_name = prefix + '_sample_counts.txt'
	
	groups = open(group_name, 'wb')
	sc = open(sc_name, 'w')

	if not os.path.exists("FWD"):
		os.makedirs("FWD")

	if not os.path.exists("RVS"):
		os.makedirs("RVS")

	fh = {}

	while True:

	
		i1_dat = fq_read(i1)
		i2_dat = fq_read(i2)
		r1_dat = fq_read(r1)
		r2_dat = fq_read(r2)

		if not i1_dat['header']:
			break

		if(header_match(i1_dat['header'], i2_dat['header'], r1_dat['header'], r2_dat['header']) == 0):
			sys.exit('[ERROR] Headers do not match.')

		bc = i2_dat['seq'] + revcom(i1_dat['seq'])

		if bc in sample_barcodes:
			found += 1
			sample = sample_barcodes[bc]

			out_name = sample + ".fastq"
			
			#if not sample in fh:
			#	fwd_file = open("FWD/" + out_name, 'w')
			#	rvs_file = open("RVS/" + out_name, 'w')
			#	fh[sample] = 1
			#else:
			#	fwd_file = open("FWD/" + out_name, 'a')
			#	rvs_file = open("RVS/" + out_name, 'a')

			if found % 100 == 0:
				sys.stdout.write('%s\r' % found)
    			sys.stdout.flush()
		
			if sample in sample_counts:
				sample_counts[sample] += 1
			else:
				sample_counts[sample] = 1
		
			groups.write(i1_dat['header'].split(" ")[0] + "\t" + sample + "\n")

			if sample in fh:
				with open("FWD/" + out_name, 'a') as fwd_file:
					fwd_file.write(r1_dat['header'] + "\n" + r1_dat['seq'] + "\n" + "+" + "\n" + r1_dat['qual'] + "\n")
				fwd_file.close()
				with open("RVS/" + out_name, 'a') as rvs_file:
					rvs_file.write(r2_dat['header'] + "\n" + r2_dat['seq'] + "\n" + "+" + "\n" + r2_dat['qual'] + "\n")
				rvs_file.close()
				
			else:
				
				fh[sample] = 1
				with open("FWD/" + out_name, 'w') as fwd_file:
					fwd_file.write(r1_dat['header'] + "\n" + r1_dat['seq'] + "\n" + "+" + "\n" + r1_dat['qual'] + "\n")
				fwd_file.close()
				with open("RVS/" + out_name, 'w') as rvs_file:
					rvs_file.write(r2_dat['header'] + "\n" + r2_dat['seq'] + "\n" + "+" + "\n" + r2_dat['qual'] + "\n")
				rvs_file.close()

			#fwd_file.write(r1_dat['header'] + "\n" + r1_dat['seq'] + "\n" + "+" + "\n" + r1_dat['qual'] + "\n")
			#rvs_file.write(r2_dat['header'] + "\n" + r2_dat['seq'] + "\n" + "+" + "\n" + r2_dat['qual'] + "\n")

			
			


for sample in sample_counts:
	sc.write(sample + "\t" + str(sample_counts[sample]) + "\n")
sc.close()

























