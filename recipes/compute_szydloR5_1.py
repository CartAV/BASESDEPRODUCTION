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
from multiprocessing import Process, Queue, Pool

CHUNK_SIZE = 10000         # size of each chunk
MAX_INPUT_ROWS = None      # number of lines to process in the recipe, None if no limit
NUM_THREADS = 4            # number of parallel threads


def chunk_row_range(chunk_index):
    """Return the index of the first and (maximum) last row of the chunk with the given index, in a string"""
    return "%d-%d" % (chunk_index * CHUNK_SIZE + 1, (chunk_index + 1) * CHUNK_SIZE)

def process_chunk(arg):
    """Encrypt the given chunk in-place and return it (for use with Pool.imap_unordered)"""
    i, df = arg
    
    json_lines = ""

    try:
        json_lines = df.to_json(orient='records', lines=True)
        print("chunk {} process".format(chunk_row_range(i)))
    except:
        logging.warning("chunk {} failed:".format(chunk_row_range(i)))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_obj, exc_tb)

    # Return i and df for writing to the output dataset
    return i, json_lines

inputs = ["es5_prod_accidents", "es5_prod_accidents_vehicules", "es5_prod_accidents_usagers", "cartav_pve_backup", "es5_prod_radars"]
for input in inputs:
    ids = dataiku.Dataset(input)
    print 'Processing input {}'.format(input)
    input_schema = ids.read_schema()
    idf = ids.get_dataframe()
    ichunks = input_ds.iter_dataframes(chunksize=CHUNK_SIZE, infer_with_pandas=False, limit=MAX_INPUT_ROWS)
    # process data chunks in parallel then write them sequentially
    pool = Pool(processes=NUM_THREADS)
    ochunks = pool.imap_unordered(process_chunk, enumerate(ichunks), chunksize=1)
    pool.close()  # Cannot be replaced with `with` in Python 2
    export_folder = dataiku.Folder("v30qzlxb")
    export_path = export_folder.get_path()
    of = os.path.join(export_path, input + '.json')
    size = 0
    with open(of, "w") as ow:
        for i, json_lines in ochunks:
            ow.write(json_lines)
            size += i * CHUNK_SIZE
    print 'Wrote {} rows to {}'.format(size, of)
    osc = os.path.join(export_path, input + '_schema.json')
    with open(osc, 'w') as output_schema:
        json.dump(input_schema, output_schema)
    print 'Wrote schema to {}'.format(size, osc)
