#!/usr/bin/python

from sys import argv
from re import sub

file_input = open(argv[1],"r")
file_output = open(argv[2], 'w')

for line in file_input:
	
	temp = sub("ITS1_","",line)
	file_output.write(temp)

file_input.close()
file_output.close()
