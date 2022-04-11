#! /usr/bin/env python

# Author: Andreas Wilke
# Test

import argparse
import os
import readline
import re
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--spreadsheet-a', '-a', default=None, dest='a')
parser.add_argument('--spreadsheet-b', '-b', dest='b')
parser.add_argument('--key-in-a', '-ka', type=int, default=None, dest='ka')
parser.add_argument('--key-in-b', '-kb', type=int, default=None, dest='kb')
parser.add_argument('--add-column-from-a', '-c', nargs="+", default=[], dest='columns' )
parser.add_argument('--has-header', action='store_true', default=False, dest='header')
args = parser.parse_args()

a = []
# key a and b
ka = None
kb = None
key2row = {}
header=[]

if len(args.columns) :
    sys.stderr.write( "Adding columns: " + " ".join(args.columns) + "\n")

if not (args.a and os.path.isfile(args.a)) :
    sys.exit("Missing file for spreadsheet a")

if args.ka == None :
    sys.exit("Missing key column for a.")
else:
    ka = args.ka - 1
if args.kb == None :
    # sys.exit("Missing key column for b.")
    pass
else:
    kb = args.kb -1
    

with open(args.a) as fa :
    
    if args.header :
        header_line = fa.readline().strip().split("\t") 
        for idx in args.columns :
            header.append(header_line[int(idx) - 1]) 
            
    for l in fa :
        stripped = l.strip()
        columns = l.strip().split("\t")
        a.append(columns)
        key2row[columns[ka]] = []
        for idx in args.columns :
            key2row[columns[ka]].append(columns[int(idx) - 1])
        # print(key2row[columns[ka]])


with open(args.b) as fb :
    # print("Reading file b")
    if args.header :
        header_line = fb.readline().strip().split("\t") 
        h = header_line + header
        print("\t".join(h))

    for l in fb :
        stripped = l.strip()
        columns = l.strip().split("\t")
        if columns[kb] in key2row:
            row = columns + key2row[columns[kb]]
        else:
            sys.stderr.write("Key " + columns[kb] + " not in mapping.\n")
        print( "\t".join(row) )


