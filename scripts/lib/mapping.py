from pathlib import Path
import os
import sys
import json
import re
from typing import List
# from typing import Optional


class Mapping(object):

    def __init__(self):
        self.file = None
        self.data = None
        self.legacy = False
        self.mapping = {}
        self.sites = {}     # map sites to other locations
        self.ids = {}       # map ids to sites
        self.id_column = 0
        self.include_columns = []
        self.exclude_columns = []

    def get_id(self, path, suffix=""):
        # 112421-HR-IF-G-4.sorted.bam
        Id = None
        basename = os.path.basename(path)

        # date_regex = re.compile("^(\d{6})\.((\d+)([-_].+))" + suffix)
        date_regex = re.compile("^([^-_\.]{6})\.([^_\.]+).*")

        res = date_regex.match(basename)
        if res:
            basename = res[2]

        if self.legacy:
            regex = re.compile("^(\d{6}[-_].+[-_].+)" + suffix)
            res = regex.match(basename)
            if res:
                Id = res[1]
        else:
            regex = re.compile("^([^_\.]+).*" + suffix)
            res = regex.match(basename)
            # print(res[0] , res[1])
            if res:
                Id = res[1]

        return Id

    def _id_legacy2date(self, Id):
        # 011022-9-C-1_S92.sorted.bam

        regex = re.compile("^(\d{2})(\d{2})(\d{2})[_-].+")
        res = regex.match(Id)

        if res:
            return "".join([res[3], res[1], res[2]])
        else:
            return None

    def _id2date(self, Id) -> str:

        if Id in self.mapping['values']:
            d = self.mapping['values'][Id]['date']
            regex = re.compile("^(\d+)/(\d+)/(\d+)")
            res = regex.match(d)

            if res is None:
                print("No date from " + d + ", skipping ")
                return None
            else:
                return "".join([res[3], res[1] if int(res[1]) > 9 else "0" + res[1], res[2] if int(res[2]) > 9 else "0" + res[2]])

        else:
            print("ID " + Id + " not in mapping, skipping.")
            return None

    def id2date(self, Id):
        if self.legacy:
            return self._id_legacy2date(Id)
        else:
            return self._id2date(Id)

    def id2site(self, Id):
        if Id in self.ids:
            return self.ids[Id]['site']
        else:
            print("ID " + str(Id) + " not in sides")
        return None

    def site2labels(self, site):
        if site in self.sites:
            return self.sites[site]
        else:
            return None

    def get_files(self, dir, pattern="*", suffix=".bam") -> List:

        if dir and os.path.isdir(dir):
            pattern = str(pattern) + suffix
            return list(map(lambda x: x.joinpath(), Path(dir).rglob(pattern)))
        else:
            sys.exit("Not a directory: " + dir)

    def _get_legacy_prefix(self, path):
        pass

    def _get_prefix(path):
        prefix = None

        date = re.compile("^(\d+)/(\d+)/(\d+)")
        res = date.match(categories['date'])

        if res is None:
            print("No date, skipping " + pattern)
            return

        prefix = "".join([res[3], res[1] if int(
            res[1]) > 9 else "0" + res[1], res[2] if int(res[2]) > 9 else "0" + res[2]])

        return prefix

    def prefix(self, path):
        prefix = ''
        if self.legacy:
            self._get_legacy_prefix(path)
        else:
            self._get_prefix(path)
        return prefix

    def _load_legacy_mapping(self):
        pass

    def load_site_mapping(self, mapping_file):

        print("Sites file: " + mapping_file)
        site2labels = self.sites

        with open(mapping_file) as f:

            primary_column = 1
            header_line = f.readline()
            tags = header_line.strip().split("\t")

            if not (tags[0].lower() == "id_pattern" and tags[1].lower() == "siteid"):
                print(tags[0].lower(), tags[1].lower())
                sys.exit(
                    "Not a valid site mapping file, missing id_pattern and siteId")

            for idx, val in enumerate(tags):
                if val.lower() == "siteid":
                    primary_column = idx

            for line in f:
                values = line.strip().split("\t")

                if not values[primary_column] in site2labels:
                    site2labels[values[primary_column]] = []  # set([])

                for idx, val in enumerate(values):
                    text = val.strip().replace(" ", "_").replace("/", "_").replace("(", "_").replace(")",
                                                                                                     "_").replace("'", "_").replace("`", "_").replace("&", "_").replace(",", "_").replace('"', '_')
                    group = tags[idx].strip().replace(" ", "_").replace("/", "_").replace("(", "_").replace(
                        ")", "_").replace("'", "_").replace("`", "_").replace("&", "_").replace(",", "_").replace('"', '_')
                    site2labels[values[primary_column]].append(
                        {
                            'group': group,
                            'label': text
                        })

    def _load_id_mapping(self):

        ids2sites2dates = {}
        sites2labels = self.sites
        mapping = {}

        with open(self.file, encoding='utf-8' , errors='replace') as f:
            header_line = f.readline()
            tags = header_line.strip().split("\t")

            primary_column = 0
            site_column = 5
            date_column = 1
            exclude_columns = []
            include_columns = []

            mapping['header'] = []
            mapping['values'] = {}
            for idx, val in enumerate(tags):
                # sample_id       sample_collect_date     wwtp_name       site_id
                value = val.lower()
                # if val =="Label" :
                # exclude_columns.append(idx)
                if value in ["wwtp_name", "siteid", "site_id"]:
                    include_columns.append(idx)
                if value in ["site_id", "siteid"]:
                    site_column = idx
                    print("Found siteid column: " + str(idx))
                if value == "sample_id" or value == "sample id":
                    primary_column = idx
                elif val == "sample_collect_date" or val == "date":
                    date_column = idx

                mapping['header'].append(val.strip().replace(" ", "_").replace("/", "_").replace("(", "_").replace(
                    ")", "_").replace("'", "_").replace("`", "_").replace("&", "_").replace(",", "_").replace('"', '_'))

            print("Primary column:\t" + str(primary_column))
            print("Excluding columns:\t" +
                  ",".join(map(lambda x: str(x), exclude_columns)))

            for l in f:
                values = l.strip().split("\t")
                # ignore rows
                if len(values) < len(mapping['header']):
                    continue
                # print(values)
                Id = values[primary_column]
                site = values[site_column]

                mapping['values'][Id] = {
                    'date': None,
                    'columns': []
                }

                ids2sites2dates[Id] = {
                    'date': values[date_column],
                    'site': values[site_column],
                    'labels': []
                }

                if not site in sites2labels:
                    sites2labels[site] = []  # set([])

                if not date_column is None:
                    mapping['values'][Id]['date'] = values[date_column]

                for i, v in enumerate(values):
                    text = v.strip().replace(" ", "_").replace("/", "_").replace("(", "_").replace(")", "_").replace("\\",
                                                                                                                     "_").replace("'", "_").replace("`", "_").replace("&", "_").replace(",", "_").replace('"', '_')
                    if i in exclude_columns:
                        pass
                    elif i in include_columns:
                        mapping['values'][Id]['columns'].append({
                                                                'header': mapping['header'][i],
                                                                'group': text
                                                                })

                        ids2sites2dates[Id]['labels'].append(text)
                        sites2labels[site].append(
                            {'group': mapping['header'][i], 'label': text})

        self.mapping = mapping
        self.ids = ids2sites2dates
        self.sites = sites2labels

    def load(self, file):
        if not os.path.isfile(file):
            sys.exit("No file " + file)
        else:
            self.file = file

        if self.legacy:
            self._load_legacy_mapping()
        else:
            self._load_id_mapping()
