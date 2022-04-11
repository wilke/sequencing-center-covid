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
parser.add_argument('--mapping-file' , dest='mapping_file' , help="ID mapping file")
parser.add_argument('--source-dir' , dest='source')
parser.add_argument('--destination-dir' , dest='destination')
parser.add_argument('--sites2labels', dest='sites_file')
args = parser.parse_args()


def parse_mapping_file(mfile) -> dict :
    mapping= {}
    
    with open(mfile) as f :
        header_line = f.readline()
        tags = header_line.strip().split("\t")
        
        primary_column = 0
        date_column =  1
        exclude_columns = []
        include_columns = []
        
        mapping['header'] = []
        mapping['values'] = {}
        for idx, val in enumerate(tags):
            
            # if val =="Label" :
                # exclude_columns.append(idx)
            if val in ["wwtp_name" , "SiteId"] :
                include_columns.append(idx)
            if val == "sample_id" :
                primary_column = idx
            elif val in ["sample_collection_data" , "sample_collect_date"] :
                date_column = idx
            
            mapping['header'].append(val.strip().replace(" " , "_"))
                
        print("Primary column:\t" + str(primary_column))
        print("Date column:\t" + str(date_column))
        print("Excluding columns:\t" + ",".join(map(lambda x: str(x) , exclude_columns)))
        
        for l in f :
            values = l.strip().split("\t")
            if len(values) < len(mapping['header']):
                continue
            mapping['values'][values[primary_column]] = { 'date' : None ,
                                                         'columns' : []
                                                         }
            if not date_column is None :
                mapping['values'][values[primary_column]]['date'] = values[date_column]
                
            for i,v in enumerate(values) :
                    
                if i in exclude_columns :
                    pass
                elif i in include_columns :
                    mapping['values'][values[primary_column]]['columns'].append({ 
                                                            'header' : mapping['header'][i],
                                                            'group' : v.strip().replace(" " , "_")
                                                            })
    
    return mapping

def find_samples(pattern=None , categories= {} , src=None , dest="/local/incoming/covid/aggregates/location/", mapping=None) :
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
    
    for path in Path(src).rglob("*." + pattern + '*.out'):
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
        
# def dev:
#     print(mapping.id2site(Id))
#     print(mapping.site2labels( mapping.id2site(Id) ) )

mapping = Mapping()
destination = Path("/tmp")

if args.destination and os.path.isdir(args.destination):
    destination = Path(args.destination)

if os.path.isfile(args.mapping_file) :
    result = parse_mapping_file(args.mapping_file)
    mapping.load(args.mapping_file)
    
    if args.sites_file and os.path.isfile(args.sites_file):
        # load sites file
        mapping.load_site_mapping(args.sites_file)

    # get all outfiles     
    for src in mapping.get_files(args.source, suffix=".out"):
        basename = os.path.basename(src)
        
        Id = mapping.get_id(src)
        if Id:
            site = mapping.id2site(Id)
            if site:
                print(Id, len(mapping.site2labels(site)))
                for l in mapping.site2labels(site):
                    outdir = destination.joinpath(l['group'], l['label'],"out")
                    datadir = destination.joinpath(l['group'], l['label'],"data")
                    # check if dir exists
                    if not outdir.is_dir() :
                        Path.mkdir(outdir, exist_ok=True , parents=True)
                    if not datadir.is_dir() :
                        Path.mkdir(datadir, exist_ok=True , parents=True)
                    
                    target = datadir.joinpath(basename)
                    
                    print(Id, site, l['group'], src, target)
                    if not os.path.exists(target) :
                        os.link(src ,target)
                    else :
                        print("Target " + str(target) + " exists, skipping")  
                              
            else:
                print("No site for ID: " + Id)
        else:
            print("No ID for file: " + str(src))
       
    sys.exit()
      
        
    for k in result['values'] :
        find_samples(pattern=k , categories=result['values'][k] , src=args.source , dest=args.destination, mapping=mapping)
    # data2tab(result , metadata=m)
else :
    print("No such file " + args.mapping_file)