# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# -*- coding: utf-8 -*-
# NOTE: parallel send in swift can be faster up to ten times
# a more chunked version of pve dataset should be realized for speeding up operations
# a monthly chunked could be a nice split
# md5 should be performed too as in ICER and histovec
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
import requests
import os
from multiprocessing import Process, Queue, Pool, current_process
from time import sleep

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
import urllib3
#urllib3.disable_warnings()

CLEAR=True
folder_id = "v30qzlxb"
export_folder = dataiku.Folder(folder_id)
export_folder_info = export_folder.get_info()
export_path = export_folder.get_path()

inputs = ["acc", "acc_vehicules", "acc_usagers",
          "pve",
          "communes", "radars"
         ]
files = [i + ".json.gz" for i in inputs] + [i + "_schema.json" for i in inputs] + [i + "json.gz.md5" for i in inputs]

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# OpenStack
openstack_auth_url = "https://identity.api.pi.dsic.minint.fr/v3/auth/tokens"
openstack_domain = "tech"
swift_url = "https://object-store.api.pi.dsic.minint.fr/v1"
swift_auth = "AUTH_373b0504876743f09427f84e4fd8fe9d"
swift_container = "cartav-dev"
project_name="cartavdev-dev-f047-z1"
openstack_user = "dupontla"
openstack_pass = "*ahk4Xee8!"
swift_threads = 10
swift_path = '{}/{}/{}'.format(swift_url, swift_auth, swift_container)
maxtries = 3
data = { "auth": {
    "scope": {
      "project": {
        "name": project_name,
        "domain": { "name": openstack_domain }
      }
    },
    "identity": { "methods": ["password"], "password": { "user": { "name": openstack_user, "domain": { "name": openstack_domain }, "password": openstack_pass } } } } }
try:
    r = requests.post(openstack_auth_url, verify=False, json=data)
    print 'Auth response content: {}'.format(r.content)
    print 'Auth response headers: {}'.format(r.headers)
    token = r.headers['X-Subject-Token']
    print "OpenStack auth successful: token={}".format(token)
except Exception as e:
    print "OpenStack auth failed :{}".format(e)
    exit

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# List Swift files
headers = { 'X-Auth-Token': token}
try:
    r = requests.get(swift_path, verify=False, headers=headers)
    if (r.status_code != 200 | r.status_code != 204):
        print "Error {} while listing content: {}".format(r.status_code, r.content)
    else:
        remote_files=[f for f in r.content.split('\n') if 'json' in f]
        if len(files) > 0:
            print "Swift container {} successfully listed : \n{}".format(swift_container, remote_files)
        else:
            print "Swift container {} successfully listed : \nno json file found"

except:
    print "Swift request failed"

if CLEAR and len(remote_files)>0:
    data = "\n".join(swift_container + '/' + f for f in remote_files)
    headers = { 'X-Auth-Token': token, 'Content-Type': 'text/plain' }
    r = requests.post(swift_path + "?bulk-delete", data=data, verify=False, headers=headers)
    if r.status_code == 200:
        # There may be errors. We don't handle them; we only print this:
        print r.content
    else:
        print "ERROR {} performing bulk delete: {}".format(r.status_code, r.content)

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def swift_send_file(src, dst, process_queue):
    tries = 1
    failed = True
    while ((failed == True) & (tries <= maxtries)):
        try:
            url = '{}/{}'.format(swift_path, dst)
            print 'Swift sending {} to {}'.format(src, url)
            with open(src, 'rb') as f:
                r = requests.put(url, data=f, verify=False, headers=headers)
            status_code = r.status_code
        except requests.exceptions.ReadTimeout:
            status_code = "timeout"
        print 'Status code: {}'.format(status_code)
        if status_code == 201:
            failed=False
        else:
            tries += 1
            if tries <= maxtries:
                sleep(3 ** (tries-1))
    process_queue.get(i)

process_queue = Queue(swift_threads)
for i, file in enumerate(files):
    print file
    try:
        input = os.path.join(export_path, [x.replace('/','', 1) for x in export_folder.list_paths_in_partition() if file in x][0])
        print 'Input file: {}'.format(input)
    except:
        print '{} not found'.format(file)
    try:
        process_queue.put(i)
        thread = Process(target=swift_send_file, args=[input, file, process_queue])
        thread.start()
    except:
        print 'Failed while swifting {}'.format(input)
        
      
# final listing of swift dir for log check
try:
    r = requests.get(swift_path, verify=False, headers=headers)
    if (r.status_code != 200 | r.status_code != 204):
        print "Error {} while listing content: {}".format(r.status_code, r.content)
    else:
        remote_files=[f for f in r.content.split('\n') if 'json' in f]
        if len(files) > 0:
            print "Swift container {} successfully listed : \n{}".format(swift_container, remote_files)
        else:
            print "Swift container {} successfully listed : \nno json file found"

except:
    print "Swift request failed"        
        