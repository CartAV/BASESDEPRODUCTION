# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
import os, re, time
import requests
import hashlib
import cStringIO
import gzip
import csv
import json
from multiprocessing import Process, Queue

inputs = ["es5_prod_accidents_copy", "es5_prod_pve_copy"]

for input in inputs:
    ids = dataiku.Dataset()
    input_schema = ids.read_schema()
    idf = ids.get_dataframe()
    export_folder = dataiku.Folder("szydloR5")
    export_path = export_folder.get_path()
    of = os.path.join(export_path, input + '.csv.gz')
    idf.to_csv(of, mode='a', index=False, sep=',', compression='gzip', encoding='utf8', header=True)
    size = idf.shape[0]
    print 'Wrote {} rows to {}'.format(size, of)
    osc = os.path.join(export_path, input + '.json')
    with open(osc, 'w') as output_schema:
        json.dump(input_schema, output_schema)
    print 'Wrote schema to {}'.format(size, osc)
