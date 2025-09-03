#! /usr/bin/env python

# Author: Andreas Wilke

import argparse
from asyncio.proactor_events import _ProactorBaseWritePipeTransport
import os
import readline
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mapping-file",
                    "--sample-metadata", dest="sample_metadata")
parser.add_argument("-o", "--output-file", dest="output_file")
parser.add_argument("-s", "--summary-dir", "--demix-dir", dest="demix_dir")
parser.add_argument("-d", "--depth-dir", dest="depth_dir")
parser.add_argument("-c", "--coverage-file", dest="coverage_file")

# parser.add_argument("out_file")
args = parser.parse_args()


def get_id(f) -> str:
    # i = re.match("^[^-_\.]+\.([^-_\.]+).+\.out", filename)
    i = re.match(r"^[^-_\.]+\.([^_\.]+).*", f)
    id = i[1] if i else None
    return id


def parse_demix(dir) -> dict:
    summary = {}
    if not os.path.isdir(dir):
        sys.exit("Not a directory: {dir}")

    for f in os.listdir(dir):
        fn = "/".join([dir, f])
        if not os.path.isfile(fn):
            sys.stderr.write("ERROR: Skipping " + f + ", not a file.\n")
            next
        else:
            id = get_id(f)
            if not id:
                sys.stderr.write(f"ERROR: No match for {f}\n")
                continue
            sys.stderr.write(
                f'INFO: Processing {f}, id is {id}, path is {fn}\n')
            summary[id] = _parse_demix_file(fn)
    return summary


def _parse_demix_file(file) -> dict:

    p = re.compile(r'^\s')
    t = re.compile(r'^(summarized|lineages|abundances|resid|coverage)\s+(.*)$')

    d = {
        'summarized': {},
        'lineages': [],
        'abundances': [],
        'resid': '',
        'coverage': ''
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
                # sum = re.findall('\(\'(\w+)\',\s*([\d\.]+)\)', stripped)
                sum = re.findall(r'\(\'([^\']+)\',\s*([\d\.]+)\)', stripped)

                for pair in sum:
                    d[tag][pair[0]] = pair[1]

            elif tag == "lineages":
                # lin = re.findall('([A-Z\.\d]+)', stripped)
                lin = re.findall(r'([\w\.\d]+)', stripped)
                d[tag] += lin
            elif tag == "abundances":
                abu = re.findall(r'([\d\.]+)', stripped)
                d[tag] += abu
            elif tag == "resid":
                d[tag] = stripped
            elif tag == 'coverage':
                d[tag] = stripped
            else:
                sys.stderr.write(f'Unknow tag {tag}, how did i get here?\n')
    return d


def parse_depth(dir) -> dict:
    pass


def parse_coverage(file) -> dict:

    coverage = {}
    with open(file) as f:
        for l in f:
            fields = l.split("\t")
            # print(get_id(fields[0]), fields)
            coverage[get_id(fields[0])] = fields[1]
    return coverage


def merge(mapping=None, coverage=None, summary=None):

    header_base = ["sample_id", "site_id", "sample_collect_date", "wwtp_name", "N1 (cp/µl)", "N1 (cp/micro_liter)"]
    header_coverage = ["coverage"]
    header_summary = ['summarized', 'lineages',
                      'abundances', 'resid', 'coverage']
    # 'summarized': {'Omicron': '0.9997349999914389'}, 'lineages': ['BA.1'], 'abundances': ['0.999735'], 'resid': '15.978256625525404'}
    if mapping and os.path.isfile(mapping):
        with open(mapping) as f:
            # add header
            header = f.readline().strip().split("\t")
            if coverage:
                header.append("coverage")

            if summary:
                header += header_summary

            print("\t".join(header))

            for l in f:
                fields = l.strip().split("\t")
                if coverage:
                    if fields[0] in coverage:
                        fields.append(coverage[fields[0]])
                    else:
                        fields.append(f"not found")
                        sys.stderr.write(
                            f"Error: can not find coverage for ID {fields[0]}\n")

                if summary:
                    if fields[0] in summary:
                        for h in header_summary:
                            fields.append(summary[fields[0]][h])
                    else:
                        for h in header_summary:
                            fields.append("N/A")
                print("\t".join(map(lambda x: str(x), fields)))

    else:
        sys.exit(f"No such file {mapping}")


# load summary and depth info
summary = {}
depth = {}
if args.demix_dir:
    summary = parse_demix(args.demix_dir)
    # print(summary)

if args.depth_dir:
    depth = parse_depth(args.depth_dir)

if args.coverage_file:
    coverage = parse_coverage(args.coverage_file)

# add variants and depth to mapping file
if args.sample_metadata:
    sys.stderr.write("Adding coverage and variants\n")
    merge(mapping=args.sample_metadata, coverage=coverage, summary=summary)
