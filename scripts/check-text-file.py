#! /usr/bin/env python

# Author: Andreas Wilke

import argparse
import os
import readline
import re
import sys
from pathlib import Path
from lib.mapping import Mapping


parser = argparse.ArgumentParser()
parser.add_argument('--file', '-f' , dest='file')
args = parser.parse_args()


original_file=args.file

with open(original_file,  errors="ignore") as f:
	
	#for l in f :
	#	print(l)
	for l in f:
		print(l)
		try:	
			l.encode('ascii')
		except UnicodeEncodeError:
			print("Not Unicode")
			print(l)
		else:
	  		print("Line: ok\t" +  l)	

f.close()


with open(original_file, encoding='utf-8' , errors='replace') as f:

            header_line = f.readline()


