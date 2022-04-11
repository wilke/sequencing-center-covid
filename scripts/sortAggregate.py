#! /usr/bin/env python

# Author: Andreas Wilke

import argparse
from asyncio.proactor_events import _ProactorBaseWritePipeTransport
import os
import readline
import re
import sys


parser = argparse.ArgumentParser()
parser.add_argument("out_file")
args = parser.parse_args()

def parse(fileAndPath) -> dict :
    
    data = {}
    rows = [] 
    beta = []
    datePattern = re.compile("^(\d{2})(\d{2})(\d{2})")
    space = re.compile('^\s')

    # ldate= d[3] + d[1] +d[2] 
    
    with open(fileAndPath) as f :
        header_line = f.readline()
        tag = None
        for l in f :
            stripped = l.strip()

            if space.match(l)  :
                rows[-1] = rows[-1] + l
                beta[-1] += " " + stripped
            else:
                rows.append(l)        
                beta.append(l.strip())
    print(header_line)
    for row in beta :
    # for row in rows :
        columns = row.split("\t")           
        # print(len(columns) , columns[0])
        print(row.strip())
        
          
    



if os.path.isfile(args.out_file) :
    result = parse(args.out_file)
    # data2tab(result , metadata=m)
else :
    print("No such file " + args.out_file)