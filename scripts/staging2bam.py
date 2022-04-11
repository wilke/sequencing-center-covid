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
from lib.mapping import Mapping


parser = argparse.ArgumentParser()
parser.add_argument('--mapping-file', '-m' , dest='mapping_file')
parser.add_argument('--source-dir', '-s' , dest='source')
parser.add_argument('--destination-dir', '-d' , dest='destination')
parser.add_argument('--legacy-sample-ids', '-l' , dest='legacy' , default=False)
parser.add_argument('--sites2labes', dest='sites_file')
args = parser.parse_args()


def find_samples(pattern=None , categories= {} , src=None , dest="/local/incoming/covid/aggregates/location/") :
    destination = None
    if not dest:
        destination=Path("/local/incoming/covid/aggregates/location/")
    else:
        destination=Path(dest)
    if not pattern :
        print("Missing pattern")
        sys.exit(0)
    else :
        print("Searching in " + src + " for " + pattern)
    
    date =re.compile("^(\d+)/(\d+)/(\d+)")
    res = date.match(categories['date'])
    
    if res is None :
        print("No date, skipping " + pattern)
        return
    

    prefix="".join([res[3],res[1] if int(res[1]) > 9 else  "0" + res[1], res[2] if int(res[2]) > 9 else "0" + res[2] ])
    print(res[0] , prefix )
    
    for path in Path(src).rglob(pattern + '*.out'):
        print(path.name , path.parts)    
        src = path.joinpath()
        
        for c in categories['columns'] :
           
            target_dir = destination.joinpath(c['header'] , c['group'])
            print(c['header'] , c['group'], pattern, target_dir) 
            
            if not target_dir.is_dir() :
                Path.mkdir(target_dir, exist_ok=True , parents=True)
            
           
            # get date right - easier to sort later
            
      
      
            
            
            
            target = os.path.join(target_dir , ".".join([prefix,path.name]))
            
            if not os.path.exists(target) :
                os.link(src ,target)
                pass
            else :
                print("Target " + target + " exists, skipping")
        

# main
mapping = Mapping()
suffix = ""
if args.legacy:
    mapping.legacy = True
    suffix=".sorted.bam"
    
print(args.destination)
if not args.destination or not os.path.isdir(args.destination):
    sys.exit("No destination directory " + str(args.destination))

if os.path.isfile(args.mapping_file) :
    mapping.load(args.mapping_file)

    for f in mapping.get_files(args.source):
        Id = mapping.get_id(f , suffix=suffix)
        if Id:
            date = mapping.id2date(Id)
            if date:
  
                fname = ".".join([date, os.path.basename(f)])
                
                dfname = os.path.join(args.destination, fname)
                print("Date: " + "\t".join([date,fname, dfname, str(f) ]))
                src = os.path.abspath(f)
                target = os.path.abspath(dfname)
                # print(src)
                if not os.path.isfile(target):
                    os.link( src, target )
                else:
                    print("File exists.")            
            else:
                print("No date for " + Id)
                   
        else:
            print("No ID for " + str(f) + ", skipping!")
            
    # print(mapping.get_files(args.source))
    sys.exit()
    for k in result['values'] :
        find_samples(pattern=k , categories=result['values'][k] , src=args.source , dest=args.destination)
    # data2tab(result , metadata=m)
else :
    print("No such file " + args.mapping_file)