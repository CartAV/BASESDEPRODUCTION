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

inputs = ["es5_prod_radars"] #["es5_prod_accidents", "es5_prod_accidents_vehicules", "es5_prod_accidents_usagers", "es5_prod_pve", "es5_prod_radars"]
for input in inputs:
    ids = dataiku.Dataset(input)
    print 'Processing input {}'.format(input)
    input_schema = ids.read_schema()
    idf = ids.get_dataframe()
    export_folder = dataiku.Folder("v30qzlxb")
    export_path = export_folder.get_path()
    # of = os.path.join(export_path, input + '.json.gz')
    # idf.to_json(of, compression='gzip')
    of = os.path.join(export_path, input + '.json')    
    idf.to_json(of, orient='records', lines=True)
    size = idf.shape[0]
    print 'Wrote {} rows out of {} to {}'.format(c, size, of)
    osc = os.path.join(export_path, input + '_schema.json')
    with open(osc, 'w') as output_schema:
        json.dump(input_schema, output_schema)
    print 'Wrote schema to {}'.format(size, osc)
