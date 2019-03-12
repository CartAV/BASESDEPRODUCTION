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

es5_prod_accidents_copy = dataiku.Dataset("es5_prod_accidents_copy")
input_schema = ids.read_schema()
es5_prod_accidents_copy_df = es5_prod_accidents_copy.get_dataframe()
export_accidents = dataiku.Folder("szydloR5")
export_path = export_accidents.get_path()

of = os.path.join(export_path, 'prod_accidents_copy.csv.gz')
es5_prod_accidents_copy_df.to_csv(of, mode='a', index=False, sep=',', compression='gzip', encoding='utf8', header=True)
size = size + es5_prod_accidents_copy_df.shape[0]
print 'Wrote {} rows to {}'.format(size, of)
osc = os.path.join(path, 'prod_accidents_copy.json')
with open(osc, 'w') as output_schema:
    json.dump(input_schema, output_schema)
print 'Wrote schema to {}'.format(size, osc)
