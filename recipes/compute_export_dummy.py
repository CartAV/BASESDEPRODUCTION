# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
import requests
import os
from multiprocessing import Process, Queue, Pool, current_process

date_update = dataiku.get_custom_variables()["date_update"]

# Read recipe inputs
export_folder = dataiku.Folder("szydloR5")
export_folder_info = export_accidents.get_info()

inputs = ["es5_prod_accidents_copy", "es5_prod_pve_copy"]
files = [i + ".json" for i in inputs] + [i + ".csv.gz" for i in inputs] 

# paramètres openstack
openstack_auth_url = "https://identity.api.pi.dsic.minint.fr/v3/auth/tokens"
openstack_domain = "tech"
swift_url = "https://object-store.api.pi.dsic.minint.fr/v1"
swift_auth = "AUTH_373b0504876743f09427f84e4fd8fe9d"
swift_container = "cartav-dev"
openstack_user = "dupontla"
openstack_pass = "ahk4Xee8"
swift_threads = 10
swift_path = '{}/{}/{}/'.format(swift_url, swift_auth, swift_container)
maxtries = 3

# authent openstack
data = { "auth": { "identity": { "methods": ["password"], "password": { "user": { "name": openstack_user, "domain": { "name": openstack_domain }, "password": openstack_pass } } } } }
try:
    r = requests.post(openstack_auth_url, verify=False, json=data)
    token = r.headers['X-Subject-Token']
    print "OpenStack auth successful"
except:
    print "OpenStack auth failed :{}".format(r.content)
    exit

# get list of files in openstack
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
            url = '{}/{}/{}'.format(swift_path, date_update, dst)
            print 'sending {} to {}'.format(src, url)
            with open(src) as f:
                r = requests.put(url, data=f, verify=False, headers=headers)
            status_code = r.status_code
        except r.exceptions.ReadTimeout:
            status_code = "timeout"
        if status_code == 201:
            failed=False
        else:
            tries += 1
            if (tries <= maxtries):
                time.sleep(3 ** (tries-1))
    process_queue.get(i)

process_queue = Queue(swift_threads)
for i, file in enumerate(files):
    handle = dataiku.Folder(file[0])
    path = handle.get_path()
    try:
        print file[1]
        input = os.path.join(path, [ x.replace('/','', 1) for x in handle.list_paths_in_partition() if file[1] in x][0])
    except:
        print '{} not found in {}'.format(file[1], file[0])
    try:
        process_queue.put(i)
        thread = Process(target=swift_send_file, args=[input, file[1], process_queue])
        thread.start()
    except:
        print 'Failed while swifting {}'.format(input)
