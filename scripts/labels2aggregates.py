#! /usr/bin/env python

# Author: Andreas Wilke
# Test

import argparse
from asyncio.proactor_events import _ProactorBaseWritePipeTransport
import os
import readline
import re
import sys
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument('--mapping-file' , dest='mapping_file')
parser.add_argument('--source-dir' , dest='source')
parser.add_argument('--destination-dir' , dest='destination')
args = parser.parse_args()


def parse_mapping_file(mfile) -> dict :
    mapping= {}
    
    with open(mfile) as f :
        header_line = f.readline()
        tags = header_line.strip().split("\t")
        
        primary_column = 0
        exclude_columns = []
        
        mapping['header'] = []
        mapping['values'] = {}
        for idx, val in enumerate(tags):
            
            if val =="Label" :
                exclude_columns.append(idx)
            elif val == "ID Pattern" :
                primary_column = idx
            
            mapping['header'].append(val.strip().replace(" " , "_").replace("/", "_").replace("(","_").replace(")", "_").replace("'","_").replace("`","_").replace("&","_").replace(",","_").replace('"','_'))
                
        print("Primary column:\t" + str(primary_column))
        print("Excluding columns:\t" + ",".join(map(lambda x: str(x) , exclude_columns)))
        
        for l in f :
            values = l.strip().split("\t")
            mapping['values'][values[primary_column]] = []
            for i,v in enumerate(values) :
                if i in exclude_columns :
                    pass
                else :
                    mapping['values'][values[primary_column]].append({ 
                                                            'header' : mapping['header'][i],
                                                            'group' : v.strip().replace(" " , "_").replace("/", "_").replace("(","_").replace(")", "_").replace("'","_").replace("`","_").replace("&","_").replace(",","_").replace('"','_')
                                                            })
    
    return mapping

def find_samples(pattern=None , categories=[] , src=None , dest="/local/incoming/covid/aggregates/location/") :
    destination = None
    if not dest:
        destination=Path("/local/incoming/covid/aggregates/location/")
    else:
        destination=Path(dest)
    if not pattern :
        print("Missing pattern")
        sys.exit(0)
    else :
        print("Searching for " + pattern + " in " + src)
    
    date =re.compile("^(\d{2})(\d{2})(\d{2})")
    for path in Path(src).rglob('*.[0-9][0-9][0-9][0-9][0-9][0-9][-_]' + pattern + '*.out'):
        # print(path.name , path.parts)    
        src = path.joinpath()
        print(path)
        for c in categories :
           
            data_dir = destination.joinpath(c['header'] , c['group'], "data")
            out_dir = destination.joinpath(c['header'] , c['group'],"out")
            print(c['header'] , c['group'], pattern, data_dir) 
            pass
            if not data_dir.is_dir() :
                Path.mkdir(data_dir, exist_ok=True , parents=True)
            if not out_dir.is_dir() :
                Path.mkdir(out_dir, exist_ok=True , parents=True)
           
            # get date right - easier to sort later
            res = date.match(path.name)
            prefix="".join([res[3],res[1],res[2]])
            # prefix="-".join([res[3],res[1],res[2]])
      
      
            
            
            
            target = os.path.join(data_dir , ".".join([prefix,path.name])) # no need for prefix anymore
            target = os.path.join(data_dir , path.name)
            
            if not os.path.exists(target) :
                print("\t".join(["Linking:", str(src) , str(target)]))
                os.link(src ,target)
            else :
                print("Target " + target + " exists, skipping")
        

if os.path.isfile(args.mapping_file) :
    result = parse_mapping_file(args.mapping_file)

    for k in result['values'] :
        find_samples(pattern=k , categories=result['values'][k] , src=args.source , dest=args.destination)
    # data2tab(result , metadata=m)
else :
    print("No such file " + args.mapping_file)