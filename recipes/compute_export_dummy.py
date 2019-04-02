# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
import requests
import os
from multiprocessing import Process, Queue, Pool, current_process
from time import sleep

import urllib3
#urllib3.disable_warnings()

folder_id = "v30qzlxb"
export_folder = dataiku.Folder(folder_id)
export_folder_info = export_folder.get_info()
export_path = export_folder.get_path()

inputs = ["es5_prod_accidents", "es5_prod_accidents_vehicules", "es5_prod_accidents_usagers", 
          "es5_prod_pve", 
          "es5_prod_radars"
         ]
files = [i + ".json" for i in inputs] + [i + "_schema.json" for i in inputs] 

# OpenStack
openstack_auth_url = "https://identity.api.pi.dsic.minint.fr/v3/auth/tokens"
openstack_domain = "tech"
swift_url = "https://object-store.api.pi.dsic.minint.fr/v1"
swift_auth = "AUTH_373b0504876743f09427f84e4fd8fe9d"
swift_container = "cartav-dev"
openstack_user = "dupontla"
openstack_pass = "*ahk4Xee8!"
swift_threads = 10
swift_path = '{}/{}/{}'.format(swift_url, swift_auth, swift_container)
maxtries = 3
data = { "auth": { "identity": { "methods": ["password"], "password": { "user": { "name": openstack_user, "domain": { "name": openstack_domain }, "password": openstack_pass } } } } }
try:
    r = requests.post(openstack_auth_url, verify=False, json=data)
    print 'Auth response content: {}'.format(r.content)
    print 'Auth response headers: {}'.format(r.headers)
    token = r.headers['X-Subject-Token']
    print "OpenStack auth successful: token={}".format(token)
except Exception as e:
    print "OpenStack auth failed :{}".format(e)
    exit

# List Swift files
headers = { 'X-Auth-Token': token}
try:
    r = requests.get(swift_path, verify=False, headers=headers)
    if (r.status_code != 200 | r.status_code != 204):
        print "Error {} while listing content: {}".format(r.status_code, r.content)
    else:
        print "Swift container {} successfully listed : \n{}".format(swift_container, r.content)
except:
    print "Swift request failed"

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
