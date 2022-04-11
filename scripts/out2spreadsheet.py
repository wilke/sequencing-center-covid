#! /usr/bin/env python

# Author: Andreas Wilke

import argparse
from asyncio.proactor_events import _ProactorBaseWritePipeTransport
import os
import readline
import re
import sys
from lib.mapping import Mapping

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mapping-file", dest="mapping_file")
parser.add_argument("out_file")
args = parser.parse_args()


def parse(file) -> dict:

    p = re.compile('^\s')
    t = re.compile('^(summarized|lineages|abundances|resid)\s+(.*)$')

    d = {
        'summarized': {},
        'lineages': [],
        'abundances': [],
        'resid': ''
    }

    with open(file) as f:
        header_line = f.readline()
        tag = None
        for l in f:
            line = ''
            if t.match(l):
                m = t.match(l)
                tag = m[1]
                l = m[2]
                # print(m[0])
                # print(m[1])
                # print(m[2])

            stripped = l.strip()
            if tag == "summarized":
                sum = re.findall('\(\'(\w+)\',\s*([\d\.]+)\)', stripped)

                for pair in sum:
                    d[tag][pair[0]] = pair[1]

            if tag == "lineages":
                lin = re.findall('([A-Z\.\d]+)', stripped)
                d[tag] += lin
            if tag == "abundances":
                abu = re.findall('([\d\.]+)', stripped)
                d[tag] += abu
            if tag == "resid":
                d[tag] = stripped

    return d


def data2tab(data, metadata=None) -> None:

    header = False

    k = data.keys()

    # print header
    if header:
        if metadata:
            print("\t".join(['id', 'date', 'location']) + "\t" + "\t".join(k))
        else:
            print("\t".join(k))

    row = []
    for i in data:

        if isinstance(data[i], str):
            row += [data[i]]
        elif isinstance(data[i], list):
            row += [",".join(data[i])]
        elif isinstance(data[i], dict):
            tmp = []
            for k, v in data[i].items():
                tmp += [":".join([k, v])]

            row += [",".join(tmp)]
        else:
            print("Error: Unsupported type " + type(data[i], file=sys.stderr))
            sys.exit(0)

    if metadata:
        print(
            " : ".join([metadata['id'], metadata['date'], metadata['location']] + row))
    else:
        print("\t".join(row))
    return None


def file2meta(filepath, mapping=None) -> dict:
    m = {
        'id': '',
        'file': '',
        'date': '',
        'date-format': '',
        'location': '',
        'tags': [],
        'hierarchy': []
    }

    filename = os.path.basename(filepath)
    m['file'] = filename

    d = re.match("^(\d{2})(\d{2})(\d{2})", filename)
    i = re.match("^[^-_\.]+\.([^-_\.]+).+\.out", filename)
    # l = re.match("^\d+-(.+)_.*", filename)
    site = mapping.id2site(i[1])
    l = mapping.site2labels(site)

    print(i[1], mapping.id2site(i[1]), l, filename)

    if i:
        m['id'] = i[1]
    else:
        m['id'] = filename

    month = ''
    day = ''
    year = ''
    location = ''

    if d:
        month = d[2]
        day = d[3]
        year = d[1]

        m['date'] = year + month + day
        m['date-format'] = year + "-" + month + "-" + day

    else:
        m['date'] = ''

    if l:
        m['location'] = l[1]
    else:
        m['location'] = m['id']

    return m


mapping = Mapping()
if args.mapping_file and os.path.isfile(args.mapping_file):
    mapping.load(args.mapping_file)

if os.path.isfile(args.out_file):
    m = file2meta(args.out_file, mapping=mapping)
    result = parse(args.out_file)
    data2tab(result, metadata=m)
else:
    print("No such file " + args.out_file)

    #  if p.match(l) :
    #             d[tag] += " " + l.strip()
