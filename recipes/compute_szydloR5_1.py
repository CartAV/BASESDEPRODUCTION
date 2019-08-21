# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
import os, re, time
import requests
import hashlib
from cStringIO import StringIO
import gzip
import os
import csv
import json
import shutil
from multiprocessing import Process, Queue, Pool

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
CHUNK_SIZE = 20000         # size of each chunk
MAX_INPUT_ROWS = None      # number of lines to process in the recipe, None if no limit
NUM_THREADS = 1            # number of parallel threads
COMPRESS = True

def chunk_row_range(chunk_index):
    """Return the index of the first and (maximum) last row of the chunk with the given index, in a string"""
    return "%d-%d" % (chunk_index * CHUNK_SIZE + 1, (chunk_index + 1) * CHUNK_SIZE)


def process_chunk(arg):
    """Encrypt the given chunk in-place and return it (for use with Pool.imap_unordered)"""
    i, df = arg

    json_lines = ""

    try:
        json_lines = df.to_json(orient='records', lines=True)
        print("chunk {} processed".format(chunk_row_range(i)))
    except:
        logging.warning("chunk {} failed:".format(chunk_row_range(i)))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_obj, exc_tb)

    # Return i and df for writing to the output dataset
    return i, json_lines

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
datasets = {
    "radars": "RADARS.equipements_radar",
    "communes": "DATAPREPOPENDATAGEO.communes_boundaries_geojson",
    "acc_vehicules": "ACCIDENTS_BRUT.vehicules_pg",
    "acc_usagers": "ACCIDENTS_BRUT.usagers_postgis",
    "acc": "ACCIDENTS.accidents_CLUV_prepared",
    "pve": "cartav_pve_backup"
}
## test values
test = False
if test:
    datasets = { "pve" : "cartav_pve_backup"}
    MAX_INPUT_ROWS = 30000
    CHUNK_SIZE = 10000

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
for output, input in datasets.items():
    ids = dataiku.Dataset(input)
    print 'Processing input {}'.format(input)
    input_schema = ids.read_schema()
    ichunks = ids.iter_dataframes(chunksize = CHUNK_SIZE, infer_with_pandas=True, limit=MAX_INPUT_ROWS)
    # process data chunks in parallel then write them sequentially
    pool = Pool(processes = NUM_THREADS)
    ochunks = pool.imap_unordered(process_chunk, enumerate(ichunks), chunksize=1)
    export_folder = dataiku.Folder("v30qzlxb")

    export_path = export_folder.get_path()
    size = 0
    of = os.path.join(export_path, output + '.json')
    with open(of, "w") as ow:
        for i, json_lines in ochunks:
            print("chunk {} processed".format(chunk_row_range(i)))
            ow.write(json_lines)
            size += i * CHUNK_SIZE              
    pool.close()  # Cannot be replaced with `with` in Python 2
    if COMPRESS:
        os.system("gzip {}".format(of))
        os.system("md5sum {}.gz > {}.gz.md5".format(of))
    else:
        os.system("md5sum {} > {}.md5".format(of))
    print 'Wrote {} rows to {}'.format(size, of)
    osc = os.path.join(export_path, output + '_schema.json')
    with open(osc, 'w') as output_schema:
        json.dump(input_schema, output_schema)
    print 'Wrote schema to {}'.format(size, osc)